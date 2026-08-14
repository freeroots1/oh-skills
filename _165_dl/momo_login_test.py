#!/usr/bin/env python3
"""momopro 完整登录: csrf+验证码"""
import urllib.request, http.cookiejar, ssl, io, re, sys, time
from PIL import Image

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://momopro.digiflowtech.com"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent", "Mozilla/5.0")]

def get_login_page():
    r = op.open(f"{BASE}/web/index.php?r=admin%2Fpassport%2Flogin", timeout=8)
    html = r.read().decode("utf-8","ignore")
    m = re.search(r'_csrf = "([^"]+)"', html)
    return m.group(1) if m else None

def get_captcha():
    r = op.open(f"{BASE}/web/index.php?r=admin%2Fpassport%2Fcaptcha", timeout=8)
    return r.read()

def ocr_captcha(data):
    """ASCII-based recognition for momopro 4-char captcha"""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w,h = img.size
    pix = list(img.getdata())
    def is_char(p):
        r,g,b = p
        return r < 80 and g < 120 and b > 120
    cols = [sum(1 for y in range(h) if is_char(pix[y*w+x])) for x in range(w)]
    segs = []
    in_seg = False
    for i,c in enumerate(cols):
        if c > 0 and not in_seg: start=i; in_seg=True
        elif c == 0 and in_seg: segs.append((start,i-1)); in_seg=False
    if in_seg: segs.append((start,w-1))
    if len(segs) != 4: return None
    # 返回每个字符的ASCII art供匹配
    chars = []
    for (s,e) in segs:
        art = []
        for y in range(h):
            row = "".join("#" if is_char(pix[y*w+x]) else "." for x in range(s,e+1))
            if "#" in row: art.append(row)
        chars.append("\n".join(art))
    return chars

def login(user, pwd, code, csrf):
    data = f"username={user}&password={pwd}&captcha_code={code}&_csrf={csrf}".encode()
    try:
        r = op.open(urllib.request.Request(f"{BASE}/web/index.php?r=admin%2Fpassport%2Flogin", data=data), timeout=8)
        body = r.read().decode("utf-8","ignore")
        return body
    except Exception as e:
        return f"ERR:{e}"

user = sys.argv[1] if len(sys.argv) > 1 else "admin"
pwd = sys.argv[2] if len(sys.argv) > 2 else "admin"

csrf = get_login_page()
print(f"csrf: {csrf[:30]}...", flush=True)
for i in range(5):
    cap = get_captcha()
    chars = ocr_captcha(cap)
    if not chars:
        print(f"[{i}] 段数不对", flush=True)
        continue
    # 打印字符ASCII
    print(f"[{i}] === 验证码字符 ===", flush=True)
    for j, art in enumerate(chars):
        print(f"--- char{j} ---", flush=True)
        print(art, flush=True)
    # 等用户输入(测试模式)
    break

# 用常见组合测试
for code in ["1234","abcd","GXHB","123456"]:
    body = login(user, pwd, code, csrf)
    print(f"code={code}: {body[:150]}", flush=True)
