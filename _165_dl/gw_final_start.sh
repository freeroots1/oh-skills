#!/bin/bash
# gw_final_start.sh - clean gateway start + verify polling
LOG=/tmp/gw_final.log
echo "=== GW FINAL START $(date) ===" >> $LOG
cd /usr/local/lib/hermes-agent
setsid nohup ./venv/bin/python3 ./hermes gateway run >> /root/.hermes/logs/gateway_restart.log 2>&1 < /dev/null &
sleep 12
echo "gw running: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
sleep 40
echo "--- gateway log tail ---" >> $LOG
tail -8 /root/.hermes/logs/gateway_restart.log 2>/dev/null | cut -c1-150 >> $LOG
echo "--- conflict check ---" >> $LOG
sleep 60
tail -4 /root/.hermes/logs/gateway_restart.log 2>/dev/null | cut -c1-150 >> $LOG
echo "=== END $(date) ===" >> $LOG
