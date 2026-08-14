import hashlib, sys

target = "2d9d5942943a1323"
count = 0

# New patterns from the website analysis
# Company: 腾龙公司 (Tenglong), 北京鸿盛嘉科技 (Beijing Hongshengjia Technology)
# Products: 色差仪 (colorimeter), 光泽度仪 (gloss meter), 光谱仪 (spectrometer), etc.

new_bases = [
    # Company name variations
    "tenglong", "tenglongkeji", "tenglonggongsi", "longteng", "tenglongkefu",
    "tl", "tenglongkj", "tenglong789", "tenglong2018", "tenglong2019",
    "tenglong2020", "tenglong2021", "tenglong2022", "tenglong2023",
    "tenglong2024", "tenglong2025", "tenglong2026",
    # Product names
    "sechayi", "colorimeter", "guangzedu", "glossmeter", "guangpuyi",
    "spectrometer", "shiyanshi", "laboratory", "yiqi", "instrument",
    "yibiao", "fenxiyiqi", "huaxueshi", "biose", "biaozhun",
    "guangpu", "kelin", "hunterlab",
    # Domain chars
    "bjhzsv", "hzsv", "bjhz", "hzsvcom",
    # Brand names in pinyin
    "tenglong", "hongshang", "hongsheng", "hongshangjia", "hongshengjia",
    "beijinghongshang", "beijinghongsheng",
    # Chinese common with domain
    "bjhzsv123", "bjhzsv2024", "bjhzsv2025", "bjhzsv2026",
    "bjhzsv888", "bjhzsv666",
    # Phone/work related  
    "19908888893", "1998888", "08888893",
    "kefu", "fuwu", "service", "customer",
    # More common Chinese company passwords
    "12345678", "123456789", "1234567890",
    "888888", "666666", "111111", "000000",
    "qwerty123", "qwerty12345",
    "admin888", "admin666",
    # Tenglong specific
    "tl888", "tl123", "tl2024", "tl2025",
    # Measurements
    "lab", "color", "gloss", "light", "spectra",
    "chroma", "chromatic", "illuminant",
    # Numbers
    "1990888", "1990888893",
]

for base in new_bases:
    # Try base alone
    md5 = hashlib.md5(base.encode()).hexdigest()
    if md5[8:24] == target:
        print(f"FOUND! Password: {base}")
        sys.exit(0)
    
    # Try with number suffixes
    for suf in ["", "1", "12", "123", "1234", "12345", "123456", "1234567", 
                "12345678", "!", "@", "#", "!@#", "@123", "#123", "!123",
                "2020", "2021", "2022", "2023", "2024", "2025", "2026",
                "01", "001", "000", "888", "666", "999",
                "2010", "2011", "2012", "2013", "2014", "2015", "2016",
                "2017", "2018", "2019", "2020",
                "admin", "bjhzsv", "tenglong"]:
        pwd = base + suf
        md5 = hashlib.md5(pwd.encode()).hexdigest()
        if md5[8:24] == target:
            print(f"FOUND! Password: {pwd}")
            sys.exit(0)
        # Also try capitalized
        pwd2 = base.capitalize() + suf
        md5 = hashlib.md5(pwd2.encode()).hexdigest()
        if md5[8:24] == target:
            print(f"FOUND! Password: {pwd2}")
            sys.exit(0)
        # Try uppercase
        pwd3 = base.upper() + suf
        md5 = hashlib.md5(pwd3.encode()).hexdigest()
        if md5[8:24] == target:
            print(f"FOUND! Password: {pwd3}")
            sys.exit(0)

# Try number sequences - maybe the password is just numbers
for length in range(4, 11):
    for start in range(0, 100, 10):
        for i in range(start, start + 10):
            pwd = str(i)
            if len(pwd) >= length:
                break
            # Pad to length
            pwd = str(i).zfill(length)
            md5 = hashlib.md5(pwd.encode()).hexdigest()
            if md5[8:24] == target:
                print(f"FOUND! Password: {pwd}")
                sys.exit(0)

# Try: phone-like patterns
for prefix in ["199", "188", "186", "138", "139", "158", "159", "150", "151", "152"]:
    for mid in range(0, 10000):
        pwd = prefix + str(mid).zfill(4) + str(mid % 10) * 4
        if len(pwd) == 11:
            md5 = hashlib.md5(pwd.encode()).hexdigest()
            if md5[8:24] == target:
                print(f"FOUND! Password: {pwd}")
                sys.exit(0)

# Try the found phone from website: 199-0888-8893
phone_variants = ["19908888893", "19908888893kf", "1998888", "08888893",
                  "199-0888-8893", "19908888893_password",
                  "19908888893admin"]
for pwd in phone_variants:
    md5 = hashlib.md5(pwd.encode()).hexdigest()
    if md5[8:24] == target:
        print(f"FOUND! Password: {pwd}")
        sys.exit(0)

print("Not found in v4 patterns", file=sys.stderr)
for test in ["tenglong", "bjhzsv", "hongshengjia", "sechayi", "hongshangjia"]:
    m = hashlib.md5(test.encode()).hexdigest()
    print(f"  {test}: {m[8:24]}")
