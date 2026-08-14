#!/usr/bin/env python3
"""尝试 124.71 pma session 修复: 
1. 测 phpinfo 里 session.save_path 目录是否存在(通过php探针的其他功能)
2. 试 pma 带 SID 参数
3. 试 https 端口
4. 试其他 pma 路径
"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def get(url, t=10):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=t, context=ctx)
        return r.status, r.read().decode("utf-8","ignore")
    except Exception as e:
        return 0, str(e)[:100]

# 1. 检查 124.71 其他端口
for port in [80, 443, 8080, 8888, 9096]:
    s, b = get(f"http://124.71.142.158:{port}/", 6)
    title = re.search(r"<title>([^<]{0,40})", b)
    print(f"port {port}: {s} title={title.group(1) if title else '?'} size={len(b)}")

# 2. pma session 修复尝试: 通过 ?s= 或强制session
s, b = get("http://124.71.142.158:9096/phpMyAdmin/index.php?server=1", 8)
print("\npma index.php:", s, "| session err:", "Cannot start session" in b)
s, b = get("http://124.71.142.158:9096/phpMyAdmin/", 8)
print("pma /:", s, "| session err:", "Cannot start session" in b)
