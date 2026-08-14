import sys
from PIL import Image

path = "/tmp/_captcha.bmp"
img = Image.open(path)
px = list(img.getdata())
bg = (238,238,238)
w,h = 40,10

colors = {}
for p in px:
    if isinstance(p,tuple) and p != bg and p not in colors:
        colors[p] = len(colors)

print("Colors found:", len(colors))
print("Image size:", w, "x", h)

for c in sorted(colors.keys()):
    min_x, max_x = w, 0
    min_y, max_y = h, 0
    for y in range(h):
        for x in range(w):
            p = px[y*w+x]
            v = p if isinstance(p,tuple) else (p,p,p)
            if v == c:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
    
    print("\nColor", colors[c], "x=", min_x, "-", max_x, "y=", min_y, "-", max_y)
    for y2 in range(min_y, max_y+1):
        line = ""
        for x2 in range(min_x, max_x+1):
            p = px[y2*w+x2]
            v = p if isinstance(p,tuple) else (p,p,p)
            line += "#" if v == c else "."
        print("  " + line)

print("\n\nPer-column content:")
for x in range(w):
    cols = []
    for y in range(h):
        p = px[y*w+x]
        v = p if isinstance(p,tuple) else (p,p,p)
        cols.append("#" if v != bg else ".")
    print("x=" + str(x).rjust(2) + ": " + "".join(cols))
