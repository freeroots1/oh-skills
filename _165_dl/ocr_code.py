from PIL import Image
import sys
idx = sys.argv[1]
img = Image.open(f"/tmp/code_{idx}.bmp")
px = list(img.getdata())
bg = (238,238,238)
colors = {}
for p in px:
    if isinstance(p, tuple) and p != bg and p not in colors:
        colors[p] = len(colors)
chars = {}
for c in colors:
    min_x, max_x = 40, 0
    for y in range(10):
        for x in range(40):
            p = px[y*40+x]
            v = p if isinstance(p, tuple) else (p,p,p)
            if v == c:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
    lines = []
    for y in range(10):
        line = ""
        for x in range(min_x, max_x+1):
            p = px[y*40+x]
            v = p if isinstance(p, tuple) else (p,p,p)
            line += "#" if v == c else " "
        lines.append(line)
    chars[min_x] = lines
print(f"--- Attempt {idx} ---")
for x in sorted(chars):
    print(f"Char at x={x}:")
    for l in chars[x]:
        print(f"  |{l}|")
