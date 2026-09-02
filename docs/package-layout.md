# Package layout

> The full census behind the claim in the README: this title is a shell plus an
> emulator, not a PS3 game. Everything here is read from an extracted package
> with `tools/inventory.py`; no keys and no decryption are involved.

## Identity

```
TITLE                NEOGEO STATION / METAL SLUG 2
TITLE_ID             NPEB00681
CATEGORY             HG          (HDD game)
PS3_SYSTEM_VER       03.6000
NP_COMMUNICATION_ID  NPWR02570_00
APP_VER / VERSION    01.00
```

`PARAM.SFO` is length-prefixed, so `strings` recovers almost none of this —
`tools/inventory.py` parses the index table properly.

## The three binaries

All are NPDRM SELFs at key revision `0x10` sharing auth ID `0x1010000001000003`.

| File | Size | Role |
|---|---|---|
| `USRDIR/EBOOT.BIN` | 3,149,856 | NEOGEO STATION shell — front end, menus, saves |
| `USRDIR/021/modules/libacc_neogeo_ps3.sprx` | 2,866,464 | Neo Geo hardware core |
| `USRDIR/021/modules/libemu_m68k_ps3.sprx` | 924,032 | Motorola 68000 CPU emulator |

The EBOOT being the *smallest* interesting binary is the tell. In a normal PS3
title the executable is the game; here it is a launcher, and the 3.8 MB of
emulator sitting beside it in `modules/` is what actually runs Metal Slug 2.

## The game data

| File | Size | What |
|---|---|---|
| `USRDIR/021/roms/MetalSlug2.ccf` | 16,732,208 | Program/graphics ROM data, `CCF\0` container |
| `USRDIR/021/roms/MetalSlug2_snd.ccf` | 6,810,480 | Sound ROM data |
| `USRDIR/system/srams/neogeo_sram.bin.m` | 1,604 | Neo Geo SRAM image |

`.ccf` is a flat container beginning with the ASCII magic `CCF\0`. This is the
Neo Geo ROM set — 68000 code and arcade assets — and it is the reason nothing in
this repository may ever include game data.

## Assets and scripts

258 of the package's 286 files begin with the magic `mdf\0` — M2's wrapper
around two different payloads, distinguished only by the inner extension:

- **`.psb.m`** — PSB, M2's binary structured format, used here for UI motion,
  backgrounds, manual pages and config tables. The largest are the menu
  backgrounds (`system/motion/bg03.psb.m`, 4.8 MB).
- **`.nut.m`** — compiled **Squirrel** scripts. The shell's entire UI is
  scripted: `setting_screen_sub`, `sound`, `watch_pad`, `wipe`,
  `shareddata_installer`, `systemdata` and others.

That the front end is Squirrel rather than native code matters for a
recompilation: a large share of the shell's behaviour is interpreted at runtime,
so lifting the EBOOT gets the interpreter, not the menu logic.

Audio is ATRAC3 (`neogeo_logo.at3`, `neomenu.at3`) with `.hd3`/`.bd3` sound-bank
pairs for menu effects.

## Directory shape

```
USRDIR/
├── EBOOT.BIN
├── purchased.main.edat        # licence data
├── 001/ .. 010/               # one PNG each: per-slot player art
├── 021/                       # the game itself
│   ├── roms/                  # CCF ROM containers
│   ├── modules/               # the two emulator PRXs
│   ├── motion/  manual/  config/  raw/
└── system/                    # shell: motion, script, sound, srams
```

The numbered directories are slots. `001`–`010` hold a single
`raw/neogeo_player_local.png.m` apiece; `021` is where this title's ROM,
emulator modules and per-title assets live — consistent with one NEOGEO STATION
shell that ships per title with its own numbered payload.

---

*Part of the [Metal Slug 2 static recompilation](../README.md).*
