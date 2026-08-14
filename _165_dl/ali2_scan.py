import socket, subprocess, threading

ranges = [
    '106.14.', '106.15.',
    '47.96.', '47.97.', '47.98.', '47.99.', '47.100.', '47.101.',
    '47.102.', '47.103.', '47.104.', '47.105.', '47.106.', '47.107.',
    '47.108.', '47.109.', '47.110.', '47.111.', '47.112.', '47.113.',
    '47.114.', '47.115.', '47.116.', '47.117.', '47.118.', '47.119.',
    '120.24.', '120.25.', '120.26.', '120.27.', '120.28.', '120.29.',
    '120.30.', '120.31.', '120.32.', '120.33.', '120.34.', '120.35.',
    '120.36.', '120.37.', '120.38.', '120.39.',
    '39.96.', '39.97.', '39.98.', '39.99.', '39.100.', '39.101.',
    '39.102.', '39.103.', '39.104.', '39.105.', '39.106.', '39.107.',
]

found = []
lock = threading.Lock()

def check_ip(ip):
    try:
        s = socket.socket()
        s.settimeout(0.5)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(
                ['curl', '-sk', '--connect-timeout', '2', '--max-time', '3',
                 'http://' + ip, '-o', '/dev/null', '-w', '%{http_code}'],
                capture_output=True, text=True, timeout=4)
            code = r.stdout.strip()
            if code in ['200', '301', '302', '403']:
                with lock:
                    print(ip)
                    found.append(ip)
    except:
        pass

threads = []
for subnet in ranges:
    for host in range(1, 10):
        if len(found) >= 30:
            break
        ip = subnet + str(host)
        t = threading.Thread(target=check_ip, args=(ip,))
        t.start()
        threads.append(t)
    if len(found) >= 30:
        break

for t in threads:
    t.join(2)

print('Found:', len(found))
