import pytesseract
from PIL import Image
import requests
import io
import base64

# Download captcha raw
session = requests.Session()
session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)

r = session.get("http://bjhzsv.com/main/inc/code.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
print(f"Captcha HTTP {r.status_code}, {len(r.content)} bytes")
print(f"Content-Type: {r.headers.get('Content-Type')}")
print(f"First 50 bytes hex: {r.content[:50].hex()}")

# Save raw
with open("/tmp/captcha_raw.bmp", "wb") as f:
    f.write(r.content)

# Open and examine
img = Image.open(io.BytesIO(r.content))
print(f"Image: mode={img.mode}, size={img.size}, format={img.format}")
print(f"Pixels:\n{list(img.getdata())}")

# Try different enlargement methods
for method_name, method in [("NEAREST", Image.NEAREST), ("BILINEAR", Image.BILINEAR), ("BICUBIC", Image.BICUBIC), ("LANCZOS", Image.LANCZOS)]:
    big = img.resize((400, 100), method)
    big.save(f"/tmp/captcha_{method_name}.png")
    
    # Try thresholds
    gray = big.convert('L')
    for threshold in [100, 120, 140, 160, 180, 200, 220]:
        bw = gray.point(lambda x, t=threshold: 0 if x < t else 255)
        text = pytesseract.image_to_string(bw, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
        clean = ''.join(c for c in text if c.isdigit())
        if 3 <= len(clean) <= 5:
            print(f"  {method_name} threshold={threshold}: {text!r} -> {clean!r}")

# Also try raw 10x
big10 = img.resize((400, 100), Image.NEAREST)
text10 = pytesseract.image_to_string(big10, config='--psm 8 --oem 3').strip()
print(f"\nNEAREST 10x no whitelist: {text10!r}")

# Try 7x to 70x19 as shown in HTML
big_html = img.resize((70, 19), Image.NEAREST)
text_html = pytesseract.image_to_string(big_html, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
clean_html = ''.join(c for c in text_html if c.isdigit())
print(f"HTML size 70x19 NEAREST: {text_html!r} -> {clean_html!r}")

# Try multi-page
for angle in [0, 90, 180, 270]:
    rotated = img.rotate(angle, expand=True)
    big_rot = rotated.resize((rotated.width * 10, rotated.height * 10), Image.NEAREST)
    text_rot = pytesseract.image_to_string(big_rot, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    clean_rot = ''.join(c for c in text_rot if c.isdigit())
    if clean_rot:
        print(f"Rotated {angle}: {text_rot!r} -> {clean_rot!r}")

print("\nBase64 of raw captcha:")
print(base64.b64encode(r.content).decode())
