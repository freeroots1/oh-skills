#!/bin/bash
# Phase 1: Port scan all IPs using nmap (fast TCP connect scan)
echo "[*] Starting nmap scan on $(wc -l < /tmp/all_ips.txt) IPs..."
nmap -n -Pn -T4 --open -p 22,21,3306,3389,6379,8080,8443,1433,5985 -iL /tmp/all_ips.txt -oG /tmp/nmap_results.gnmap 2>&1
echo "[*] nmap scan complete"

# Parse open ports
echo ""
echo "=== OPEN PORTS BY IP ==="
grep -v "^#" /tmp/nmap_results.gnmap | grep -i "open" | while read line; do
    ip=$(echo "$line" | awk '{print $2}')
    ports_info=$(echo "$line" | grep -oP '\d+/open/[^ ]*')
    if [ -n "$ports_info" ]; then
        echo "$ip: $ports_info"
    fi
done

echo ""
echo "[*] Total IPs with open ports: $(grep -v '^#' /tmp/nmap_results.gnmap | grep -c -i 'open')"
