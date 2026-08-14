import socket, subprocess, threading, sys

# 阿里云常见企业Windows主机IP段
ranges = [
    '47.92.', '47.93.', '47.94.', '47.95.',
    '47.96.', '47.97.', '47.98.', '47.99.',
    '47.100.', '47.101.', '47.102.', '47.103.',
    '47.104.', '47.105.', '47.106.', '47.107.',
    '47.108.', '47.109.', '47.110.', '47.111.',
    '47.112.', '47.113.', '47.114.', '47.115.',
    '47.116.', '47.117.', '47.118.', '47.119.',
    '8.210.', '8.211.', '8.212.', '8.213.',
    '8.214.', '8.215.', '8.216.', '8.217.',
    '8.218.', '8.219.',
    '120.76.', '120.77.', '120.78.', '120.79.',
    '120.24.', '120.25.', '120.26.',
    '121.40.', '121.41.', '121.42.', '121.43.',
    '121.196.', '121.197.', '121.198.', '121.199.',
    '118.190.', '118.191.',
    '123.56.', '123.57.', '123.58.',
    '39.96.', '39.97.', '39.98.', '39.99.',
    '39.100.', '39.101.', '39.102.', '39.103.',
    '39.104.', '39.105.', '39.106.', '39.107.',
    '139.196.', '139.197.', '139.198.',
    '112.124.', '112.125.',
]

iis_found = []
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
            if 'IIS' in r.stdout or 'Microsoft' in r.stdout:
                with lock:
                    iis_found.append(ip)
                    print(ip)
        s.close()
    except:
        pass

threads = []
for subnet in ranges:
    for host in [1,2,3,4,5,6,7,8,9,10]:
        if len(iis_found) >= 20:
            break
        ip = subnet + str(host)
        t = threading.Thread(target=check, args=(ip,))
        t.start()
        threads.append(t)
    if len(iis_found) >= 20:
        break

for t in threads:
    t.join(2)

print('IIS found:', len(iis_found))
