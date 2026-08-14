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

# Test admin and admin999 with various transformations
pws = set()
for base in ['admin', 'admin999']:
    pws.add(base)
    pws.add(base.upper())
    pws.add(base.capitalize())
    pws.add('Admin' + base[5:])
    for n in range(200):
        pws.add(base + str(n))
    for sfx in ['', '!', '@', '#', '$', '123', '1', '12', '1234', '12345']:
        pws.add(base + sfx)

more = ['bjhzsv', 'bjhzsv.com', 'root', 'password', '123456', 'passw0rd',
        'P@ssw0rd', 'admin123', 'Admin123', 'nagios', 'zabbix', 'cisco',
        'administrator', 'changeme', '']
pws.update(more)

found = False
for p in pws:
    h = mysql_old_password(p)
    if h in targets:
        print('FOUND: ' + targets[h] + ' -> ' + repr(p))
        found = True

if not found:
    print('No matches found')
    print('admin -> ' + mysql_old_password('admin') + ' (target: 2d9d5942943a1323)')
    print('admin999 -> ' + mysql_old_password('admin999') + ' (target: 79dca16741891333)')
