import hashlib, binascii, sys
T={"admin":"2d9d5942943a1323","admin999":"79dca16741891333"}
def crc64_we(d):
 c=0xFFFFFFFFFFFFFFFF;p=0x42F0E1EBA9EA3693
 if isinstance(d,str): d=d.encode()
 for b in d:
  c^=b
  for _ in range(8):
   if c&1: c=(c>>1)^p
   else: c>>=1
 c^=0xFFFFFFFFFFFFFFFF
 return format(c,"016x")
def djb2(d):
 h=5381
 if isinstance(d,str): d=d.encode()
 for b in d: h=((h<<5)+h)+b;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def fnv1a(d):
 h=0xCBF29CE484222325
 if isinstance(d,str): d=d.encode()
 for b in d: h^=b;h*=0x100000001B3;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def pw_hex(d): return binascii.hexlify(d.encode()).decode()
def md5_16(d): return hashlib.md5(d.encode()).hexdigest()[:16]
def sha1_16(d): return hashlib.sha1(d.encode()).hexdigest()[:16]
def crc32_p(d): return format(binascii.crc32(d.encode())&0xFFFFFFFF,"016x")
def utf16le(d): return binascii.hexlify(d.encode("utf-16-le")).decode()
def rev_hex(d): return binascii.hexlify(d.encode()[::-1]).decode()
def asc_hx(d): return ''.join(format(ord(c),'02x') for c in d)
def xor80(d): return binascii.hexlify(bytes(b^0x80 for b in d.encode())).decode()
def xorff(d): return binascii.hexlify(bytes(b^0xff for b in d.encode())).decode()
for p in ["admin","admin999","","bjhzsv","123456","password","admin888","35080508","!QAZ2wsx","01062489782","13681449049","62489782","hongzuo","shengwei","hzsv2011","cnkuai","tjzr","zhuiri","hzsv","Server2016","8LRG32Q4EGA","Administrator","administrator","ADMIN","HZSV","BJZHSV","WIN-8LRG32Q4EGA","1qaz2wsx"]:
 for n,f in [("CRC64-WE",crc64_we),("DJB2",djb2),("FNV1a",fnv1a),("Hex",pw_hex),("MD5_16",md5_16),("SHA1_16",sha1_16),("CRC32",crc32_p),("UTF16LE",utf16le),("RevHex",rev_hex),("AscHex",asc_hx),("XOR80",xor80),("XORFF",xorff)]:
  try:
   r=f(p)
   if r and len(r)>=16: r=r[:16].lower()
   else: continue
   for u,t in T.items():
    if r==t: print("MATCH [%s] %r -> %s (%s)" % (n,p,r,u))
  except: pass
print("Basic test done")
