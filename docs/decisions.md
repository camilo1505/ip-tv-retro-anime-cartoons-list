# Decisions

Short architecture decision records (ADRs) for choices that should not be undone without
understanding the reason. Format: context → decision → consequences.

---

## ADR-001: One playlist per theme, with stable filenames

**Context.** The TV needs predictable URLs, and the content mixes official channels,
restreams and different languages.

**Decision.** Keep three files with stable names:

- `lists/locomotion-anime.m3u` — main Locomotion/anime/cartoon list;
- `lists/anime-extra.m3u` — Pluto TV anime;
- `lists/retro-sereno.m3u` — retro and anime channels discovered through SerenoTV.

**Consequences.** Renaming a file requires editing the TV source. Adding a new theme should
create a new file instead of reorganising existing ones.

---

## ADR-002: The repository stays public

**Context.** OwnTV downloads playlists over plain HTTP and cannot send an `Authorization`
header. Private GitHub raw URLs return 404 to the TV.

**Decision.** Keep the repository public and store only channel metadata.

**Consequences.** The lists are readable by anyone with the URL. No credentials, personal
data or private information may be committed. If privacy becomes a requirement, a public
host or proxy must be set up before changing the repository visibility.

---

## ADR-003: Locomotion uses the alternate signal as primary

**Context.** The official Locomotion playlist publishes the same multibitrate feed under
several names, and that feed repeats the same programming day in a loop.

**Decision.** Use the alternate live signal (SerenoTV "Segunda señal") as the primary
Locomotion entry, and keep one official URL as a fallback.

**Consequences.** Locomotion shows different content from the official loop, but depends on
a third-party restream that can disappear. The official fallback is stable but repetitive.

---

## ADR-004: No adult content

**Context.** The repository is public and its purpose is retro cartoons and anime.

**Decision.** Do not include +18 channels, lists or references.

**Consequences.** Adult animation channels are kept out even when they are technically
available. This keeps the repository safe to share and consistent with its name.

---

## ADR-005: English for documentation and group titles

**Context.** The channel names come from Spanish-, Portuguese- and English-language
sources, while the repository is meant to be readable by a broad audience and by automated
agents.

**Decision.** Write documentation and `group-title` values in English; keep channel names
as published by the source.

**Consequences.** Group names are consistent across lists. Renaming a group is safe for
playback, but it changes how channels are grouped in players.

---

## ADR-006: Link directly to the CDN, not to the catalog page

**Context.** SerenoTV was used to discover channels, but its pages are not streams and may
require sessions or tokens.

**Decision.** Store the direct HLS URL of each channel. SerenoTV is treated as a directory,
not as a proxy.

**Consequences.** Playback does not depend on SerenoTV being up, except for the EnerGeek
token. URLs are more fragile because CDNs rotate paths.

---

## ADR-007: Pluto TV through jmp2.uk

**Context.** Pluto TV exposes channels through several endpoints that change over time.

**Decision.** Use `https://jmp2.uk/plu-<channel-id>.m3u8` for Pluto entries.

**Consequences.** All Pluto channels share one dependency. If the redirector changes, they
fail together.

---

## ADR-008: No embedded EPG

**Context.** The playlists mix sources from several countries, and no single guide covers
all of them.

**Decision.** Keep EPG configuration out of the playlists and document the guides
separately in `README.md`.

**Consequences.** Users configure the guide in the player. Some channels have no accurate
guide, especially the alternate Locomotion signal.

---

## ADR-009: A Git repository instead of gists

**Context.** Earlier versions used GitHub gists as the TV source. Gists are harder to
organise, have no directory structure and make multi-file maintenance awkward.

**Decision.** Host the playlists in a Git repository with one file per list and versioned
documentation.

**Consequences.** Every change is reviewable and reversible. The TV uses raw URLs, so file
paths and branch names are part of the public contract.

---

## ADR-010: Twelve-hour refresh

**Context.** Restreams change frequently, but refreshing too often wastes resources and can
hit rate limits.

**Decision.** Set OwnTV sources to refresh every 12 hours.

**Consequences.** A broken channel may remain visible for up to half a day. Use a manual
resync after an urgent fix.
