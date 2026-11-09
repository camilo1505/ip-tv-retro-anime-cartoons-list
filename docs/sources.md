# Sources and channel notes

Last full verification: **2026-11-09**.

Method: every URL was resolved from the master playlist to a variant, then to a media
playlist, and the last segment was downloaded. A channel is considered working when the
segment is a real video segment (not an empty file, not an HTML error page).

Group names in the playlists are in English; channel names are kept as published by each
source.

## Conventions

- **Status** reflects the latest verification date shown in each table: `Working`,
  `Degraded` (plays but unstable) or `Dead` (fails).
- **Type** values: `Official` (published by the broadcaster), `FAST channel` (commercial
  free ad-supported service), `Community` (fan-run) and `Restream` (third-party relay of
  another signal).
- **Country** is the country declared by the source catalog; it is not necessarily where
  the stream is hosted.

---

## `lists/locomotion-anime.m3u` (12 channels)

| # | Channel | Language | Type | Source | Status (2026-11-09) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Locomotion (official fallback) | Spanish | Official | `146.19.49.197:81/live/loco.m3u8` | **Temporarily down (HTTP 404)** | Official feed. All official variants share the same encoder, so they repeat the same day. Kept so the TV recovers automatically when the feed returns. |
| 2 | Anime XTV | Spanish | Community | `animezonetv.net:81/live_hls/animetest/index.m3u8` | Working | Alternate server of the AnimeZone project. |
| 3 | Pluto TV Anime (LatAm) | Spanish | Official (via `jmp2.uk`) | `jmp2.uk/plu-5dcde17bf6591d0009839e02.m3u8` | Working | Official Pluto TV channel through the jmp2.uk redirector. |
| 4 | One Piece (LatAm) | Spanish | Official (via `jmp2.uk`) | `jmp2.uk/plu-5ff4b9ccf938f8000779eb99.m3u8` | Working | Official Pluto TV channel. |
| 5 | Naruto (Spanish) | Spanish | Official (via `jmp2.uk`) | `jmp2.uk/plu-5ee92e72fb286e0007285fec.m3u8` | Working | Official Pluto TV channel. |
| 6 | Detective Conan | Spanish | Official (via `jmp2.uk`) | `jmp2.uk/plu-629a066860ef810008267b70.m3u8` | Working | Official Pluto TV channel. |
| 7 | MAX Anime | — | Community | `cdnlive.klicgo.net/maxanime/live/playlist.m3u8` | Working | Community channel. |
| 8 | Tooncast | Spanish | Restream | `45.134.141.161:2200/ARG/Tooncast/index.m3u8` | Working | Third-party restream. |
| 9 | Tooncast (backup) | Spanish | Restream | `190.61.42.218:9000/play/a06i/index.m3u8` | Working | Third-party restream; use if entry 8 fails. |
| 10 | Nickelodeon Clásico | Spanish | Official (via `jmp2.uk`) | `jmp2.uk/plu-6824cda00101510f9eeaa011.m3u8` | Working | Official Pluto TV channel. |
| 11 | Nickelodeon Toons (LatAm) | Spanish | Official (via `jmp2.uk`) | `jmp2.uk/plu-645952687cb4b100084ed52e.m3u8` | Working | Official Pluto TV channel. |
| 12 | Cartoon Network (LatAm) | Spanish | Restream | `158.172.217.18:8000/play/a03a/index.m3u8` | Working | Third-party restream. |

Removed on 2026-11-09: the bozztv primary Locomotion signal and AnimeZoneTV (see below).

### Locomotion background

- The official playlist (`http://locomotiontv.com/envivo/xtv/m3u`) publishes four entries:
  `51.222.85.85:81/hls/loco/index.m3u8` and three variants on
  `146.19.49.197:81` (`loco.m3u8`, `loco_hi`, `loco_low`).
- Those three variants are the same multibitrate feed: the master playlist only lists
  `loco_low`, `loco_mid` and `loco_hi`. That is why they show the same content at the same
  time.
- The feed repeats the same programming day in a loop, so the three entries were replaced
  by one alternate signal plus one official fallback.
- **2026-11-09: both signals died the same day.** The alternate signal
  (`lbgo.bozztv.com`, SerenoTV channel `25664` "Segunda señal") disappeared because the
  whole `bozztv.com` domain stopped resolving (no NS records; confirmed against Google,
  Cloudflare and Quad9). The official feed now returns **HTTP 404 on every variant it
  still publishes**; the servers answer (nginx), so the encoders or paths were taken
  down, not the machines.
- Only the official fallback entry is kept in the playlist. When the feed returns, the
  12-hour TV refresh picks it up automatically.
