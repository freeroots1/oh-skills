import re
h = open('/tmp/pi13080.html', encoding='utf-8', errors='ignore').read()
# phpinfo的表格格式: <tr><td class="e">key</td><td class="v">value</td></tr>
rows = re.findall(r'<td class="e">([^<]+)</td>\s*<td class="v">([^<]*)</td>', h)
keys = ['disable_functions', 'open_basedir', 'allow_url_include', 'allow_url_fopen',
        'short_open_tag', 'display_errors', 'error_reporting', 'max_execution_time',
        'upload_max_filesize', 'post_max_size', 'safe_mode', 'mysqli.default_socket',
        'pdo_mysql.default_socket']
found = {}
for k, v in rows:
    kk = k.strip()
    if kk in keys or any(kk.startswith(x) for x in keys):
        found[kk] = v.strip()
for k in sorted(found):
    print('%s = %s' % (k, found[k][:200]))
# 系统信息
m = re.search(r'<td class="e">System</td>\s*<td class="v">([^<]*)</td>', h)
if m: print('System = %s' % m.group(1)[:150])
m = re.search(r'<td class="e">SERVER_SOFTWARE</td>\s*<td class="v">([^<]*)</td>', h)
if m: print('SERVER_SOFTWARE = %s' % m.group(1)[:100])
m = re.search(r'<td class="e">DOCUMENT_ROOT</td>\s*<td class="v">([^<]*)</td>', h)
if m: print('DOCUMENT_ROOT = %s' % m.group(1)[:150])
