#!/usr/bin/env python3
"""csroots.cn WP user enum + xmlrpc check + plugin vuln scan"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOST = "https://www.csroots.cn"

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "text/xml" if data and "<" in data else "application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.geturl(), r.read(100000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(10000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

# 1. author enum
print("=== user enum ===")
for i in range(1, 6):
    code, final, body = fetch(HOST + "/?author=%d" % i)
    if code == 200:
        m = re.search(r'/author/([^/]+)/', body) or re.search(r'author=([^"&]+)', body)
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        print("  author=%d: %s %s" % (i, m.group(1) if m else "?", (title.group(1).strip()[:30] if title else "")))

# 2. xmlrpc
print("=== xmlrpc ===")
code, final, body = fetch(HOST + "/xmlrpc.php", data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>')
print("  xmlrpc:", code, "wp.getUsersBlogs:", "wp.getUsersBlogs" in body)

# 3. wp-json users
code, final, body = fetch(HOST + "/wp-json/wp/v2/users")
print("  wp-json users:", code, body[:200])

# 4. plugin presence
print("=== plugins ===")
plugins = ["/wp-content/plugins/revslider/", "/wp-content/plugins/elementor/",
           "/wp-content/plugins/contact-form-7/", "/wp-content/plugins/woocommerce/",
           "/wp-content/plugins/duplicator/", "/wp-content/plugins/yith-woocommerce-",
           "/wp-content/plugins/wordfence/", "/wp-content/plugins/akismet/"]
for p in plugins:
    code, final, body = fetch(HOST + p)
    if code in (200, 403):
        print("  %s: %s" % (p, code))

# 5. readme version
code, final, body = fetch(HOST + "/readme.html")
if code == 200:
    m = re.search(r'Version\s+([0-9.]+)', body)
    print("  WP version:", m.group(1) if m else "?")
code, final, body = fetch(HOST + "/wp-links-opml.php")
if code == 200:
    m = re.search(r'generator="wordpress/([0-9.]+)"', body)
    print("  WP gen:", m.group(1) if m else "?")
