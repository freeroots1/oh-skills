#!/usr/bin/env python3
"""ddddocr识别率对比测试"""
import urllib.request, http.cookiejar, ssl, ddddocr, cv2, numpy as np
from collections import Counter

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"
ocr = ddddocr.DdddOcr(show_ad=False)

for i in range(6):
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    raw = r.read()
    data = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    pix = img.reshape(-1,3)
    colors = Counter(map(tuple, pix))
    bg = np.array(colors.most_common(1)[0][0])
    cc = np.array(colors.most_common(2)[1][0])
    dist = np.abs(img.astype(int) - cc.astype(int)).sum(axis=2)
    mask = dist < 120
    code = ocr.classification(raw)
    print(f"=== 样本{i}: ddddocr=[{code}] ===")
    # 打印ASCII(只前25行)
    n = 0
    for y in range(0, h, 2):
        line = "".join("#" if mask[y,x] else "." for x in range(w))
        if "#" in line:
            print(line)
            n += 1
            if n >= 22: break
    print("")
