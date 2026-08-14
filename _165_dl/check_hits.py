import json

with open('/tmp/overnight_scan_results.json') as f:
    r = json.load(f)

alive = sum(1 for e in r['targets'].values() if e.get('alive'))
total = len(r['targets'])
hits_list = []

for d, e in r['targets'].items():
    tp = len(e.get('thinkphp_hits', []))
    pb = len(e.get('pboot_hits', []))
    vl = len(e.get('vuln_hits', []))
    if tp + pb + vl > 0:
        hits_list.append(f"[{d}] TP:{tp} PB:{pb} VL:{vl}")
        for h in e.get('thinkphp_hits', []):
            hits_list.append(f"  TP: {h}")
        for h in e.get('pboot_hits', []):
            hits_list.append(f"  PB: {h}")
        for h in e.get('vuln_hits', []):
            hits_list.append(f"  VL: {h}")

hit_count = len([x for x in hits_list if x.startswith('[')])

print(f"Total: {total} | Alive: {alive} | Hit targets: {hit_count}")
for line in hits_list:
    print(line)
print(f"\nProgress: {r.get('scan_progress', '?')}")
