#!/usr/bin/env python3
"""debug ip_reverse: check which IPs queried + rapidDNS responses"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode(errors="ignore")
    except Exception:
        return ""

ips = [l.strip() for l in open("/opt/msray/ips.txt") if l.strip()]
print("total ips:", len(ips))
seen = set(l.strip() for l in open("/opt/msray/collect_domains.txt"))
print("known domains:", len(seen))

# test 10 IPs from different positions
for ip in ips[0:3] + ips[1500:1503] + ips[3200:3203]:
    html = fetch("https://rapiddns.io/s/%s?full=1" % ip)
    doms = set(re.findall(r"[\w.-]+\.(?:com|cn|net|org|cc|top|xyz|vip|info|biz|me)", html))
    clean = {d.lower() for d in doms if not any(x in d.lower() for x in ["rapiddns", "w3.org", "google", "schema", "cloudflare"])}
    new = clean - seen
    print("%s: raw=%d clean=%d NEW=%d %s" % (ip, len(doms), len(clean), len(new), list(new)[:3]))
    time.sleep(0.5)
