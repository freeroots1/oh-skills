#!/usr/bin/env python3
"""probe DedeCMS/PbootCMS known vuln paths on fresh targets"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOSTILE = ["register", ".vip", "bet", "casino", "f7ae5v", "i_code"]

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.geturl(), r.read(100000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, url, ""

def probe(domain):
    if any(h in domain for h in HOSTILE):
        return
    results = []
    # home first
    code, final, body = fetch("http://" + domain + "/")
    if code == 0 or "register" in final.lower() or ".vip" in final.lower():
        return
    title = re.search(r"<title>([^<]*)</title>", body, re.I)
    results.append(("home", code, title.group(1).strip()[:30] if title else ""))
    # DedeCMS paths
    dede_paths = [
        "/dede/login.php", "/dede/index.php", "/member/index.php",
        "/plus/download.php", "/plus/flink.php", "/plus/search.php",
        "/data/admin/ver.txt", "/install/index.php",
    ]
    # PbootCMS paths
    pboot_paths = [
        "/admin.php", "/index.php?list=1", "/api.php", "/robots.txt",
        "/static/", "/doc.html",
    ]
    for p in dede_paths:
        code, final, body = fetch("http://" + domain + p)
        if code == 200 and len(body) > 500:
            results.append(("dede:" + p, code, body[:60].replace("\n", " ")))
    for p in pboot_paths:
        code, final, body = fetch("http://" + domain + p)
        if code == 200 and len(body) > 300:
            results.append(("pboot:" + p, code, body[:60].replace("\n", " ")))
    return results

def main():
    doms = ["xiangshanrc.com", "szshunmin.com", "zhxcard.com", "csroots.cn",
            "gdhhjxkj.com", "lahzjc.com", "wuhushangjie.com", "ahygfz.com",
            "ouyu158.com", "greatnqi.com"]
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(probe, d): d for d in doms}
        for fut in as_completed(futs):
            d = futs[fut]
            r = fut.result()
            if not r:
                print("%s: skip/hijacked" % d, flush=True)
                continue
            print("\n=== %s ===" % d, flush=True)
            for tag, code, info in r:
                print("  %s: %s %s" % (tag, code, info), flush=True)

if __name__ == "__main__":
    main()