- **States to distinguish when the official feed comes back.** The HLS check passes in
  all three cases, so a passing script result is not proof of programming:
  1. real live signal (what you want);
  2. the day-loop: the same programming day repeated endlessly (expected behaviour of
     this feed, not a bug);
  3. the holding card ("Sentimos los inconvenientes / volveremos pronto"): a static
     slate, not programming.
- Play the entry in VLC and confirm which state it is in before recording the status as
  `Working` here.
- SerenoTV channel `24791` ("Canal Locomotion") is **not** live HLS: it is a VOD playlist
  (`transmision.mode = "lista"`) over `videos.gia.tv`, so it cannot be used as a single
  channel.

### AnimeZoneTV removed

`animezonetv.com/hls/stream.m3u8` now answers `Access Denied!` (a PHP block, 15 bytes of
plain text) instead of an HLS playlist. The same block applies to
`animezonetv.net/hls/stream.m3u8`, with or without a browser User-Agent or a matching
Referer, so it is a server-side block, not a header problem. The sibling server
`animezonetv.net:81/live_hls/animetest/index.m3u8` (Anime XTV) still works and stays in
the list. Re-add AnimeZoneTV only if the block is lifted.

---

## `lists/anime-extra.m3u` (7 channels)

All channels are official Pluto TV feeds served through `jmp2.uk`:

| Channel | Pluto channel id | Status (2026-11-02) |
| --- | --- | --- |
| ANIME x HIDIVE | `6793eaa4bc03978b9bc63db1` | Working |
| Pluto TV Anime Movies | `67ed8f7e443f0671bc2b2368` | Working |
| Pluto TV Anime CA | `68d25b620a0f3829b116bb6f` | Working |
| Pluto TV Anime Ação | `604b79c558393100078faeef` | Working |
| Naruto Shippuden | `64c92f965580090008084968` | Working |
| It's Anime | `6a4fda4538f47f0af402bdb0` | Working |
| Big A Anime | `6a3c5fa46276c42ac6726b27` | Working |

Language varies by channel and region; do not assume Spanish. Check the source before
adding a channel to a Spanish-oriented list.

EPG: `https://i.mjh.nz/PlutoTV/us.xml`.

---

## `lists/retro-sereno.m3u` (10 channels)

Third-party live HLS channels originally found through the SerenoTV catalog. SerenoTV is
only the directory: the playlists point directly at the CDN that serves each channel
(`vdopanel`, `enlineatv`, `energeek`, `brstream`, `srvif`, `cloudfront`,
`frequency.stream`, plus Pluto TV via `jmp2.uk`).

**2026-11-09:** the `bozztv.com` domain stopped resolving entirely, killing six restreams
(Retro Magico, Retro Toons, Clasicos Animados, Dragon Ball, X-Men, Delmi TV, Delmi
Channel shared it; Dragon Ball was replaced, the rest removed). Dragon Ball now uses the
official Pluto TV feeds.

| Channel | Country | Language | Type | Content | Status (2026-11-09) | URL |
| --- | --- | --- | --- | --- | --- | --- |
| Magic Kids OK | Argentina | Spanish | Restream | Argentine kids channel, nostalgic | Working | `kali.vdopanel.com:3957/stream/play.m3u8` |
| Canal Retro TV | Costa Rica | Spanish | Restream | Retro programming in Spanish | Working | `stream.enlineatv.net/hls/retrotv/index.m3u8` |
| Dragon Ball Z (Pluto TV) | — | Spanish | FAST channel (via `jmp2.uk`) | Dragon Ball Z 24/7, official | Working | `jmp2.uk/plu-68e8fd7c3ede4398bc69af93.m3u8` |
| Dragon Ball (Pluto TV) | — | Spanish | FAST channel (via `jmp2.uk`) | Dragon Ball (original) 24/7, official | Working | `jmp2.uk/plu-685a996c7c4f2ad40cb4f276.m3u8` |
| EnerGeek | Chile | Spanish | Restream (token) | 80s/90s/2000s series and anime | Working | `cl-2.backend.energeek.cl/bkp/egretroweb/index.m3u8?token=S3r3noTV` |
| EnerGeek Fan | Chile | Spanish | Restream (token) | Cartoons, anime, live-action and movies | Working | `cl-2.backend.energeek.cl/bkp/egfanweb/index.m3u8?token=S3r3noTV` |
| Retro Cartoon | Brazil | Portuguese | Restream | 1940s-1980s classic cartoons | Working | `stmv1.video.brstream.com.br/retrotv/retrotv/playlist.m3u8` |
| Otaku Sign TV | Brazil | Portuguese | Restream | Anime 24/7 | Working | `stmv1.srvif.com/anime/anime/playlist.m3u8` |
| FilmRise Anime | United States | English | FAST channel | Anime movies and series | Working | `dvu7aia8rjlfm.cloudfront.net/master.m3u8` |
| RetroCrush | United States | English | FAST channel | Retro anime | Working | `linear-899.frequency.stream/dist/cineverse/899/hls/master/playlist.m3u8` |

