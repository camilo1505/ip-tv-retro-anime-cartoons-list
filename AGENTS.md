# AGENTS.md

Operational notes for AI agents and maintainers working on this repository.

## Purpose and scope

This repository keeps M3U playlists for **retro cartoons, anime and 24/7 animation
channels**. The lists are consumed by [OwnTV](https://github.com/owntv-app) on Android TV,
but any M3U player can read them.

- Keep the repo focused on that scope.
- **No adult content.** Do not add +18 channels, lists, links or references.
- Group titles in the playlists are in English. Channel names stay as published by the
  source.

## Non-negotiable constraints

### The repository must stay public

OwnTV fetches playlists over plain HTTP and cannot send an `Authorization` header. Raw URLs
from a private GitHub repository return **404** to the TV.

If the repository ever needs to be private, do not flip the visibility first. Set up a
public host or proxy for the playlists, point the TV sources at it, verify playback, and
only then make the repository private.

### Keep file paths stable

OwnTV sources point to exact raw URLs such as:

```text
https://raw.githubusercontent.com/camilo1505/ip-tv-retro-anime-cartoons-list/main/lists/locomotion-anime.m3u
```

Renaming or moving a file in `lists/` breaks the TV silently: the source keeps working but
stops updating. If a file must be renamed, update the TV source in the same session.

### Store metadata only

This repository contains channel names and stream URLs. It must not contain:

- credentials, personal access tokens, API keys or cookies;
- personal data, LAN addresses, device serial numbers or local filesystem paths;
- video files or anything that redistributes content.

The `token=S3r3noTV` query string in the EnerGeek URLs is a third-party public token
published by SerenoTV, not a secret of this project. Do not add new tokens without checking
that they are meant to be public.

## Repository map

```text
.
├── AGENTS.md                  # this file
├── README.md                  # user-facing overview
├── lists/
│   ├── locomotion-anime.m3u   # 14 channels: Locomotion, anime, cartoons
│   ├── anime-extra.m3u        # 7 Pluto TV anime channels
│   └── retro-sereno.m3u       # 15 retro/anime channels (ES, PT, EN)
├── docs/
│   ├── sources.md             # per-channel origin, status and caveats
│   ├── verification.md        # how to validate streams
│   ├── owntv.md               # how the TV consumes the lists
│   ├── troubleshooting.md     # known failure modes
│   └── decisions.md           # why the lists look the way they do
└── scripts/
    └── verify_playlists.py    # runnable stream checker
```

## Change workflow

1. Read `docs/sources.md` before touching a channel.
2. Verify the candidate URL with `scripts/verify_playlists.py` (see
   `docs/verification.md`). A 200 response is not proof: HTML error pages and empty
   segments are common.
3. Edit only the affected file in `lists/`.
4. Update the channel count in `README.md` and the relevant table in `docs/sources.md`.
5. Commit with a message such as `Update retro-sereno: replace dead Dragon Ball stream`.
6. Push to `main`.
7. Re-sync the source in OwnTV, or wait for the 12-hour automatic refresh.
8. Confirm the channel count in OwnTV matches the playlist.

## Verification contract

A channel is considered working when:

1. the URL returns an HLS playlist (`#EXTM3U`);
2. if it is a master playlist, a variant resolves to a media playlist;
3. the last segment downloads successfully;
4. the segment is real media, not HTML/JSON, and is not empty.

`scripts/verify_playlists.py` implements this flow. Use `>20 KB` as a practical minimum for
a segment, and record the verification date in `docs/sources.md`.

## Known fragility

- **Bozztv restreams** (`live20.bozztv.com`, `183.bozztv.com`, `lbgo.bozztv.com`) rotate
  URLs without notice. They are the most likely channels to break.
- **EnerGeek** URLs depend on a SerenoTV token. If both EnerGeek channels fail at once,
  suspect the token before the CDN.
- **Locomotion official feed** repeats the same programming day in a loop. The preferred
  entry is the alternate live signal; the official one is only a fallback.
- **Pluto TV** channels are reached through `jmp2.uk`. If that redirector changes, every
  Pluto entry fails together.
- **Geoblocking** may make a channel work in one country and fail in another.

## Things that look like bugs but are not

- Locomotion showing the same episode again: the official feed is a loop.
- Both Tooncast entries showing the same content: they share the same upstream.
- Empty EPG: the playlists do not embed EPG data; it is configured separately in the
  player.
- A very small M3U being rejected by a player: add comment lines as padding.
- A channel working in VLC but not in another player: request headers (User-Agent,
  Referer) differ.

## Related documents

- `docs/verification.md` — validation method and script usage.
- `docs/owntv.md` — TV setup, refresh behaviour and remote-control navigation.
- `docs/troubleshooting.md` — symptom → cause → fix.
- `docs/decisions.md` — architectural decisions already made.
- `docs/sources.md` — channel-by-channel reference.
