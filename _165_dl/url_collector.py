#!/usr/bin/env python3
"""
URL采集器 v4 — RapidDNS/HackerTarget同IP反查 + ViewDNS
从已有目标IP反查同服务器站点，大量收割中国域名
"""
import subprocess, re, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def curl(url, timeout=15):
    cmd = ["curl", "-sk", "--connect-timeout", "8", "--max-time", str(timeout), url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return r.stdout
    except:
        return ""

def rapiddns(ip):
    """RapidDNS 同IP反查"""
    domains = set()
    html = curl("https://rapiddns.io/sameip/{}?full=1".format(ip))
    if not html: return domains
    for m in re.finditer(r"<td[^>]*>([a-z0-9.-]{3,}\.[a-z]{2,})</td>", html, re.I):
        domains.add(m.group(1).lower())
    return domains

def hackertarget(ip):
    """HackerTarget 反查"""
    domains = set()
    html = curl("https://api.hackertarget.com/reverseiplookup/?q={}".format(ip))
    if not html: return domains
    for line in html.split("\n"):
        d = line.strip().lower()
        if "." in d and len(d) > 5:
            domains.add(d)
    return domains

def viewdns(ip):
    """ViewDNS 反查"""
    domains = set()
    html = curl("https://viewdns.info/reverseip/?host={}&t=1".format(ip))
    if not html: return domains
    for m in re.finditer(r"<td[^>]*>([a-z0-9.-]{3,}\.[a-z]{2,})</td>", html, re.I):
        d = m.group(1).lower()
        if len(d) > 5: domains.add(d)
    return domains

def normalize(host):
    h = re.sub(r"^www\d*\.", "", host.lower())
    if " " in h or "." not in h or len(h) < 6 or len(h) > 60: return None
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", h): return None
    if re.match(r"^\d+$", h): return None
    # 过滤基础设施/垃圾
    if re.search(r"(api\.|cdn\.|static\.|img\.|mail\.|smtp\.|pop\.|ftp\.|ns\d?\.|dns\d?\.|test\.|demo\.|dev\.|staging\.)", h): return None
    # 过滤WAF/CDN子域名
    if re.search(r"(yundunwaf|aliyundun|aligfwaf|rswaf|jcloud-cache|iispbdy|cdngslb|cdn\..*\.com$)", h): return None
    # 过滤随机hash子域名 (>20字符)
    if len(h.split(".")[0]) > 20: return None
    # 过滤垃圾TLD
    if re.search(r"\.(xyz|tk|ml|ga|cf|gq|pw)$", h): return None
    return h

def main():
    # 从已有的扫描数据中提取IP种子
    seed_ips = [
        # 来自 scan_v7_out.txt 的活跃IP
        "47.92.19.42", "47.100.0.1", "47.92.200.140",
        "124.71.142.158", "150.158.95.32", "81.70.245.25",
        "211.149.230.223", "39.96.129.124", "180.76.132.237",
        "119.23.85.119", "134.175.104.187", "180.97.198.41",
        "120.48.70.251", "140.249.250.183", "148.178.64.17",
        "38.11.47.136", "139.196.56.187", "67.211.78.137",
        "107.151.115.9", "103.39.148.199", "47.105.73.201",
    ]
    
    # 用户可通过命令行添加更多IP
    if len(sys.argv) > 1:
        seed_ips = sys.argv[1:]
    
    print("数据源: RapidDNS + HackerTarget")
    print("种子IP: {} 个".format(len(seed_ips)))
    print("=" * 50)
    
    all_domains = set()
    
    # 并发反查
    tasks = []
    for ip in seed_ips:
        tasks.append(("RapidDNS", ip, rapiddns))
        tasks.append(("HackerTarget", ip, hackertarget))
    
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fn, ip): (name, ip) for name, ip, fn in tasks}
        for f in as_completed(futures):
            name, ip = futures[f]
            try:
                domains = f.result()
                if domains:
                    print("  [{}] {} -> {} domains".format(name, ip, len(domains)))
                all_domains.update(domains)
            except Exception as e:
                print("  [{}] {} FAILED: {}".format(name, ip, e))
    
    # 去重+过滤
    final = []
    seen = set()
    for d in all_domains:
        nd = normalize(d)
        if nd and nd not in seen:
            seen.add(nd)
            final.append(nd)
    final.sort()
    
    # 保存
    out = "/tmp/collected_domains.txt"
    with open(out, "w") as f:
        for d in final: f.write(d + "\n")
    
    # 对比已有
    try:
        with open("/tmp/all_4719_domains.txt") as f:
            existing = set(l.strip() for l in f if l.strip())
    except:
        existing = set()
    
    new_domains = [d for d in final if d not in existing]
    if new_domains:
        with open("/tmp/new_domains.txt", "w") as f:
            for d in new_domains: f.write(d + "\n")
    
    print("\n" + "=" * 50)
    print("总域名: {} | 新域名(不在4719中): {}".format(len(final), len(new_domains)))
    print("保存: {} / {}".format(out, "/tmp/new_domains.txt"))
    print("\n样本(前30):")
    for d in final[:30]: print("  " + d)
    if new_domains:
        print("\n新域名(前20):")
        for d in new_domains[:20]: print("  " + d)

if __name__ == "__main__":
    main()
