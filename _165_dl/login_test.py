import urllib.request, urllib.parse, io, os
from PIL import Image

# Step 1: Get captcha
req = urllib.request.Request("http://bjhzsv.com/main/inc/code.asp")
resp = urllib.request.urlopen(req, timeout=10)
captcha_data = resp.read()
# Save captcha
with open("/tmp/captcha.bmp", "wb") as f:
    f.write(captcha_data)
print(f"Captcha downloaded: {len(captcha_data)} bytes")

# Step 2: Try to read captcha with OCR
try:
    import pytesseract
    img = Image.open(io.BytesIO(captcha_data))
    text = pytesseract.image_to_string(img, config="--psm 8").strip()
    print(f"OCR result: {text}")
except:
    print("pytesseract not available")

# Step 3: Try to brute force login with session
import http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Try login with manual captcha
print("Will need manual captcha approach")
