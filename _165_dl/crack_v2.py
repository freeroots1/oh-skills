#!/usr/bin/env python3
import hashlib, binascii, sys

T = {"admin":"2d9d5942943a1323","admin999":"79dca16741891333"}
def crc64_e(d):
 c=0;p=0xC96C5795D7870F42
 if isinstance(d,str): d=d.encode()
 for b in d:
  c^=(b<<56)
  for _ in range(8):
   if c&(1<<63): c=(c<<1)^p
   else: c<<=1
   c&=0xFFFFFFFFFFFFFFFF
 return format(c,"016x")
def crc64_w(d):
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
def sdbm(d):
 h=0
 if isinstance(d,str): d=d.encode()
 for b in d: h=(h<<6)+(h<<16)-h+b;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def fnv1(d):
 h=0xCBF29CE484222325
 if isinstance(d,str): d=d.encode()
 for b in d: h^=b;h*=0x100000001B3;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def fnv1a(d):
 h=0xCBF29CE484222325
 if isinstance(d,str): d=d.encode()
 for b in d: h^=b;h*=0x100000001B3;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def loselose(d):
 h=0
 if isinstance(d,str): d=d.encode()
 for b in d: h+=b;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def pw_hx(d): return binascii.hexlify(d.encode()).decode()
def xor80(d): return binascii.hexlify(bytes(b^0x80 for b in d.encode())).decode()
def xorff(d): return binascii.hexlify(bytes(b^0xff for b in d.encode())).decode()
def md5_16(d): return hashlib.md5(d.encode()).hexdigest()[:16]
def sha1_16(d): return hashlib.sha1(d.encode()).hexdigest()[:16]
def sha256_16(d): return hashlib.sha256(d.encode()).hexdigest()[:16]
def crc32_p(d): return format(binascii.crc32(d.encode())&0xFFFFFFFF,"016x")
def adler32_p(d): return format(binascii.adler32(d.encode())&0xFFFFFFFF,"016x")
def sum_b(d): return format(sum(d.encode()),"016x")
def utf16le(d): return binascii.hexlify(d.encode("utf-16-le")).decode()
def utf16be(d): return binascii.hexlify(d.encode("utf-16-be")).decode()
def rev_hx(d): return binascii.hexlify(d.encode()[::-1]).decode()
def asc_hx(d): return "".join(format(ord(c),"02x") for c in d)
def asc_str(d): return "".join(str(ord(c)) for c in d)
def bp_h(d):
 h=0
 if isinstance(d,str): d=d.encode()
 for b in d: h=(h*7)^b;h&=0xFFFFFFFFFFFFFFFF
 return format(h,"016x")
def xor_s(d):
 h=0
 if isinstance(d,str): d=d.encode()
 for b in d: h^=b
 return format(h,"016x")
HF = [
 ("CRC64-E",crc64_e),("CRC64-W",crc64_w),("DJB2",djb2),("SDBM",sdbm),
 ("FNV1",fnv1),("FNV1a",fnv1a),("Sum",loselose),("Hex",pw_hx),
 ("XOR80",xor80),("XORFF",xorff),("MD5",md5_16),("SHA1",sha1_16),
 ("SHA256",sha256_16),("CRC32",crc32_p),("Adler32",adler32_p),
 ("SumBytes",sum_b),("UTF16LE",utf16le),("UTF16BE",utf16be),
 ("RevHex",rev_hx),("AscHex",asc_hx),("AscStr",asc_str),
 ("BP",bp_h),("XORs",xor_s)
]
PW = set()
for f in ["/tmp/bj_pass.txt","/tmp/bj_uniq.txt","/tmp/pass_big.txt","/tmp/pass.txt",
 "/tmp/bj_admin.txt","/tmp/bj_admin123.txt","/tmp/bj_admin888.txt",
 "/tmp/bj_admin999.txt","/tmp/bj_bjhzsv.txt","/tmp/bj_123456.txt"]:
 try:
  with open(f) as fh:
   for ln in fh:
    p=ln.strip()
    if p and not p.startswith("#"): PW.add(p)
 except: pass
EX = ["","admin","Admin","ADMIN","administrator","Administrator",
 "admin999","Admin999","ADMIN999","admin888","admin123","admin666",
 "bjhzsv","BJZHSV","bjhzsv.com","bjhzsv123","bjhzsv2011","bjhzsv888",
 "hzsv","hzsv123","hzsv2011","hzsv888",
 "35080508","35080508123","350805082011","35080508888",
 "62489782","62489782123","624897822011","62489782888",
 "hongzuo","hongzuo123","hongzuo2011","hongzuo888",
 "shengwei","shengwei123","shengwei2011","shengwei888",
 "hermes","Hermes","HERMES","password","Password","PASSWORD",
 "passw0rd","P@ssw0rd","letmein","welcome","login",
 "root","Root","ROOT","test","Test","TEST","master","Master",
 "123456","12345678","123456789","1234567890","111111","000000",
 "asdfgh","qwerty","Qwerty","QWERTY","abc123","pass123","admin@123",
 "admin2012","admin2013","admin2014","admin2015","admin2016",
 "admin2017","admin2018","admin2019","admin2020","admin2021","admin2022",
 "admin2023","admin2024","admin2025",
 "sa","dbadmin","sysadmin","super","Super",
 "!QAZ2wsx","1qaz2wsx","zaq12wsx",
 "cnkuai","CNKuai","cnkuai123","CNKuai123","cnkuai2016","CNKuai2016",
 "cnkuai888","CNKuai888","cnkuai@123","CNKuai@123",
 "tjzr","TJZR","tjzr123","TJZR123","tjzr2016","TJZR2016","tjzr888","TJZR888",
 "zhuiri","ZhuiRi","zhuiri123","ZhuiRi123","zhuiri2016","ZhuiRi2016",
 "zhuiri888","ZhuiRi888",
 "Server2016","Server2019","Server2020","Server2022","Server2024","Server2025",
 "Win2016","Win2019","Win2020","Win2022",
 "Windows2016","Windows2019","Windows2020","Windows2022",
 "8LRG32Q4EGA","WIN-8LRG32Q4EGA","WIN8LRG32Q4EGA",
 "13681449049","01062489782",
 "Aa123456","Admin123","password1","Password1",
 "bjhzsv2011","bjhzsv888",
 "35080508123","62489782123"]
for e in EX:
 PW.add(e);PW.add(e.upper());PW.add(e.lower());PW.add(e.capitalize())
 if e: PW.add(e[::-1])
print("Loaded",len(PW),"passwords,",len(HF),"hashes",file=sys.stderr)
found=False
for fn,f in HF:
 for pw in sorted(PW):
  try:
   r=f(pw)
   if r and len(r)>=16:
    r=r[:16].lower()
    for u,t in T.items():
     if r==t:
      print("MATCH [] for fn,f in HF:
 for pw in sorted(PW):
  try:
   r=f(pw)
   if r and len(r)>=16:
    r=r[:16].lower()
    for u,t in T.items():
     if r==t:
      import sys; sys.stdout.write("MATCH [%s] %s -> %s (%s)\n" % (fn,repr(pw),r,u))
      found=True
  except: pass
if not found:
 import sys
 sys.stderr.write("No matches found\n")
else:
 import sys; sys.stderr.write("Matches found!\n")
import sys; sys.stderr.write("Done\n")
