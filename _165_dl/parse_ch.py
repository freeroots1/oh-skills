#!/usr/bin/env python3
import re, sys

def parse_payloads(path):
    """从 tcpdump -XX 输出提取每个 TCP payload 的字节"""
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

def parse_clienthello(p):
    # 找 TLS record 起点
    idx = p.find(b'\x16\x03')
    if idx < 0:
        return None
    rec = p[idx:]
    if len(rec) < 5:
        return None
    rec_len = int.from_bytes(rec[3:5], 'big')
    hs = rec[5:]
    if len(hs) < 4:
        return None
    hs_type = hs[0]
    hs_len = int.from_bytes(hs[1:4], 'big')
    ch = hs[4:]
    if len(ch) < 35:
        return None
    ver = ch[:2]
    random = ch[2:34]
    sidlen = ch[34]
    sid = ch[35:35+sidlen] if sidlen else b''
    off = 35 + sidlen
    if len(ch) < off + 2:
        return None
    cslen = int.from_bytes(ch[off:off+2], 'big')
    ciphers = ch[off+2:off+2+cslen]
    off2 = off + 2 + cslen
    if len(ch) < off2 + 1:
        return None
    complen = ch[off2]
    off3 = off2 + 1 + complen
    # extensions
    if len(ch) < off3 + 2:
        return None
    extlen = int.from_bytes(ch[off3:off3+2], 'big')
    exts = ch[off3+2:off3+2+extlen]
    ext_list = []
    e = 0
    while e + 4 <= len(exts):
        et = int.from_bytes(exts[e:e+2], 'big')
        el = int.from_bytes(exts[e+2:e+4], 'big')
        ext_list.append((et, el))
        e += 4 + el
    return {
        'hs_type': hs_type, 'hs_len': hs_len, 'ver': ver.hex(),
        'sidlen': sidlen, 'sid_hex': sid.hex() if sid else '',
        'sid_ascii': sid.decode('latin1', 'replace'),
        'cipher_count': cslen // 2,
        'ext_count': len(ext_list),
        'ext_types': [hex(t) for t, _ in ext_list],
        'total': len(rec),
    }

payloads = parse_payloads(sys.argv[1])
print(f"total payloads: {len(payloads)}")
for i, p in enumerate(payloads):
    ch = parse_clienthello(p)
    if ch:
        print(f"--- payload {i} ({ch['total']}B) ---")
        for k, v in ch.items():
            print(f"  {k}: {v}")
