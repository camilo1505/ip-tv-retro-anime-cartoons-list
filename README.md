# IPTV Retro Anime Cartoons List

Curated M3U playlists for **retro cartoons, anime and 24/7 animation channels**, kept for personal use with [OwnTV](https://github.com/owntv-app) on Android TV (also works with VLC, Kodi, TiviMate or any M3U player).

The playlists are plain text files served from this repository, so they can be imported by URL and updated with a `git push`.

> This repository contains **no adult content**.

## Playlists

| Playlist | Channels | Content |
| --- | --- | --- |
| [`lists/locomotion-anime.m3u`](lists/locomotion-anime.m3u) | 14 | Locomotion, anime and cartoon channels used as the main list |
| [`lists/anime-extra.m3u`](lists/anime-extra.m3u) | 7 | Pluto TV anime channels |
| [`lists/retro-sereno.m3u`](lists/retro-sereno.m3u) | 15 | Retro cartoons and anime (Spanish, Portuguese and English) found through the SerenoTV catalog |

### Raw URLs

Replace `main` with the branch you want to use if it ever changes.

```text
https://raw.githubusercontent.com/camilo1505/ip-tv-retro-anime-cartoons-list/main/lists/locomotion-anime.m3u
https://raw.githubusercontent.com/camilo1505/ip-tv-retro-anime-cartoons-list/main/lists/anime-extra.m3u
https://raw.githubusercontent.com/camilo1505/ip-tv-retro-anime-cartoons-list/main/lists/retro-sereno.m3u
```

## Usage

### OwnTV (Android TV)

1. Open **Settings → Sources & guide → Playlists → Add source**.
2. Choose **M3U / M3U8**.
3. Paste one of the raw URLs above.
4. Set **Auto refresh** to `12 hours`.
5. Start the import, then pick the list from the selector at the top of the screen.

Keep only the lists you actually watch marked as visible; the selector lets you switch between them without mixing groups.

### Any other player

Point VLC, Kodi, TiviMate or similar to the same raw URL.

## EPG

The lists do not embed an EPG URL. These are the guides used in practice:

| Source | EPG URL | Notes |
| --- | --- | --- |
| Pluto TV (Mexico) | `https://i.mjh.nz/PlutoTV/mx.xml` | Good match for the Pluto channels in these lists |
| Pluto TV (United States) | `https://i.mjh.nz/PlutoTV/us.xml` | Used for the anime extra list |
| Locomotion (official) | `http://epg.locomotiontv.com/guia.xml` | May not match the alternate Locomotion signal |

## Repository layout

```text
.
├── AGENTS.md
├── README.md
├── lists/
│   ├── locomotion-anime.m3u
│   ├── anime-extra.m3u
│   └── retro-sereno.m3u
├── docs/
│   ├── sources.md
│   ├── verification.md
│   ├── owntv.md
│   ├── troubleshooting.md
│   └── decisions.md
└── scripts/
    └── verify_playlists.py
```

- `docs/sources.md` documents where every channel comes from, which ones are official and which ones are third-party restreams.
- `docs/verification.md` explains how to validate that a stream is alive.
- `docs/owntv.md` covers the Android TV setup and its limits.
- `docs/troubleshooting.md` lists known failure modes and fixes.
- `docs/decisions.md` records why the lists are organised this way.
- `AGENTS.md` is the quick operational contract for maintainers and AI agents.

## Notes and caveats

- **Restreams are volatile.** Channels hosted by third parties (especially `bozztv`, `vdopanel` and similar) can change URL or disappear without notice. If a channel stops working, check `docs/sources.md` for the original source and replace the entry.
- **No guarantee of uptime or quality.** Most streams are public and community-run.
- **Geoblocking** may apply to some channels depending on your country.
- **No adult content** is included in this repository.

## Maintenance

Validate every URL in the playlists:

```bash
python3 scripts/verify_playlists.py
```

Only one list:

```bash
python3 scripts/verify_playlists.py --list retro-sereno
```

The script resolves each master playlist to a media playlist, downloads the last segment
and reports whether it contains real media. A 200 response alone is not proof; see
[`docs/verification.md`](docs/verification.md).

After editing a playlist:

```bash
git add .
git commit -m "Update <playlist>: <short reason>"
git push
```

Players pick up the change on their next automatic refresh, or immediately after a manual re-sync.

## Disclaimer

This repository only stores playlist metadata (channel names and stream URLs) for personal use. It does not host, transcode or redistribute any video content. All trademarks and content belong to their respective owners.
