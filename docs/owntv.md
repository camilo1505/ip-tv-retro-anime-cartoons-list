# OwnTV setup and behaviour

The playlists are consumed by [OwnTV](https://github.com/owntv-app) on Android TV. This
document explains how the sources are configured and what the app can and cannot do.

## How the sources are configured

1. Open **Settings → Sources & guide → Playlists**.
2. Select **Add source** (or **Agregar fuente** in the Spanish UI).
3. Choose **M3U / M3U8**.
4. Set a **Name** that identifies the list, for example `Locomotion + Anime`.
5. Paste the raw GitHub URL of the playlist.
6. Set **Auto refresh** to `12 hours`.
7. Start the import.
8. Pick the list from the selector at the top of the **Live TV** screen.

The three sources currently expected are:

| Name | File | Channels |
| --- | --- | --- |
| `Locomotion + Anime` | `lists/locomotion-anime.m3u` | 14 |
| `Anime extra` | `lists/anime-extra.m3u` | 7 |
| `Retro Anime Sereno` | `lists/retro-sereno.m3u` | 15 |

Names are cosmetic; the important part is the URL.

## What OwnTV can and cannot send

OwnTV exposes optional **User-Agent** and **Referer** fields per source. That is enough for
most restreams.

It does **not** support custom `Authorization` headers or HTTP basic auth. This is why the
repository must stay public: a private GitHub raw URL returns 404 to the app.

If a future source needs authentication, the workaround is an intermediate host or proxy
that adds the credentials and exposes a public URL, not a private repository.

## Refresh behaviour

- Sources refresh automatically every 12 hours.
- After a change in the repository, use **Resync** / **Volver a sincronizar** to apply it
  immediately.
- The resync dialog offers two options:
  - **Resync now** keeps favourites, history and playback positions.
  - **Resync and remove missing titles** also drops entries that disappeared upstream.
- A resync does not delete manual settings such as the source name or refresh interval.

## Editing an existing source

1. Open the source list.
2. Move the focus to the source row and press **Right** to open the side panel.
3. Choose **Edit**.
4. Change the URL or name.
5. Choose **Save**.
6. Choose **Resync → Resync now**.
7. Confirm the channel count next to the source.

If the channel count does not change, the playlist probably did not parse. Check the URL
with `scripts/verify_playlists.py` and `docs/verification.md`.

## Remote-control navigation quirks

These are behaviours observed in the Android TV build; they matter when automating the app.

- **Focus can jump to the left sidebar.** Press **Right** once to return to the content
  area, then continue with Up/Down.
- **Tapping a row does not always open it.** Some rows only react to the D-pad: focus the
  row and press **OK**.
- **The on-screen keyboard captures the D-pad.** Pressing Down inside a text field can move
  the keyboard focus instead of the form focus.
- **TAB** moves to the next focusable element, but it can skip an empty URL field. Use
  Up/Down after closing the keyboard.
- **BACK closes the keyboard if it is open.** If the keyboard is already closed, BACK
  leaves the form without saving. Save first, then leave.
- **Spaces in `adb shell input text`** must be written as `%s`; otherwise only the first
  word is typed.
- **Select-all in a text field** can be done with `adb shell input keycombination 113 29`
  (Ctrl+A).

## Remote form

OwnTV can display a local web form so a playlist can be added from a phone or computer. It
only works on the same local network and the address is shown on the TV. It is convenient
for long URLs, but it is optional: the same data can be entered with the remote.

## Verifying the result

After adding or resyncing a source:

1. Open **Live TV**.
2. Check the channel count in the header. It should equal the sum of the imported lists
   (currently 36 channels with all three sources).
3. Open one channel from each source and confirm it starts playing.
4. If a channel fails, test its URL with the verification script before editing the TV.

## Updating the repository without touching the TV

As long as the file path and branch stay the same, a normal `git push` is enough. The TV
picks up the new content on its next automatic refresh, or immediately after a manual
resync. The raw URL does not change when the playlist content changes.
