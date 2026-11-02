# Troubleshooting

Symptom → likely cause → what to do.

## The TV shows 0 channels after adding a source

1. Open the raw URL in a browser or with `curl`. It must return plain text starting with
   `#EXTM3U`.
2. If it returns `404`, check:
   - the repository is still **public**;
   - the branch is `main`;
   - the filename matches exactly (`lists/retro-sereno.m3u`, not `retro-sereno.m3u`);
   - there is no typo in the account or repository name.
3. If it returns HTML, the URL points to a GitHub page instead of the raw file.
4. If the raw file is correct, run `scripts/verify_playlists.py --list <name>` to see
   whether the playlist content itself is valid.

## The channel count did not change after a push

- OwnTV refreshes every 12 hours. Force a **Resync → Resync now**.
- If the count is still old, the source may be pointing to a different file or branch.
- A playlist with parse errors is silently ignored. Validate it:

```bash
python3 - <<'PY'
import re
text = open("lists/retro-sereno.m3u", encoding="utf-8").read()
extinf = re.findall(r"#EXTINF[^\n]*", text)
urls = [l for l in text.splitlines() if l and not l.startswith("#")]
print(len(extinf), "channels,", len(urls), "urls")
PY
```

Both numbers must match.

## One channel is black, frozen or returns an error

1. Verify the stream:

```bash
python3 scripts/verify_playlists.py --list retro-sereno
```

2. If it fails, open `docs/sources.md` and look for a backup entry for that channel.
3. If there is no backup, search the original catalog (for example SerenoTV) for the
   channel and copy the current direct URL.
4. Test the candidate URL before editing the playlist.
5. Update the playlist, `docs/sources.md` and the verification date.

## Every Pluto TV channel fails at once

All Pluto entries use the `jmp2.uk` redirector. If they fail together:

1. Test a single URL manually.
2. Check whether `jmp2.uk` changed its path format.
3. As a fallback, resolve the Pluto channel ID through another Pluto endpoint and update
   the affected entries.

## Both EnerGeek channels return 403 or 404

The EnerGeek URLs include a SerenoTV token:

```text
...?token=S3r3noTV
```

If the token expired, both channels fail at the same time. Refresh the token from the
SerenoTV catalog and update both entries, or remove the channels until a new token is
available.

## Locomotion repeats the same programming day

This is expected. The official Locomotion feed publishes several variants that share the
same encoder, and the feed loops. The playlist uses an alternate live signal as the primary
entry and keeps the official one only as a fallback. Do not "fix" the loop by adding more
official variants: they all show the same thing.

## A channel buffers every few seconds

- Test with `ffprobe` or VLC on a computer to separate network from player issues.
- Restreams hosted on free CDNs are often overloaded at peak hours.
- Try the backup entry if one exists.
- Lower the player quality only if the stream exposes multiple variants; otherwise the
  problem is upstream.

## Audio plays but the picture is black

- The stream may be audio-only during an ad break or a transitional slate.
- Check another segment a minute later.
- If it persists, replace the channel: the upstream encoder is likely broken.

## The EPG is empty

The playlists do not embed EPG data. Configure the guide separately in the player. See the
EPG table in `README.md` and `docs/sources.md`.

## A player rejects an M3U file as too small

Some players ignore files below a minimum size. Add comment lines as padding:

```text
# padding: keeps the file above the minimum size some players expect
```

Comments are ignored by M3U parsers and do not affect playback.

## A channel works in VLC but not on the TV

Players send different headers. OwnTV lets you set **User-Agent** and **Referer** per
source. If the stream expects a browser-like User-Agent, set one. If it expects a specific
origin, set the Referer.

## The same channel appears twice

The same playlist was probably imported more than once, or two lists contain the same
channel. Remove the duplicate source or delete the duplicate entry from the playlist.

## A source works on one network but not another

The channel may be **geoblocked**, or the network may block the CDN. Test from a phone on
mobile data to confirm.
