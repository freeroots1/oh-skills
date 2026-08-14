#!/usr/bin/env python3
import re, sys

def parse_payloads(path):
    payloads = []
    cur = b''
    for ln in open(path, 'rb'):
        m = re.match(rb'\s*0x[0-9a-f]+:\s+((?:[0-9a-f]{2,4}\s+)+)', ln)
        if m:
            hexs = m.group(1).replace(b' ', b'')
            cur += bytes.fromhex(hexs.decode())
        else:
            if cur:
                payloads.append(cur)
                cur = b''
    if cur:
        payloads.append(cur)
    return payloads

def parse_ch(p):
    idx = p.find(b'\x16\x03')
    if idx < 0:
        return None
    rec = p[idx:]
    if len(rec) < 5:
        return None
    hs = rec[5:]
    if len(hs) < 4:
        return None
    ch = hs[4:]
    if len(ch) < 35:
        return None
    sidlen = ch[34]
    off = 35 + sidlen
    cslen = int.from_bytes(ch[off:off+2], 'big')
    off2 = off + 2 + cslen
    complen = ch[off2]
    off3 = off2 + 1 + complen
    extlen = int.from_bytes(ch[off3:off3+2], 'big')
    exts = ch[off3+2:off3+2+extlen]
    # parse key_share (0x33)
    ks = None
    e = 0
    groups = []
    while e + 4 <= len(exts):
        et = int.from_bytes(exts[e:e+2], 'big')
        el = int.from_bytes(exts[e+2:e+4], 'big')
        data = exts[e+4:e+4+el]
        if et == 0x33 and len(data) >= 2:
            total = int.from_bytes(data[:2], 'big')
            d = data[2:2+total]
            g = 0
            while g + 4 <= len(d):
                grp = int.from_bytes(d[g:g+2], 'big')
                klen = int.from_bytes(d[g+2:g+4], 'big')
                groups.append((hex(grp), klen))
                g += 4 + klen
        e += 4 + el
    return {'sidlen': sidlen, 'groups': groups, 'total': len(rec)}

for i, p in enumerate(parse_payloads(sys.argv[1])):
    r = parse_ch(p)
    if r and r['groups']:
        print(f"payload {i} ({r['total']}B) sidlen={r['sidlen']} key_share={r['groups']}")