Removed on 2026-11-09 (bozztv domain dead, no replacement found):

| Channel | Last URL (dead) |
| --- | --- |
| Retro Magico | `live20.bozztv.com/akamaissh101/ssh101/retromagicocnl/chunks.m3u8` |
| Retro Toons | `183.bozztv.com/giatv/giatv-Retrotoonstv/Retrotoonstv/chunks.m3u8` |
| Clasicos Animados | `live20.bozztv.com/giatvplayout7/giatv-209599/index.m3u8` |
| X-Men (1992) | `live20.bozztv.com/giatvplayout7/giatv-210703/playlist.m3u8` |
| Delmi TV | `live20.bozztv.com/giatvplayout7/giatv-210634/playlist.m3u8` |
| Delmi Channel | `live20.bozztv.com/giatvplayout7/giatv-209474/playlist.m3u8` |

Dead ends checked while looking for replacements: an old `vivo.solumedia.com:19360`
mirror of Retro Magico (404), the AnimeZone project (blocked; see the AnimeZoneTV note in
the Locomotion list), Tele Clasicos / The Retro Channel / Retro TV Palmares (network
timeouts or wrong genre: music), Best Clasicos TV and Ciudad Magica TV (work, but they air
classic series/movies in general, not cartoons or anime — out of scope).

Notes:

- The EnerGeek URLs include a SerenoTV token (`token=S3r3noTV`). If the channel stops
  working, the token may have expired and needs to be refreshed from SerenoTV.
- The Pluto TV Dragon Ball feeds were added on 2026-11-09 as the replacement for the dead
  bozztv "Dragon Ball" restream (which aired Dragon Ball Z 24/7). Both are official
  Pluto channels with Spanish audio (per the Pluto API summaries), but they do not appear
  yet in the `i.mjh.nz` regional EPG files, so the guide will be empty for them until
  mjh.nz picks them up.
- Portuguese and English channels are grouped separately (`Portuguese`, `English`) so the
  Spanish audio lists stay easy to browse.
- Premium SerenoTV channels (Anime Shock, Anime Presente 2, Macross 24h, Tom & Jerry,
  Dinosaurios, Retro BIG, Ninjala, Pop Japones) require an account and are not included.

---

## EPG reference

| Guide | URL |
| --- | --- |
| Pluto TV Mexico | `https://i.mjh.nz/PlutoTV/mx.xml` |
| Pluto TV United States | `https://i.mjh.nz/PlutoTV/us.xml` |
| Locomotion official | `http://epg.locomotiontv.com/guia.xml` |

The alternate Locomotion signal has no EPG of its own, so the official guide may not match
its schedule.

---

## Fragility and fallbacks

| Risk | Channels | Why | Fallback |
| --- | --- | --- | --- |
| Realized (2026-11-09) | Former bozztv restreams | The `bozztv.com` domain stopped resolving entirely; the entries were removed | None; GIA/bozztv must publish new URLs (check the SerenoTV catalog) |
| High | Locomotion (official fallback) | The official feed returns 404 on every variant since 2026-11-09; servers alive, so it may return | None; when it comes back it may show the day-loop or the "volveremos pronto" holding card |
| High | EnerGeek, EnerGeek Fan | The URL carries a SerenoTV token that can expire | Refresh the token from SerenoTV |
| Medium | Magic Kids OK, Canal Retro TV, Retro Cartoon, Otaku Sign TV | Small third-party hosts (`vdopanel`, `enlineatv`, `brstream`, `srvif`) | None |
| Low | Pluto TV entries (including Dragon Ball) | Depend on the `jmp2.uk` redirector | Resolve the Pluto channel id through another endpoint |
| Low | Tooncast | Third-party restream | The backup Tooncast entry |
| Low | FilmRise Anime, RetroCrush | Commercial FAST endpoints (`cloudfront`, `frequency.stream`) | None |

## Verification helper

Run the checker after any change:

```bash
python3 scripts/verify_playlists.py
```

It resolves each URL from the master playlist to a media playlist, downloads the last
segment and reports whether it contains real media. See `docs/verification.md` for the full
method, thresholds and manual fallback.
