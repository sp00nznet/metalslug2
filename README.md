# Metal Slug 2 (NEOGEO STATION) — Static Recompilation

> Turning SNK's *Metal Slug 2* on PS3 (`NPEB00681`, NEOGEO STATION) from a PSN
> package into a native executable — no emulator underneath.
>
> Except that this one already **is** an emulator, which is the interesting part.

This project takes the package's own `EBOOT.BIN`, disassembles every PowerPC
function, lifts them to C, and links the result against
[ps3recomp](https://github.com/sp00nznet/ps3recomp) — clean-room HLE runtime
libraries that stand in for the PS3 operating system. Same approach as
[twistedmetal](https://github.com/sp00nznet/twistedmetal),
[vf5](https://github.com/sp00nznet/vf5),
[flow](https://github.com/sp00nznet/flow) and
[simpsonsarcade-ps3](https://github.com/sp00nznet/simpsonsarcade-ps3).

**You supply your own copy.** No game binary, ROM, asset, key or licence is
committed here.

## What this title actually is

The hypothesis going in was that this would look like
[The Simpsons Arcade Game](https://github.com/sp00nznet/simpsonsarcade-ps3) —
a PS3 wrapper around an arcade emulator rather than a PS3 game. It does, and
more cleanly than expected. Running `tools/inventory.py` over an extracted
package says so without decrypting anything:

```
== SCE binaries (what actually executes)
   EBOOT.BIN                3149856 B  keyrev=0x0010  NPDRM
   libacc_neogeo_ps3.sprx   2866464 B  keyrev=0x0010  NPDRM
   libemu_m68k_ps3.sprx      924032 B  keyrev=0x0010  NPDRM

== Container formats
    258  M2 "mdf" wrapper (PSB asset or Squirrel script)
      2  CCF container (Neo Geo ROM data)
```

Three binaries, and the division of labour is legible from their names alone:

| Binary | What it is |
|---|---|
| `EBOOT.BIN` | The **NEOGEO STATION shell** — front end, menus, save handling. Its UI is driven by Squirrel scripts (`.nut`), not native code |
| `libacc_neogeo_ps3.sprx` | The **Neo Geo hardware core** — the emulated system around the CPU |
| `libemu_m68k_ps3.sprx` | The **Motorola 68000 CPU emulator**. The Neo Geo's main CPU is a 68000, and here it is, as its own PRX |

So the stack is a 68000 emulator inside a Neo Geo emulator inside a PS3 shell,
and this project recompiles the outermost layer to native code. The game itself
never appears as PowerPC at all — `MetalSlug2.ccf` is 68000 ROM data that the
emulated hardware reads.

That shape is *good* for a port. The parts most likely to be a problem in a
recompilation — a big bespoke renderer, SPURS job chains, a physics engine — are
absent. What matters instead is that the shell boots, the two PRXs load, and the
emulator gets its ROM and a framebuffer.

**Which also sets the bar honestly:** getting this running proves the PS3 layer
works. It does not port Metal Slug 2 — it ports the machine that runs it.

## Status

Analysis only so far. Nothing is lifted yet, and nothing builds.

| Phase | State |
|---|---|
| Package inventory | **done** — `NPEB00681`, 286 files, category HG, firmware 3.60+ |
| Architecture identified | **done** — shell EBOOT + Neo Geo core PRX + 68000 CPU PRX |
| Container formats mapped | **done** — `CCF` ROM data, M2 `mdf`-wrapped PSB assets and Squirrel scripts |
| `EBOOT.BIN` → plain ELF | **blocked** — NPDRM SELF, key revision 0x10; needs your own licence (see below) |
| PRX decryption | **blocked** — same, for both `libacc_neogeo_ps3` and `libemu_m68k_ps3` |
| Import / NID analysis | not started |
| Function boundary detection | not started |
| PPU lifting | not started |
| Build & link | not started |
| Boot | not started |

## The first gate: decryption

All three binaries are **NPDRM** SELFs at key revision `0x10`, sharing one
auth ID (`0x1010000001000003`). Unlike a disc SELF, an NPDRM binary is tied to a
licence — so decrypting these needs the RAP or klicensee that came with *your*
purchase, plus a firmware key set. Neither ships here, and neither should.

This is the same bring-your-own-keys model the other ports use; it is simply the
first step here rather than a footnote, because a PSN title cannot be analysed
at all until it is done.

Once a plain ELF exists, the pipeline is the usual one, and the two PRXs are
lifted alongside the EBOOT the way [flow](https://github.com/sp00nznet/flow)
lifts `libsre.prx`.

## Reproducing the inventory

Needs only your own copy of the package — no keys, nothing decrypted.

```bash
# Extract the PKG you purchased (ps3recomp's tool keeps the directory tree)
python ../ps3recomp/tools/pkg_extract.py your-metal-slug-2.pkg input

# What is in it, and what runs the game
python tools/inventory.py input
```

## Prerequisites

- Python 3.9+
- [ps3recomp](https://github.com/sp00nznet/ps3recomp) checked out at `../ps3recomp`
- CMake 3.20+, Ninja and LLVM/clang-cl 14+ — once there is something to build

## Layout

```
metalslug2/
├── README.md
├── LICENSE
├── tools/
│   └── inventory.py        # what the package is, read from your own copy
├── docs/
│   └── package-layout.md   # the full file census and format notes
├── input/                  # your extracted package (gitignored)
├── meta/                   # analysis output, regenerated (gitignored)
└── src/recomp/             # lifted C, regenerated (gitignored)
```

Everything derived from the game — the plain ELF, lifted C, analysis JSON, ROM
containers, assets — is generated from your own copy and stays out of the repo.

## Related

- **[ps3recomp](https://github.com/sp00nznet/ps3recomp)** — the PS3 HLE runtime this builds against
- **[simpsonsarcade-ps3](https://github.com/sp00nznet/simpsonsarcade-ps3)** — the other emulator-in-a-wrapper port, and playable
- **[vf5](https://github.com/sp00nznet/vf5)** — a clean disc title on the same pipeline

## Legal

No proprietary Sony or SNK code, ROM data, encryption keys, licences or
copyrighted assets are in this repository. It contains clean-room tooling only;
everything derived from the game is generated locally from a copy you supply.

Licensed under the [MIT License](LICENSE).
