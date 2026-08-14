#!/usr/bin/env python3
"""测试验证码分割"""
import urllib.request, http.cookiejar, ssl, cv2, numpy as np

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"

for i in range(8):
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    data = np.frombuffer(r.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        print(f"{i}: decode fail"); continue
    target = np.array([25, 42, 128])
    mask = cv2.inRange(img, target-70, target+70)
    kh = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kh)
    kd = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.dilate(mask, kd, iterations=2)
    col_sum = mask.sum(axis=0)
    segs=[]; in_seg=False
    for x,c in enumerate(col_sum):
        if c>3 and not in_seg: start=x; in_seg=True
        elif c<=3 and in_seg:
            if x-start>=6: segs.append((start,x-1))
            in_seg=False
    if in_seg and len(col_sum)-start>=6: segs.append((start,len(col_sum)-1))
    print(f"{i}: 原像素={cv2.countNonZero(cv2.inRange(img, target-70, target+70))} 段={segs}")
