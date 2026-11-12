# Own channel: landing design

Status: approved design (2026-11-09). Nothing implemented yet — this document is the
agreed blueprint for a personal TV channel built from a private library of series,
bumpers, transitions and promos.

## Goals and constraints

- A live, scheduled TV channel (not VOD) with a Locomotion-style on-air identity.
- Audience: 2 viewers (1 on the home LAN, 1 remote). Personal use only.
- Runs alongside the existing setup: the channel is consumed as one more M3U source in
  OwnTV, next to the playlists in `lists/`.
- Two machines, two roles: an always-on server (transmission) and the existing GPU
  workstation (pautas factory, intermittent).

## Hardware

| Machine | Role | Spec |
| --- | --- | --- |
| New mini PC | 24/7 playout server | Intel N100/N150 (Quick Sync), 16 GB RAM, 512 GB-1 TB NVMe, Ethernet, auto power-on in BIOS. ~15-25 W. |
| Existing workstation | Pautas factory | AMD Ryzen 5 5600X (6C/12T), 32 GB RAM, RTX 3070 Ti 8 GB (driver 595.112.07), Gigabyte B550 AORUS ELITE AX V2, 1 TB NVMe (root) + 512 GB NVMe + 1 TB HDD, Ethernet (eno1, 1 Gb/s, wired to the Hitron CGNV5UNE ONT) + Wi-Fi (wlp6s0), Nobara Linux 44 KDE (kernel 7.3.1), ComfyUI with MOSS-Image SFT INT8 ConvRot. |

Quick Sync does the transcoding on the mini PC; no GPU needed there. The 3070 Ti stays
in the workstation as the render farm.

The workstation is already provisioned for the factory role: 32 GB RAM covers ComfyUI plus
DaVinci Resolve at the same time, and the spare 512 GB NVMe plus the 1 TB HDD give scratch
space for batch QTGMC deinterlacing and optional upscaling without touching the system
drive. No hardware upgrade is required before the first pautas.

### LAN topology (measured 2026-11-12)

The ISP gateway is a **Hitron CGNV5UNE** (Tigo UNE, DOCSIS 3.0) at `192.168.1.254`. It is
gigabit: **4× RJ-45 10/100/1000 LAN ports**, Wi-Fi 6 (2×2 2.4 GHz + 2×2 5 GHz), 960 Mbps
down / 240 Mbps up on the DOCSIS side. It is the **only router and the only NAT**.

```text
Hitron CGNV5UNE (router, DHCP, 192.168.1.0/24)
├─ port 1 ── workstation        eno1, 1000 Mb/s
├─ port 2 ── mini PC (pending)  target 1000 Mb/s
├─ port 3 ── spare
├─ Wi-Fi  ── FAMILIA_GIRALDO_5G (built-in 5 GHz)
└─ extender ─ Xiaomi 4A, wireless relay, same subnet, no NAT
```

- **Workstation:** RTL8125 2.5GbE on `eno1`, trains at **1000 Mb/s**; internet measures
  **~250-400 Mbps** across runs (server-side variance dominates). Before the re-cable the
  same machine sat behind the Xiaomi at 100 Mb/s and measured ~84 Mbps.
- **Xiaomi Mi Router 4A** (`R4ACv2`, 100M ports) is **out of the wired path**, demoted to a
  wireless extender (SSID `CCGAX4D35_5G`, `192.168.1.184`). It no longer NATs, so there is
  one subnet and one NAT hop — `traceroute` shows a single hop to `192.168.1.254`. Its 100M
  ports now only affect devices plugged into it: keep wired clients off it.
- **Mini PC goes on ONT port 2.** Two of the four gigabit ports are free, so workstation ↔
  mini PC runs at 1 Gb/s (~110 MB/s) with no extra hardware. A 500 MB pauta copies in ~5 s
  instead of ~45 s.
- **No switch and no new router are required.** Both were costed against the old 100M path;
  the ONT already provides what they were going to buy. A 2.5G switch would gain nothing,
  since the ONT's LAN ports are gigabit.
- **Minor cleanup:** the workstation still holds a Wi-Fi lease on the same subnet
  (`192.168.1.147`). Harmless with route metrics in place, but `nmcli radio wifi off`
  removes the duplicate path.

Mini PC RAM: 16 GB is comfortable headroom, not a requirement — the whole stack (OS,
Docker, ErsatzTV, 2 ffmpeg sessions) peaks around 4 GB. Buy 32 GB only if the mini PC will
co-locate extra services (Jellyfin, Home Assistant, *arr stack, monitoring); otherwise the
money is better spent on NVMe capacity.

