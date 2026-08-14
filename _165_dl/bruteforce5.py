import itertools
import string
import sys

def mysql_old_password(password):
    nr = 1345345333
    add = 7
    nr2 = 0x12345671
    for c in password:
        if c == ' ' or c == '\t':
            continue
        byte = ord(c)
        nr ^= (((nr & 63) + add) * byte) + (nr << 8)
        nr2 += (nr2 << 8) ^ nr
        add += byte
    nr = nr & 0x7fffffff
    nr2 = nr2 & 0x7fffffff
    return '%08lx%08lx' % (nr, nr2)

targets = {'2d9d5942943a1323': 'admin', '79dca16741891333': 'admin999'}

# Try length 5 with lowercase only (11.8M combinations)
charset = string.ascii_lowercase  # 26 letters
print('Trying length 5 with charset: ' + charset, flush=True)
count = 0
for combo in itertools.product(charset, repeat=5):
    pw = ''.join(combo)
    h = mysql_old_password(pw)
    if h in targets:
        print('FOUND: ' + targets[h] + ' -> ' + pw, flush=True)
        sys.exit(0)
    count += 1
    if count % 1000000 == 0:
        print('Progress: ' + str(count) + ' / 11881376', flush=True)

print('No passwords found at length 5 with lowercase', flush=True)
