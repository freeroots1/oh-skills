#!/usr/bin/env python3
"""连通域法分割验证码"""
import urllib.request, http.cookiejar, ssl, cv2, numpy as np
from collections import Counter

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"

def get_mask(img):
    h, w = img.shape[:2]
    pix = img.reshape(-1, 3)
    colors = Counter(map(tuple, pix))
    bg = np.array(colors.most_common(1)[0][0])
    char_color = np.array(colors.most_common(2)[1][0]) if len(colors) > 1 else None
    if char_color is None: return None
    dist = np.abs(img.astype(int) - char_color.astype(int)).sum(axis=2)
    mask = (dist < 120).astype(np.uint8) * 255
    return mask

def get_components(mask):
    """连通域分析, 过滤干扰线"""
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    comps = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        # 字符特征: 高>15, 宽<60(排除横贯干扰线), 面积合适
        if h > 12 and h < 55 and w < 70 and area > 40:
            comps.append((x, y, w, h))
    comps.sort()
    return comps

ok = 0
for i in range(15):
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    data = np.frombuffer(r.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None: continue
    mask = get_mask(img)
    if mask is None: continue
    comps = get_components(mask)
    print(f"{i}: 组件={[(x,w,h) for x,y,w,h in comps]}")
    if len(comps) == 4: ok += 1
print(f"4段成功: {ok}/15")
