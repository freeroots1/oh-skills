#!/usr/bin/env python3
"""filter real attackable targets from web_vuln2 - exclude hijacked/betting/redirect"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOSTILE = ["register", ".vip", "bet", "casino", "lottery", "baccarat", "88", "999",
           "f7ae5v", "i_code", "im_token", "ky77", "kg168", "haha", "blg", "bw",
           "touzhu", "dubo", "yule", "lehu", "tenglong", "kf", "ag", "bg", "og"]

def check(domain):
    try:
        req = urllib.request.Request("http://" + domain + "/", headers=UA)
        r = urllib.request.urlopen(req, timeout=8)
        url = r.geturl()
        body = r.read(200000).decode("utf-8", "ignore")
        code = r.status
        # hijacked if redirects to hostile domain
        if any(h in url.lower() for h in ["register", ".vip", "bet", "casino"]):
            return (domain, "REDIRECT-HIJACK", url[:60])
        # check title
        m = re.search(r"<title>([^<]*)</title>", body, re.I)
        title = m.group(1).strip()[:40] if m else ""
        if not title:
            return (domain, "NO-TITLE", url[:60])
        # betting indicators in title/body
        if any(h in (title + body[:3000]).lower() for h in ["博彩", "娱乐城", "开户", "投注", "ag真人", "彩票", "棋牌"]):
            return (domain, "BETTING", title)
        return (domain, "REAL", title + " | " + url[:50])
    except urllib.error.HTTPError as e:
        return (domain, "HTTP%d" % e.code, "")
    except Exception as ex:
        return (domain, "ERR", str(ex)[:40])

def main():
    doms = set()
    for line in open("/tmp/web_vuln2.txt"):
        m = re.search(r"\[(?:CMS|UPLOAD)\]\s+([a-z0-9.-]+)", line)
        if m:
            d = m.group(1).strip().lower()
            if any(b in d for b in ["sina", "sohu", "163.com", "baidu", "douyin", "taobao", "pcauto", "58pic", "ibaotu", "bilibili", "gov.cn", "cambridge", "csdn", "jb51", "hanslaser", "chemicalbook", "shiyanjia", "chinacable", "dedemao"]):
                continue
            doms.add(d)
    print("checking %d unique" % len(doms), flush=True)
    real = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for fut in as_completed(futs):
            d, status, info = fut.result()
            if status == "REAL":
                real.append((d, info))
            print("  %s [%s] %s" % (d, status, info), flush=True)
    print("\n=== REAL targets (%d) ===" % len(real))
    with open("/tmp/real_targets.txt", "w") as f:
        for d, info in real:
            f.write("%s\t%s\n" % (d, info))
            print(d, "|", info)

if __name__ == "__main__":
    main()
