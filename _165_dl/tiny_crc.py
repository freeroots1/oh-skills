import hashlib, binascii, sys
TARGETS = {"admin": "2d9d5942943a1323", "admin999": "79dca16741891333"}
def crc64_ecma(d):
 c=0;p=0xC96C5795D7870F42
 if isinstance(d,str): d=d.encode()
 for b in d:
  c^=(b<<56)
  for _ in range(8):
   if c&(1<<63): c=(c<<1)^p
   else: c<<=1
   c&=0xFFFFFFFFFFFFFFFF
 return format(c,"016x")
print("CRC64-ECMA admin:", crc64_ecma("admin"))
print("CRC64-ECMA admin999:", crc64_ecma("admin999"))
