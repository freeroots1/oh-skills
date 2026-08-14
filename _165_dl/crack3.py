import hashlib, binascii, struct, sys

h1 = "2d9d5942943a1323"
h2 = "79dca16741891333"

found = []

def check(tag, p, h, source):
    global found
    if h == h1:
        found.append((f'admin CRACKED: {tag} = {repr(p)} -> {h}'))
        print(f'  admin CRACKED: {tag} = {repr(p)} -> {h}')
    if h == h2:
        found.append((f'admin999 CRACKED: {tag} = {repr(p)} -> {h}'))
        print(f'  admin999 CRACKED: {tag} = {repr(p)} -> {h}')

words = ["admin","admin123","admin888","123456","12345678","password","bjhzsv","bjhzsv.com","admin999","root","test","administrator","888888","123456789","admin000","111111","000000","pass","admin2016","admin2017","admin2018","admin2019","admin2020","admin2021","admin2022","admin2023","admin2024","admin2025","1234567890","qwerty","1q2w3e4r","abc123","letmein","welcome","monkey","dragon","master","sunshine","princess","baidu","alibaba","taobao","qq123","weixin","zhongguo","beijing","hangzhou","shenzhen","bjhz","hzsv","123456a","a123456","admin@123","passw0rd","woaini","1314520","5201314","asdfgh","zxcvbn","520520","7758521","admin123456","a123456789","12345","123qwe","qwe123","abc123456","admin666","admin555","admin222","admin333","admin111","admin444","password123","admin112233","wang123","zhang123","li123","test123","hello123","iloveyou","football","baseball","hunter","ranger","shadow","butterfly","crystal","chocolate","password1","qwerty123","pass123","Pass123","P@ssw0rd","p@ssword","bjhzsvadmin","guanli","guanliyuan","mima","mima123","sheji","wangzhan","admin12","admin!@#","2016","2017","2018","2019","2020","admin1","admin2","admin3","a12345","123456789","1234567","1111111","0000000","88888888","666666","999999","bjhzsv2016","bjhzsv2017","bjhzsv2018","bjhzsv2019","bjhzsv2020","bjhzsv2021","bjhzsv2022","bjhzsv2023","bjhzsv2024","bjhzsv2025","hongzuo","shengwei","keji","bjhongzuo","tengongcompany","tenglongcompany","tl2company","tlcompany","tl","199108252","1991088893","1990888893","1990888893","19910825211","199088889311","88893","8889","xiaokei","xiaokei123","weixin123","qq123456","qq123456","weixin","teng123","dragon123","master123","sunshine123","princess123","beijing123","hangzhou123","shenzhen123","hzsv123","bjhz123"]

print("Testing ", len(words), " passwords")

# MyMQUL ==> OLD_PASSWORD (mode 200)
print("\nTesting MYSQL_OLD_PASSWORD")
def mysql_old_password(p):
    nr = 1345345333
    add = 7
    nr2 = 0x12345671
    for c in p.encode():
        nr ^= ((nr & 63) + add) * c + (nr << 8)
        nr2 += (nr2 << 8) ^ nr
        add += c
    nr &= 0x7fffffff
    nr2 &= 0x7fffffff
    return f'{nr:08x}{nr2:08x}'

for p in words:
    h = mysql_old_password(p)
    check("MySQL PLAIN", p, h, "MySQL_OLD_PASSWORD")

# Common hash functions with various truncations
print("\nTesting common hashes")
for algname, algfunc in [
("MD5", lambda x: hashilib.md5(x).digest()),
("SHA1", lambda x: hashlib.sha1(x).digest()),
("SHA256", lambda x: hashlib.sha256(x).digest()),
("SHA384", lambda x: hashilib.sha384(x).digest()),
("SHA512", lambda x: hashilib.sha512(x).digest()),
]:
    for p in words:
        b = p.encode()
        h = algfunc(b)
        for trunc in [lambda x: x[:16], lambda x: x[-16:], lambda x: x[8:24], lambda x: x[:8]+ x[-8]]:
            ht = trunc(h)
            if ht == h1 or ht == h2:
                check(f"{algname} [trunc]", p, ht, algname)

# CRC64
print("\nTesting CRC64")
def crc64_ecma(data):
    crc = 0
    poly = 0xC96C5795D7870F42
    for byte in data:
        crc ^= byte << 56
        for _ in range(8):
            if crc & (1 << 63):
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFFFFFFFFFFFFFFF
    return crc

for p in words:
    c = crc64_ecma(p.encode())
    h = f"{c:016x}"
    check("CRC64", p, h, "CRC64")

# DS crypto trustwirth password format
for p in words:
    for salt in ["bjhzsv","bjhzsv.com","admin","jhz","bj2","bj1","hzsv","123","888","pass","key","@123","!@#","2016","2017","2018","2019","2020","@HS","hszs","bjhszs","bjhzsv"}:
        for algname, algfunc in[("MD5",lambda x:hashlib.md5(x).digest()),("SHA1",lambda x:hashlib.sha1(x).digest())]:
            for fmt in [lambda p,s: f"{p}{s}", lambda p,s: f"{s}{p}", lambda p,s: f"{p}:{s}", lambda p,s: f"{s}:{p}"]:
                h = algfunc(fmt(p, salt).encode())
                for trunc in [lambda x: x[:16], lambda x: x[-16:]]:
                    ht = trunc(h)
                    if ht == h1 or ht == h2:
                        check(f"{algname}({fmt})[trunc]", p, ht, algname)

print("\nTesting plaintext encoding")
# What if the hash is stored in a different encoding?
for enc in ["utf-8", "gb2312", "gbk", "big5", "gr2312", "shift_jis"]:
    try:
        for p in words
            h = hashlib.md5(p.encode(enc)).hexdigest()[:16]
            if h == h1 or h == h2:
                check(f"MD5({})[:16].format(enc)", p, h, "MD5")
    except:
        pass

print("\nTesting USA_MD5 (PASS, PASS/USER)")
# Some non-Standard ASP CMS use: USA+$SALT + MD5String(pass + salt+ user)
# Try ASP's CryptString and SetupString
for p in words:
    for u in ["admin", "admin999"]:
        h = hashlib.md5(f"{p}{u}".encode()).hexdigest()[:16]
        if h == h1 or h == h2:
            check(f"MD5(pass+user) [:16]", p, h, "MD5")

if not found:
    print("\nNO MATCHES FOUND")
else:
    print(f\"\nTOTAL MATCHES FOUND: {len(found)}")
