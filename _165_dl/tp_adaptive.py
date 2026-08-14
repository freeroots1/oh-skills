#!/usr/bin/env python3
"""自适应颜色验证码分割"""
import urllib.request, http.cookiejar, ssl, cv2, numpy as np
from collections import Counter

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"

def get_mask_adaptive(img):
    h, w = img.shape[:2]
    pix = img.reshape(-1, 3)
    colors = Counter(map(tuple, pix))
    # 背景是数量最多的颜色
    bg = np.array(colors.most_common(1)[0][0])
    # 找非背景的主要颜色(字符色) - 数量第2多的
    char_color = np.array(colors.most_common(2)[1][0]) if len(colors) > 1 else None
    if char_color is None: return None
    dist = np.abs(img.astype(int) - char_color.astype(int)).sum(axis=2)
    mask = (dist < 120).astype(np.uint8) * 255
    # 形态学
    kh = cv2.getStructuringElement(cv2.MORPH_RECT, (1,4))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kh)
    kd = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.dilate(mask, kd, iterations=2)
    return mask

for i in range(10):
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    data = np.frombuffer(r.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None: continue
    mask = get_mask_adaptive(img)
    if mask is None: 
        print(f"{i}: 无字符色"); continue
    col_sum = mask.sum(axis=0)
    segs=[]; in_seg=False
    for x,c in enumerate(col_sum):
        if c>3 and not in_seg: start=x; in_seg=True
        elif c<=3 and in_seg:
            if x-start>=6: segs.append((start,x-1))
            in_seg=False
    if in_seg and len(col_sum)-start>=6: segs.append((start,len(col_sum)-1))
    print(f"{i}: 段={segs}")
