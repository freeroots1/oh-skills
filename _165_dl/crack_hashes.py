import hashlib, binascii

def mysql_old_password(password):
    nr = 1345345333
    add = 7
    nr2 = 0x12345671
    for c in password.encode():
        nr ^= (((nr & 63) + add) * c) + (nr << 8)
        nr2 += (nr2 << 8) ^ nr
        add += c
    nr &= 0x7fffffff
    nr2 &= 0x7fffffff
    return f"{nr:08x}{nr2:08x}"

h1 = "2d9d5942943a1323"
h2 = "79dca16741891333"

words = ["admin","admin123","admin888","123456","12345678","password","bjhzsv","bjhzsv.com","admin999","root","test","administrator","888888","123456789","admin000","111111","000000","pass","admin2016","admin2017","admin2018","admin2019","admin2020","admin2021","admin2022","admin2023","admin2024","admin2025","1234567890","qwerty","1q2w3e4r","abc123","letmein","welcome","monkey","dragon","master","sunshine","princess","baidu","alibaba","taobao","qq123","weixin","zhongguo","beijing","hangzhou","shenzhen","bjhz","hzsv","123456a","a123456","admin@123","passw0rd","woaini","1314520","5201314","asdfgh","zxcvbn","520520","7758521","wang123","zhang123","li123","admin123456","a123456789","12345","123qwe","qwe123","abc123456","admin666","admin777","admin555","admin222","admin333","admin111","admin444","password123","admin112233"]

print("=== MySQL OLD_PASSWORD ===")
for p in words:
    h = mysql_old_password(p)
    if h in (h1, h2):
        print(f"MATCH: {repr(p)} -> {h} (user: {admin if h==h1 else admin999})")

print("=== MD5[:16] ===")
for p in words:
    h = hashlib.md5(p.encode()).hexdigest()[:16]
    if h == h1: print(f"admin MATCH (MD5[:16]): {repr(p)}")
    if h == h2: print(f"admin999 MATCH (MD5[:16]): {repr(p)}")

print("=== Full MD5 ===")
for p in words:
    h = hashlib.md5(p.encode()).hexdigest()
    if h == h1: print(f"admin MATCH (MD5): {repr(p)}")
    if h == h2: print(f"admin999 MATCH (MD5): {repr(p)}")

print("=== SHA1[:16] ===")
for p in words:
    h = hashlib.sha1(p.encode()).hexdigest()[:16]
    if h == h1: print(f"admin MATCH (SHA1[:16]): {repr(p)}")
    if h == h2: print(f"admin999 MATCH (SHA1[:16]): {repr(p)}")

print("=== CRC32 ===")
for p in words:
    crc = f"{binascii.crc32(p.encode())&0xffffffff:08x}"
    if crc == h1: print(f"admin MATCH (CRC32): {repr(p)}")
    if crc == h2: print(f"admin999 MATCH (CRC32): {repr(p)}")

print("=== MD5(MD5(x))[:16] ===")
for p in words:
    h = hashlib.md5(hashlib.md5(p.encode()).hexdigest().encode()).hexdigest()[:16]
    if h == h1: print(f"admin MATCH (MD5(MD5)[:16]): {repr(p)}")
    if h == h2: print(f"admin999 MATCH (MD5(MD5)[:16]): {repr(p)}")

print("=== SHA256[:16] ===")
for p in words:
    h = hashlib.sha256(p.encode()).hexdigest()[:16]
    if h == h1: print(f"admin MATCH (SHA256[:16]): {repr(p)}")
    if h == h2: print(f"admin999 MATCH (SHA256[:16]): {repr(p)}")

print("Done.")
