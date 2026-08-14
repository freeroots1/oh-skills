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

charset = string.ascii_lowercase + string.digits
print('Charset: ' + charset, flush=True)

# Try lengths 1 to 4 first (fast)
for length in range(1, 5):
    print('Trying length ' + str(length) + '...', flush=True)
    for combo in itertools.product(charset, repeat=length):
        pw = ''.join(combo)
        h = mysql_old_password(pw)
        if h in targets:
            found[h] = pw
            print('FOUND: ' + targets[h] + ' -> ' + pw, flush=True)
            if len(found) == len(targets):
                print('All found!', flush=True)
                sys.exit(0)
    if found:
        break

if found:
    print()
    print('=== RESULTS ===')
    for h, username in targets.items():
        if h in found:
            print(username + ' (' + h + '): ' + found[h])
        else:
            print(username + ' (' + h + '): NOT FOUND')
else:
    print()
    print('No passwords found up to length 4')
    print('Would need to try longer lengths')