Storage sizing (channel bitrate): 480p ≈ 0.8-1 GB/h, 720p ≈ 1.5-1.8 GB/h, 1080p ≈ 2 GB/h.
A 1 TB NVMe holds roughly 700-1000 hours.

## Architecture

```text
Mini PC (Debian/Ubuntu Server, headless, Docker)
├─ ErsatzTV          — playout: scheduling, bumpers, promos, HLS via Quick Sync
│    reads: /library (series), /pautas (bumpers, intros, promos, transitions)
│    serves: HLS 1080p h264 ~4 Mbps + channels.m3u + XMLTV EPG (port 8409)
├─ Tailscale         — remote viewer joins as LAN; no open ports
└─ cloudflared       — (phase 2, optional) public URL with secret path

Workstation (intermittent)
└─ ComfyUI + DaVinci Resolve — produces pauta MP4s into the server's /pautas folder
```

- Home viewer: OwnTV source `http://<mini-pc-lan-ip>:8409/m3u/channels.m3u`.
- Remote viewer: same URL via the Tailscale IP of the mini PC.
- Both viewers trigger separate ffmpeg sessions (2 concurrent QSV transcodes — trivial
  for an N100).
- HLS adds 15-30 s of latency. Normal for internet TV; not a problem to fix.

## Playout design

- Everything is emitted onto a uniform 1080p canvas regardless of source resolution
  (480p-720p sources get scaled by the playout encoder).
- Schedule shape: bumper → block of 2-3 episodes → promo → bumper; dayparted groups
  (e.g. cartoons mornings, anime afternoons/nights) using ErsatzTV scheduling rules.
- Channel naming and groups in English (ADR-005); content stays in its original audio.

## Pautas factory (Locomotion-style)

```text
MOSS-Image SFT (INT8)      → backgrounds, cards, idents with rendered text
  (use layout/bounding-box templates — strong native text-in-image)
Wan 2.2 TI2V-5B GGUF       → animate 3-5 s idents (image-to-video)
  + LightX2V 4-step LoRA (fast); RIFE node interpolates to 24/30 fps
DaVinci Resolve            → typography, stingers, voice-over, final MP4
  → copy to /pautas on the mini PC
```

- 8 GB VRAM rules: Wan 2.2 5B GGUF is the workhorse (official ComfyUI workflow targets
  8 GB; GGUF quants via ComfyUI-GGUF). LTX-2.x (2.3/2.5, open weights, native ComfyUI)
  is worth testing for synced audio+video idents, but the 22B fp8 checkpoint is tight on
  8 GB — check for community GGUF quants first. 14B models and AnimateDiff are out.
- Voice-over: Qwen3-TTS (Apache 2.0, actively maintained; clones from a 3 s clip and has
  a VoiceDesign mode to invent the channel announcer) is the pick. Kokoro 82M for instant
  no-cloning drafts; XTTS v2 as fallback (non-commercial weights, acceptable for personal
  use).
- LoRA/DMD turbo (8-step) presets for fast iteration on MOSS-Image.

## Quality policy

- Do not gate the launch on AI upscaling. 480p-720p retro material is on-brand; the
  uniform canvas plus player scaling is acceptable.
- Mandatory pass only where needed: deinterlace interlaced sources (480i/576i) once,
  batch, with QTGMC (VapourSynth). Interlacing on modern panels looks broken; soft
  480p looks retro.
- Optional later pass: favorites only, Real-ESRGAN `realesr-animevideov3` + RIFE frame
  interpolation (both comfortable on the 3070 Ti). Run when the GPU is idle.

## Operation

- Docker restart policy brings the channel back after power cuts; BIOS auto power-on
  covers outages.
- Disk monitoring before the library outgrows the NVMe; library grows one series at a
  time.
- ErsatzTV web UI is the only day-to-day management surface.

## Out of scope (phase 2 candidates)

- Public URL via Cloudflare Tunnel with a secret path (decided against for launch:
  private VPN matches "personal use, 2 viewers"; tunnel needs no hardware changes to add
  later).
- VPS migration (only if 24/7 independence from home becomes a real requirement).
- EPG integration into this repository's docs, new-channel documentation, or adding the
  channel as a documented source next to the public lists.

## First milestone (after design sign-off)

1. Acquire mini PC; install OS + Docker; enable auto power-on.
2. Deploy ErsatzTV; point it at one test series folder.
3. Confirm playback in OwnTV over LAN (M3U + EPG visible).
4. Add Tailscale; confirm remote playback.
5. Produce the first 3 pautas with MOSS-Image; wire them in as bumpers.
6. Only then: normalize the full library and build the real schedule.
