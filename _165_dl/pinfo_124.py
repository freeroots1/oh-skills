#!/usr/bin/env python3
"""抓 124.71 phpinfo 完整配置"""
import urllib.request, re

B = "http://124.71.142.158:9096/phpinfo.php"
r = urllib.request.urlopen(urllib.request.Request(B, headers={"User-Agent":"Mozilla/5.0"}), timeout=15)
body = r.read().decode("utf-8","ignore")

# 表格解析: <td>key</td><td>value</td>
rows = re.findall(r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]*)</td>', body)
keys = ["session.save_path", "session.save_handler", "DOCUMENT_ROOT", "SCRIPT_FILENAME",
        "session.upload_progress", "upload_tmp_dir", "session.cookie_path", "session.cookie_domain",
        "System Root", "SERVER_SOFTWARE", "disable_functions", "open_basedir"]
for k, v in rows:
    if any(x in k for x in ["session", "DOCUMENT", "SCRIPT_FILENAME", "upload_tmp", "System Root", "SERVER_SOFTWARE", "disable_functions", "open_basedir"]):
        print(f"{k} = {v[:120]}")
