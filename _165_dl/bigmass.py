import socket, subprocess, threading, time

# 阿里云全量国内企业常用/16段
ranges = []
# 47.x段
for i in range(88, 120): ranges.append('47.' + str(i) + '.')
# 120.x段  
for i in range(24, 56): ranges.append('120.' + str(i) + '.')
# 121.x段
for i in range(40, 43): ranges.append('121.' + str(i) + '.')
for i in range(196, 200): ranges.append('121.' + str(i) + '.')
# 118.x段
for i in range(190, 192): ranges.append('118.' + str(i) + '.')
# 123.x段
for i in range(56, 59): ranges.append('123.' + str(i) + '.')
# 39.x段
for i in range(96, 108): ranges.append('39.' + str(i) + '.')
# 8.x段
for i in range(210, 220): ranges.append('8.' + str(i) + '.')
# 112.x段
for i in range(124, 126): ranges.append('112.' + str(i) + '.')
# 106.x段
for i in range(14, 16): ranges.append('106.' + str(i) + '.')
# 101.x段
for i in range(126, 127): ranges.append('101.' + str(i) + '.')
# 139.x段
for i in range(196, 199): ranges.append('139.' + str(i) + '.')

print('Scanning ' + str(len(ranges)) + ' subnets...')

found = []
lock = threading.Lock()

def check(ip):
    try:
        s = socket.socket(); s.settimeout(0.5)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(
                ['curl', '-sk', '--connect-timeout', '2', '--max-time', '3',
                 'http://' + ip, '-D', '-', '-o', '/dev/null'],
                capture_output=True, text=True, timeout=4)
            out = r.stdout
            if 'IIS' in out or 'Microsoft' in out:
                rdp = False
                try:
                    s2 = socket.socket(); s2.settimeout(1)
                    if s2.connect_ex((ip, 3389)) == 0: rdp = True
                    s2.close()
                except: pass
                with lock:
                    tag = 'RDP' if rdp else 'IIS'
                    found.append((ip, tag))
                    print(ip + ' [' + tag + ']')
    except: pass

threads = []
count = 0
MAX = 30

for subnet in ranges:
    for host in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        if len(found) >= MAX: break
        ip = subnet + str(host)
        t = threading.Thread(target=check, args=(ip,))
        t.start()
        threads.append(t)
    if len(found) >= MAX: break

for t in threads:
    t.join(2)

rdp_count = sum(1 for _, tag in found if tag == 'RDP')
print('IIS: ' + str(len(found)) + ', RDP: ' + str(rdp_count))
