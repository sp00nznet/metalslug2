#!/usr/bin/env python3
"""Inventory a NEOGEO STATION package: what it is, and what runs the game.

Reads an extracted PKG tree and reports PARAM.SFO, the SCE binaries and their
SELF types, the container formats, and a file census.  Everything it prints is
read from YOUR copy -- this script ships no game data and no keys.

    python tools/inventory.py input/

The point it exists to make: this title is a shell plus an emulator, not a
game.  The shell boots, the emulator PRXs run a Neo Geo, and the ROM lives in
a .ccf container beside them.  See docs/package-layout.md.
"""
import os, struct, sys, collections

SELF_TYPES = {1: 'LV0', 2: 'LV1', 3: 'LV2', 4: 'APP', 5: 'ISO', 6: 'LDR', 8: 'NPDRM'}
MAGICS = {
    b'SCE\0': 'encrypted SCE binary (SELF/SPRX)',
    b'CCF\0': 'CCF container (Neo Geo ROM data)',
    b'mdf\0': 'M2 "mdf" wrapper (PSB asset or Squirrel script)',
    b'RIFF':  'RIFF/AT3 audio',
    b'\x7fELF': 'plain ELF',
}


def read_sfo(path):
    """PARAM.SFO is length-prefixed, so `strings` misses most of it."""
    d = open(path, 'rb').read()
    if d[:4] != b'\0PSF':
        return []
    _, _, key_off, data_off, n = struct.unpack('<IIIII', d[:20])
    out = []
    for i in range(n):
        ko, fmt, ln, _mx, do = struct.unpack('<HHIII', d[20 + i * 16:36 + i * 16])
        key = d[key_off + ko:d.index(b'\0', key_off + ko)].decode('ascii', 'replace')
        raw = d[data_off + do:data_off + do + ln]
        val = struct.unpack('<I', raw[:4])[0] if fmt == 0x0404 else \
              raw.split(b'\0')[0].decode('utf-8', 'replace')
        out.append((key, val))
    return out


def sce_info(path):
    """Key revision and SELF type out of an SCE header, without decrypting it."""
    d = open(path, 'rb').read(0x200)
    if d[:4] != b'SCE\0' or len(d) < 0x88:
        return None
    keyrev = struct.unpack('>H', d[8:10])[0]
    authid, _vendor, stype, _ver = struct.unpack('>QIIQ', d[0x70:0x88])
    return keyrev, SELF_TYPES.get(stype, str(stype)), authid


def magic_of(path):
    with open(path, 'rb') as f:
        head = f.read(4)
    return MAGICS.get(head, MAGICS.get(head[:4]))


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'input'
    if not os.path.isdir(root):
        sys.exit('usage: inventory.py <extracted-pkg-dir>   (e.g. input/)')

    sfo = os.path.join(root, 'PARAM.SFO')
    if os.path.exists(sfo):
        print('== PARAM.SFO')
        for k, v in read_sfo(sfo):
            print('   %-20s %s' % (k, str(v).replace('\n', ' / ')))

    print('\n== SCE binaries (what actually executes)')
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            info = sce_info(p)
            if info:
                keyrev, stype, authid = info
                print('   %-28s %9d B  keyrev=0x%04X  %s  authid=0x%016X'
                      % (fn, os.path.getsize(p), keyrev, stype, authid))

    print('\n== Container formats')
    kinds = collections.Counter()
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            k = magic_of(os.path.join(dirpath, fn))
            if k:
                kinds[k] += 1
    for k, n in kinds.most_common():
        print('   %4d  %s' % (n, k))

    print('\n== Largest files')
    sizes = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            p = os.path.join(dirpath, fn)
            sizes.append((os.path.getsize(p), os.path.relpath(p, root)))
    for n, rel in sorted(sizes, reverse=True)[:12]:
        print('   %10d  %s' % (n, rel.replace(os.sep, '/')))
    print('\n   %d files total' % len(sizes))


if __name__ == '__main__':
    main()
