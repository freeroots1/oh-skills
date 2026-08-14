import json

with open('/root/tools/enterprise_db.json') as f:
    db = json.load(f)

targets = []
for domain, info in db.items():
    if isinstance(info, dict) and 'skip' not in info:
        targets.append({
            'domain': domain,
            'powered': info.get('powered',''),
            'cms': info.get('cms',''),
            'server': info.get('server',''),
        })

thinkphp = [t for t in targets if 'ThinkPHP' in t['powered'] or 'ThinkPHP' in t['cms']]
pboot = [t for t in targets if 'PbootCMS' in t['powered']]
php_t = [t for t in targets if 'PHP' in t['powered'] or 'PHP' in t['server']]
others = [t for t in targets if t not in thinkphp and t not in pboot and t not in php_t]

print(f"Total: {len(targets)} | ThinkPHP: {len(thinkphp)} | Pboot: {len(pboot)} | PHP: {len(php_t)} | Other: {len(others)}")
print()
print("=== ThinkPHP ===")
for t in thinkphp:
    print(f"  {t['domain']}")
print()
print("=== PbootCMS ===")
for t in pboot:
    print(f"  {t['domain']}")
print()
print("=== PHP ===")
for t in php_t[:20]:
    print(f"  {t['domain']} | {t['powered']} | {t['server']}")
print()
print("=== Others ===")
for t in others[:20]:
    print(f"  {t['domain']} | {t['powered']} | {t['server']} | {t['cms']}")

print()
print("=== Old Sites DB ===")
with open('/root/tools/old_sites_db.json') as f:
    old = json.load(f)
for s in old.get('sites', []):
    print(f"  {s['domain']} | {s.get('powered','')} | {s.get('server','')} | score={s.get('vuln_score',0)}")
