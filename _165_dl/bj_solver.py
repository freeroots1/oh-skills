from PIL import Image
from collections import Counter
import subprocess, sys

# Known digit patterns for the 40x10 colored captcha at bjhzsv.com
# Digits 0-9 mapped to 5x9 grid patterns
TEMPLATES = {
    "0": [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(1,0),(1,8),(2,0),(2,8),(3,0),(3,8),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7)],
    "1": [(2,0),(1,1),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(0,8),(1,8),(2,8),(3,8),(4,8)],
    "2": [(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(3,2),(2,3),(1,4),(0,5),(0,6),(0,7),(0,8),(1,8),(2,8),(3,8),(4,8)],
    "3": [(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(4,2),(2,3),(3,3),(4,3),(4,4),(4,5),(4,6),(4,7),(0,8),(1,8),(2,8),(3,8)],
    "4": [(3,0),(2,1),(3,1),(1,2),(3,2),(0,3),(3,3),(0,4),(1,4),(2,4),(3,4),(4,4),(3,5),(3,6),(3,7),(3,8)],
    "5": [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(4,3),(4,4),(4,5),(4,6),(4,7),(0,8),(1,8),(2,8),(3,8)],
    "6": [(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4),(0,5),(4,5),(0,6),(4,6),(0,7),(4,7),(1,8),(2,8),(3,8)],
    "7": [(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(3,2),(2,3),(2,4),(1,5),(1,6),(0,7)],
    "8": [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(1,3),(2,3),(3,3),(0,4),(4,4),(0,5),(4,5),(0,6),(4,6),(0,7),(4,7),(1,8),(2,8),(3,8)],
    "9": [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(1,3),(2,3),(3,3),(4,3),(4,4),(4,5),(4,6),(4,7),(0,8),(1,8),(2,8),(3,8)],
}

def match_digit(positions):
    """Match a set of pixel positions against digit templates"""
    # Scale positions to 5x9 grid
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    dw, dh = max_x-min_x+1, max_y-min_y+1
    
    scaled = set()
    for x, y in positions:
        sx = int(round((x - min_x) * 4.0 / max(1, dw-1)))
        sy = int(round((y - min_y) * 8.0 / max(1, dh-1)))
        scaled.add((sx, sy))
    
    best_digit = "?"
    best_score = 0
    for digit, template in TEMPLATES.items():
        tset = set(template)
        matches = len(scaled & tset)
        total = max(len(scaled), len(tset))
        score = matches / total if total > 0 else 0
        if score > best_score:
            best_score = score
            best_digit = digit
    return best_digit, best_score

def solve():
    """Download captcha and OCR it"""
    subprocess.run(["curl", "-sk", "-c", "/tmp/bj_sess.txt", 
        "http://bjhzsv.com/main/", "-o", "/dev/null"], timeout=5)
    subprocess.run(["curl", "-sk", "-b", "/tmp/bj_sess.txt",
        "http://bjhzsv.com/main/inc/code.asp", "-o", "/tmp/bj_captcha.png"], timeout=5)
    
    img = Image.open("/tmp/bj_captcha.png")
    pixels = list(img.getdata())
    w = img.size[0]
    colors = Counter(pixels)
    bg = colors.most_common(1)[0][0]
    digit_colors = [c for c in colors if c != bg]
    digit_colors.sort(key=lambda c: min(i % w for i, p in enumerate(pixels) if p == c))
    
    result = ""
    for color in digit_colors:
        positions = [(i % w, i // w) for i, p in enumerate(pixels) if p == color]
        digit, score = match_digit(positions)
        result += digit
    
    return result

if __name__ == "__main__":
    for i in range(3):
        code = solve()
        print(f"Captcha {i+1}: {code}")
