from PIL import Image
import subprocess, sys

def solve():
    img = Image.open("/tmp/fresh.bmp")
    px = list(img.getdata())
    bg = (238,238,238)
    w, h = 40, 10

    colors = {}
    for p in px:
        if isinstance(p, tuple) and p != bg and p not in colors:
            colors[p] = len(colors)

    output = []
    for c in sorted(colors.keys(), key=lambda c: colors[c]):
        min_x, max_x = w, 0
        min_y, max_y = h, 0
        for y in range(h):
            for x in range(w):
                p = px[y*w+x]
                v = p if isinstance(p, tuple) else (p,p,p)
                if v == c:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        
        cw = max_x - min_x + 1
        ch = max_y - min_y + 1
        
        ci = Image.new("L", (cw, ch), 255)
        for y in range(min_y, max_y+1):
            for x in range(min_x, max_x+1):
                p = px[y*w+x]
                v = p if isinstance(p, tuple) else (p,p,p)
                if v == c:
                    ci.putpixel((x-min_x, y-min_y), 0)
        
        # Enlarge 4x for better OCR
        ci_big = ci.resize((cw*4, ch*4), Image.LANCZOS)
        ci_big.save("/tmp/_ch.png")
        
        txt = ""
        for psm in [10, 8, 7, 6]:
            r = subprocess.run(["tesseract", "/tmp/_ch.png", "stdout", 
                              "--psm", str(psm),
                              "-c", "tessedit_char_whitelist=0123456789"],
                             capture_output=True, text=True, timeout=5)
            txt = r.stdout.strip()
            if txt:
                break
        
        print(f"Color {colors[c]} at x={min_x}-{max_x} OCR=[{txt}]", file=sys.stderr)
        for y2 in range(ch):
            row = ""
            for x2 in range(cw):
                row += "#" if ci.getpixel((x2, y2)) == 0 else " "
            print(f"  |{row}|", file=sys.stderr)
        
        output.append((min_x, txt))

    output.sort(key=lambda x: x[0])
    result = "".join(o[1] for o in output)
    print(f"CODE_RESULT:{result}")
    return result

if __name__ == "__main__":
    solve()
