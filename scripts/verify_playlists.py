#!/usr/bin/env python3
"""Verify that every stream in the M3U playlists is actually alive.

A URL is considered working when:

1. it returns an HLS playlist (``#EXTM3U``);
2. a master playlist resolves to a media playlist;
3. the last segment of the media playlist downloads;
4. that segment is real media (not HTML/JSON) and is not suspiciously small.

Only the Python standard library is required.

Usage:
    python3 scripts/verify_playlists.py
    python3 scripts/verify_playlists.py --list retro-sereno
    python3 scripts/verify_playlists.py --json > report.json
    python3 scripts/verify_playlists.py --timeout 40 --min-bytes 30000

Exit codes:
    0  every stream passed
    1  at least one stream failed
    2  no streams were found
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_UA = (
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36"
)
PLAYLIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lists")

# Many public IPTV endpoints use self-signed or expired certificates.
# Verification is disabled on purpose; this script only checks availability.
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def fetch(url: str, limit: int, timeout: float, ua: str, referer: str | None = None):
    """Fetch at most ``limit`` bytes and return (final_url, status, body)."""
    headers = {"User-Agent": ua, "Accept": "*/*"}
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout, context=SSL_CONTEXT) as response:
        return response.geturl(), response.status, response.read(limit)


def parse_playlist(path: str) -> list[tuple[str, str]]:
    """Return [(channel_name, url), ...] from an M3U file."""
    entries: list[tuple[str, str]] = []
    pending_name: str | None = None
    with open(path, encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#EXTINF"):
                pending_name = line.split(",", 1)[1].strip() if "," in line else "unknown"
            elif not line.startswith("#") and pending_name is not None:
                entries.append((pending_name, line))
                pending_name = None
    return entries


def pick_variant(master_url: str, text: str) -> str:
    """Pick the highest-bandwidth variant from a master playlist."""
    lines = text.splitlines()
    best_bandwidth = -1
    best_uri: str | None = None
    for index, line in enumerate(lines):
        if not line.startswith("#EXT-X-STREAM-INF"):
            continue
        match = re.search(r"BANDWIDTH=(\d+)", line)
        bandwidth = int(match.group(1)) if match else 0
        for candidate in lines[index + 1 :]:
            candidate = candidate.strip()
            if candidate and not candidate.startswith("#"):
                if bandwidth > best_bandwidth:
                    best_bandwidth = bandwidth
                    best_uri = candidate
                break
    if best_uri is None:
        raise ValueError("master playlist without variants")
    return urllib.parse.urljoin(master_url, best_uri)


def resolve_segment(url: str, timeout: float, ua: str, referer: str | None, depth: int = 0) -> str:
    """Resolve a playback URL to the last segment of its media playlist."""
    final_url, _status, body = fetch(url, limit=2_000_000, timeout=timeout, ua=ua, referer=referer)
    text = body.decode("utf-8", "ignore")

    if "#EXTM3U" not in text[:2000]:
        raise ValueError("response is not an HLS playlist")

    if "#EXT-X-STREAM-INF" in text:
        if depth >= 2:
            raise ValueError("too many nested master playlists")
        variant = pick_variant(final_url, text)
        return resolve_segment(variant, timeout, ua, referer, depth + 1)

    segments = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if not segments:
        raise ValueError("media playlist without segments")
    return urllib.parse.urljoin(final_url, segments[-1])


def check_stream(
    playlist: str,
    channel: str,
    url: str,
    timeout: float,
    min_bytes: int,
    ua: str,
    referer: str | None,
) -> dict:
    """Check one stream and return a result dictionary."""
    result = {
        "playlist": playlist,
        "channel": channel,
        "url": url,
        "status": "FAIL",
        "http": None,
        "bytes": 0,
        "segment": None,
        "detail": "",
    }
    try:
        segment = resolve_segment(url, timeout, ua, referer)
        result["segment"] = segment
        _final_url, status, data = fetch(
            segment, limit=400_000, timeout=timeout, ua=ua, referer=referer
        )
        result["http"] = status
        result["bytes"] = len(data)

        stripped = data[:200].lstrip()
        if stripped.startswith(b"<") or stripped.startswith(b"{"):
            result["detail"] = "segment is HTML/JSON, not media"
        elif len(data) < min_bytes:
            result["detail"] = f"segment too small ({len(data)} bytes)"
        else:
            result["status"] = "OK"
            result["detail"] = "media segment received"
    except urllib.error.HTTPError as error:
        result["http"] = error.code
        result["detail"] = f"HTTP {error.code}"
    except urllib.error.URLError as error:
        result["detail"] = f"network error: {error.reason}"
    except Exception as error:  # noqa: BLE001 - report anything unexpected per channel
        result["detail"] = f"{type(error).__name__}: {error}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", dest="only", help="only check this playlist stem (e.g. retro-sereno)")
    parser.add_argument("--json", action="store_true", help="print a JSON report instead of a table")
    parser.add_argument("--timeout", type=float, default=25.0, help="per-request timeout in seconds")
    parser.add_argument("--min-bytes", type=int, default=20_000, help="minimum segment size")
    parser.add_argument("--jobs", type=int, default=8, help="parallel checks")
    parser.add_argument("--user-agent", default=DEFAULT_UA, help="User-Agent header")
    parser.add_argument("--referer", default=None, help="Referer header for every request")
    args = parser.parse_args()

    if not os.path.isdir(PLAYLIST_DIR):
        print(f"error: playlist directory not found: {PLAYLIST_DIR}", file=sys.stderr)
        return 2

    targets = []
    for filename in sorted(os.listdir(PLAYLIST_DIR)):
        if not filename.endswith(".m3u"):
            continue
        stem = filename[:-4]
        if args.only and stem != args.only:
            continue
        for channel, url in parse_playlist(os.path.join(PLAYLIST_DIR, filename)):
            targets.append((stem, channel, url))

    if not targets:
        print("error: no streams found", file=sys.stderr)
        return 2

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = [
            pool.submit(
                check_stream,
                playlist,
                channel,
                url,
                args.timeout,
                args.min_bytes,
                args.user_agent,
                args.referer,
            )
            for playlist, channel, url in targets
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    order = {name: index for index, (name, _channel, _url) in enumerate(targets)}
    results.sort(key=lambda item: order.get((item["playlist"], item["channel"], item["url"]), 999))

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        header = f"{'PLAYLIST':<18} {'CHANNEL':<28} {'RESULT':<7} {'HTTP':<5} {'BYTES':>8}  DETAIL"
        print(header)
        print("-" * len(header))
        for item in results:
            print(
                f"{item['playlist']:<18} {item['channel'][:28]:<28} "
                f"{item['status']:<7} {str(item['http'] or '-'):<5} "
                f"{item['bytes']:>8}  {item['detail']}"
            )

    failures = [item for item in results if item["status"] != "OK"]
    print()
    print(f"{len(results) - len(failures)} ok, {len(failures)} failed, {len(results)} total")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
