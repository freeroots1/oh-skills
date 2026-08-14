import json, glob

for f in sorted(glob.glob("/tmp/scan_results/*.json")):
    d = json.load(open(f))
    server = d.get("server","")
    if "IIS" in server or "ASP" in server:
        domain = d.get("domain","")
        ips = d.get("ips",[])
        ip = ips[0] if ips else ""
        logins = d.get("logins",[])
        mdb_hit = d.get("others",[])
        print("%-35s | IIS: %-25s | IP: %-15s | logins:%s | other:%s" % (domain, server[:25], ip, logins[:3], mdb_hit[:3]))
