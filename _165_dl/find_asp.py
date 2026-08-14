import json, glob, os
os.chdir("/tmp/scan_results")
asp_sites = []
for f in glob.glob("*.json"):
    d = json.load(open(f))
    url = d.get("url","")
    h = d.get("headers",{})
    if not isinstance(h, dict): h = {}
    server = h.get("Server","")
    xpb = h.get("X-Powered-By","") or h.get("x-powered-by","")
    cookies = h.get("Set-Cookie","") or h.get("set-cookie","")
    if "ASPSESSIONID" in str(cookies) or "IIS" in str(server) or "ASP" in str(xpb) or ".asp" in url.lower():
        domain = url.replace("https://","").replace("http://","").split("/")[0]
        asp_sites.append([domain, str(server)[:50], str(xpb)[:50], str(cookies)[:80]])
asp_sites.sort()
for s in asp_sites:
    print("%-40s | %-25s | %-25s | %s" % (s[0], s[1], s[2], s[3][:60]))
print("\nTotal ASP/IIS: %d" % len(asp_sites))
