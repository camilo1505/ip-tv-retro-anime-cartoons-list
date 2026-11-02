# Verifying streams

Every URL in `lists/` is a live HTTP stream. A channel can disappear, change URL or start
returning an error page without any change in this repository. Verify before and after
editing a playlist.

## Why HTTP 200 is not enough

Public IPTV endpoints commonly return:

- **200 with an HTML page** (parking page, provider error, Cloudflare challenge);
- **200 with an empty body**;
- **200 with a very short segment** that players cannot decode;
- **302 to another dead URL**.

The only reliable check is to resolve the HLS chain down to a media segment and download
part of it.

## Quick start

```bash
python3 scripts/verify_playlists.py
```

Only one playlist:

```bash
python3 scripts/verify_playlists.py --list retro-sereno
```

Machine-readable report:

```bash
python3 scripts/verify_playlists.py --json > /tmp/iptv-report.json
```

Slow or strict sources:

```bash
python3 scripts/verify_playlists.py --timeout 40 --min-bytes 30000 --jobs 4
```

Streams that require a specific origin:

```bash
python3 scripts/verify_playlists.py --referer "https://example.com/"
```

Exit code is `0` when every stream passes, `1` when at least one fails and `2` when no
streams were found.

## What the script does

For each URL:

1. Fetches the URL and checks for `#EXTM3U`.
2. If it is a **master playlist** (`#EXT-X-STREAM-INF`), picks the highest-bandwidth
   variant and resolves it. Up to two nesting levels are supported.
3. If it is a **media playlist**, takes the last non-comment line (the most recent
   segment) and resolves it against the playlist URL.
4. Downloads up to 400 KB of that segment.
5. Marks the channel `OK` only when the payload looks like media and is at least
   `--min-bytes` (20 KB by default).

The script disables TLS certificate verification because many public IPTV endpoints use
self-signed or expired certificates. It only checks availability, never content.

## Reading the output

```text
PLAYLIST           CHANNEL                      RESULT  HTTP     BYTES  DETAIL
--------------------------------------------------------------------------------
retro-sereno       Dragon Ball                  OK      200    419428  media segment received
retro-sereno       EnerGeek                     FAIL    403         0  HTTP 403

14 ok, 1 failed, 15 total
```

- `HTTP 403` on both EnerGeek channels usually means the SerenoTV token expired.
- `HTTP 404` usually means the restream moved or was removed.
- `segment too small` often means the upstream is serving a placeholder.
- `not an HLS playlist` means the URL now returns HTML or JSON.
- `network error` can be DNS, timeout or the host being offline.

## Manual fallback

When the script cannot resolve a stream, inspect it by hand:

```bash
curl -sSL --max-time 25 "URL" | head -20
```

- If the output is HTML, the stream is gone.
- If it is a master playlist, copy a variant URL and request it again.
- If it is a media playlist, take the last segment URL and download a few hundred KB:

```bash
curl -sSL --max-time 25 -o /tmp/segment.ts "SEGMENT_URL"
ls -lh /tmp/segment.ts
```

A valid TS segment is usually several hundred kilobytes. To confirm it decodes:

```bash
ffprobe -v error -show_entries format=duration,size -of default=nw=1 /tmp/segment.ts
```

`ffprobe` is optional; the Python checker does not require ffmpeg.

## When to run it

- After adding, replacing or removing a channel.
- Before a release or a large cleanup.
- Periodically (for example monthly) to refresh `docs/sources.md`.
- When the TV reports a channel as unavailable.

Individual streams can fail temporarily because of upstream restarts or rate limits. Retry
a failure once before declaring the channel dead.

## Updating the documentation

After a verification round:

1. Update the **Last full verification** date at the top of `docs/sources.md`.
2. Change the `Status` of any channel that failed or recovered.
3. If a URL changed, update both the playlist and `docs/sources.md`.
4. If a channel was removed, update the count in `README.md` and the playlist header.

## Limitations

- The script checks the stream from the machine that runs it. **Geoblocked** channels may
  work in another country.
- It does not validate DRM, subtitles or audio tracks.
- It does not prove that the content matches the channel name.
- High concurrency can trigger rate limits on some hosts. Lower `--jobs` if failures look
  suspicious.
- A passing check means "there is media right now", not "this URL will work tomorrow".
