#!/usr/bin/env python3
"""momopro 验证码自动识别+登录"""
import urllib.request, http.cookiejar, ssl, io, time, sys
from PIL import Image

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://momopro.digiflowtech.com"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent", "Mozilla/5.0")]

# 字符模板: 每字符的列模式(基于120x50验证码,字符高约32px)
# 列高度模式: 每列字符像素数
TEMPLATES = {}

def get_captcha():
    r = op.open(f"{BASE}/web/index.php?r=admin%2Fpassport%2Fcaptcha", timeout=8)
    return r.read()

def analyze(data):
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w,h = img.size
    pix = list(img.getdata())
    def is_char(p):
        r,g,b = p
        return r < 80 and g < 120 and b > 120
    cols = [sum(1 for y in range(h) if is_char(pix[y*w+x])) for x in range(w)]
    # 分段
    segs = []
    in_seg = False
    for i,c in enumerate(cols):
        if c > 0 and not in_seg: start=i; in_seg=True
        elif c == 0 and in_seg: segs.append((start,i-1)); in_seg=False
    if in_seg: segs.append((start,w-1))
    return cols, segs, img, is_char, w, h

def match_char(img, is_char, seg, w, h):
    """提取字符的列高度模式, 与模板匹配"""
    s,e = seg
    pattern = []
    for x in range(s, e+1):
        cnt = sum(1 for y in range(h) if is_char(img.getpixel((x,y))))
        pattern.append(cnt)
    # 归一化
    maxv = max(pattern) if pattern else 1
    norm = [round(c/maxv*10) for c in pattern]
    return norm

def main():
    user = sys.argv[1] if len(sys.argv) > 1 else "admin"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "admin"
    op.open(f"{BASE}/web/index.php?r=admin%2Fpassport%2Flogin", timeout=8)
    for i in range(30):
        cap = get_captcha()
        cols, segs, img, is_char, w, h = analyze(cap)
        if len(segs) != 4:
            print(f"[{i}] segments={len(segs)}", flush=True)
            continue
        # 打印ASCII供参考(第一轮)
        if i == 0:
            for y in range(0,h,3):
                line = "".join("#" if is_char(img.getpixel((x,y))) else "." for x in range(w))
                print(line, flush=True)
        # 识别: 打印列模式
        pats = []
        for seg in segs:
            pats.append(match_char(img, is_char, seg, w, h))
        print(f"[{i}] segs={segs} patterns={pats}", flush=True)
        # 尝试登录(先试常见组合)
        for code_guess in ["GXHB","1234","abcd"]:
            data = f"username={user}&password={pwd}&captcha_code={code_guess}".encode()
            try:
                r = op.open(urllib.request.Request(f"{BASE}/web/index.php?r=admin%2Fpassport%2Flogin", data=data), timeout=8)
                body = r.read().decode("utf-8","ignore")
                if "验证码" not in body and "captcha" not in body.lower() and len(body) > 100:
                    print(f"[{i}] code={code_guess} -> {body[:200]}", flush=True)
                else:
                    print(f"[{i}] code={code_guess} 验证码错", flush=True)
            except Exception as e:
                print(f"[{i}] ERR {str(e)[:60]}", flush=True)
        time.sleep(0.5)
    print("DONE")

if __name__ == "__main__":
    main()
