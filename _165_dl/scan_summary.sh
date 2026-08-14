#!/bin/bash
# Run tomorrow: bash /tmp/scan_summary.sh
python3 -c "
import json
with open('/tmp/overnight_scan_results.json') as f:
    r = json.load(f)

total = len(r.get('targets',{}))
alive = sum(1 for e in r['targets'].values() if e.get('alive'))
all_hits = []

for domain, entry in r['targets'].items():
    if not entry.get('alive'): continue
    hits = []
    for h in entry.get('thinkphp_hits', []):
        hits.append(f\"ThinkPHP:{h['name']}\")
    for h in entry.get('pboot_hits', []):
        hits.append(f\"PbootCMS:{h['name']}\")
    for h in entry.get('vuln_hits', []):
        hits.append(f\"Vuln:{h['name']}\")
    if hits:
        all_hits.append((domain, entry.get('powered',''), entry.get('cms',''), hits))

print(f'=== OVERNIGHT SCAN RESULTS ===')
print(f'Scanned: {total} | Alive: {alive} | Hits: {len(all_hits)} targets')
print()

for d, p, c, hits in all_hits:
    print(f'[+] {d} (powered={p} cms={c})')
    for h in hits:
        print(f'    -> {h}')
    print()
"
