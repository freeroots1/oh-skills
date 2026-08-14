import pytesseract
from PIL import Image, ImageFilter, ImageOps
import requests
import io
import re

# Download captcha
session = requests.Session()
session.get("http://bjhzsv.com/main/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
r = session.get("http://bjhzsv.com/main/inc/code.asp", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
img = Image.open(io.BytesIO(r.content))
pixels = img.load()
w, h = img.size

# Print ASCII art showing the different colors
print("Captcha pixel ASCII art (R,G,B) - markers for different colors:")
color_map = {}
color_idx = 0
for y in range(h):
    row = ""
    for x in range(w):
        px = pixels[x, y]
        if px == (238, 238, 238):
            row += "."
        elif px not in color_map:
            color_map[px] = str(color_idx)
            color_idx += 1
            row += color_map[px]
        else:
            row += color_map[px]
    print(f"  {row}")

print(f"\nColor mapping:")
for c, idx in color_map.items():
    print(f"  {idx}: RGB{c}")

# Now try to identify each digit by color separation + more aggressive preprocessing
gray = img.convert('L')
print(f"\nGrayscale values (0-255):")
for y in range(h):
    row_vals = []
    for x in range(w):
        row_vals.append(str(gray.getpixel((x, y))).rjust(3))
    print(f"  {' '.join(row_vals)}")

# Threshold to separate foreground from background
# Background is 238, digits are darker
bw = gray.point(lambda x: 0 if x < 220 else 255)

print(f"\nBinary (threshold 220):")
for y in range(h):
    row = ""
    for x in range(w):
        row += "0" if bw.getpixel((x, y)) == 0 else "."
    print(f"  {row}")

# Save enlarged versions
big_nearest = img.resize((400, 100), Image.NEAREST)
big_nearest.save("/tmp/captcha_nearest.png")

big_bil = img.resize((400, 100), Image.BILINEAR)
big_bil.save("/tmp/captcha_bilinear.png")

# Try different binarizations of nearest-neighbor enlarged image
for thresh in [180, 200, 220]:
    big_bw = big_nearest.convert('L').point(lambda x: 0 if x < thresh else 255)
    big_bw.save(f"/tmp/captcha_thresh_{thresh}.png")
    
    # OCR on binarized
    text = pytesseract.image_to_string(big_bw, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    clean = ''.join(c for c in text if c.isdigit())
    print(f"\nThreshold {thresh}: OCR={text!r} clean={clean!r}")

# Try with some dilation/erosion
from PIL import ImageFilter
big_bw = big_nearest.convert('L').point(lambda x: 0 if x < 200 else 255)
# Dilate to make digits thicker
dilated = big_bw.filter(ImageFilter.MaxFilter(3))
dilated.save("/tmp/captcha_dilated.png")
text = pytesseract.image_to_string(dilated, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
clean = ''.join(c for c in text if c.isdigit())
print(f"\nDilated (MaxFilter 3): OCR={text!r} clean={clean!r}")

# Erode
eroded = big_bw.filter(ImageFilter.MinFilter(3))
text = pytesseract.image_to_string(eroded, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
clean = ''.join(c for c in text if c.isdigit())
print(f"Eroded (MinFilter 3): OCR={text!r} clean={clean!r}")

# Try with box blur
blurred = big_bil.filter(ImageFilter.BoxBlur(1))
text = pytesseract.image_to_string(blurred, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
clean = ''.join(c for c in text if c.isdigit())
print(f"BoxBlur(1): OCR={text!r} clean={clean!r}")

# Try adaptive threshold or just using the original image with --psm 6 (uniform block)
text = pytesseract.image_to_string(big_nearest, config='--psm 6 --oem 3').strip()
print(f"\nPSM 6 (no whitelist): {text!r}")

# Let's try extracting each digit by column ranges
# Find bounding boxes of non-white pixels in binarized image
bw_small = gray.point(lambda x: 0 if x < 220 else 255)
found_any = False
in_digit = False
digit_starts = []
for x in range(w):
    has_dark = any(bw_small.getpixel((x, y)) == 0 for y in range(h))
    if has_dark and not in_digit:
        digit_starts.append(x)
        in_digit = True
    elif not has_dark and in_digit:
        digit_starts.append(x - 1)
        in_digit = False
if in_digit:
    digit_starts.append(w - 1)

print(f"\nDigit column ranges: {digit_starts}")
# Pair them up
if len(digit_starts) >= 2:
    for i in range(0, len(digit_starts) - 1, 2):
        x1, x2 = digit_starts[i], digit_starts[i+1]
        print(f"  Digit {i//2}: columns {x1}-{x2}")
        for y in range(h):
            row = ""
            for x in range(x1, x2+1):
                row += "0" if bw_small.getpixel((x, y)) == 0 else "."
            print(f"    {row}")
