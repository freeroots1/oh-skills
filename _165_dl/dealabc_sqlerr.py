#!/usr/bin/env python3
"""dealabc: verify sqlerr - is it real SQL error or page noise?"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# baseline vs quote
for u, tag in [
    ("http://www.dealabc.com/member.php?mod=logging&action=login&username=test", "login-base"),
    ("http://www.dealabc.com/member.php?mod=logging&action=login&username=test%27", "login-quote"),
    ("http://www.dealabc.com/home.php?mod=space&uid=1", "space-base"),
    ("http://www.dealabc.com/home.php?mod=space&uid=1%27", "space-quote"),
]:
    code, body = fetch(u)
    # real SQL error signatures
    real = re.findall(r'(SQLSTATE|You have an error|mysql_fetch|Unclosed quotation|SQL syntax|Warning: mysql|Discuz! Database)', body, re.I)
    print("%s: code=%s size=%d real_sqlerr=%s" % (tag, code, len(body), real[:2]))
    if real:
        i = body.lower().find(real[0].lower())
        print("  CTX:", body[max(0,i-80):i+150].replace("\n", " ")[:200])
