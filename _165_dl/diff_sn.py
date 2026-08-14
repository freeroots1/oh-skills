#!/usr/bin/env python3
import re
t2 = open('/tmp/kir_sn_1042.html', encoding='gbk', errors='ignore').read()
t3 = open('/tmp/kir_sn_1043.html', encoding='gbk', errors='ignore').read()
for kw in ['2026-08-10', '1042', '1043', 'kshell', 'injecttest', 'BACBCAB7', '599E3CAF']:
    print(kw, 'in1042:', kw in t2, '| in1043:', kw in t3)
print('len1042:', len(t2), 'len1043:', len(t3))
# find the differing region
import difflib
sm = difflib.SequenceMatcher(None, t2, t3)
for op in sm.get_opcodes():
    if op[0] == 'replace' or op[0] == 'delete' or op[0] == 'insert':
        print('OP:', op[0], 't2[%d:%d]' % (op[1], op[2]), 't3[%d:%d]' % (op[3], op[4]))
        for i in range(op[1], min(op[2], op[1]+200)):
            pass
        seg2 = t2[op[1]:op[2]][:300]
        seg3 = t3[op[3]:op[4]][:300]
        print('  t2:', repr(seg2[:200]))
        print('  t3:', repr(seg3[:200]))
        break
# print tail of page to find content area
print('--- 1042 tail 400 ---')
print(' '.join(t2[-400:].split())[:400])
