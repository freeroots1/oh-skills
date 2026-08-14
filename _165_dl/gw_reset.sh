#!/bin/bash
# gw_reset.sh - stop gw, reset telegram session via offset=-1, clean start
LOG=/tmp/gw_reset.log
echo "=== GW RESET $(date) ===" >> $LOG
TOKEN="8862875681:AAHxAyFUp-kaBXnEVhDeoTqbyWBTXg7KvlI"

# 1. stop gateway
pkill -f 'hermes gateway run' 2>/dev/null
sleep 6
echo "stopped: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG

# 2. reset telegram polling session (consume pending, force refresh)
echo "--- getUpdates offset=-1 x3 ---" >> $LOG
for i in 1 2 3; do
  curl -s --max-time 15 "https://api.telegram.org/bot${TOKEN}/getUpdates?offset=-1&timeout=0" -o /tmp/tg_reset_$i.json >> $LOG 2>&1
  python3 -c "
import json
try:
    d = json.load(open('/tmp/tg_reset_$i.json'))
    print('round $i ok=%s desc=%s pending=%d' % (d.get('ok'), d.get('description',''), len(d.get('result',[]))))
except Exception as e:
    print('round $i err', e)
" >> $LOG 2>&1
  sleep 4
done

# 3. wait for stale session expiry
sleep 15

# 4. clean start
cd /usr/local/lib/hermes-agent
setsid nohup ./venv/bin/python3 ./hermes gateway run >> /root/.hermes/logs/gateway_restart.log 2>&1 < /dev/null &
sleep 8
echo "restarted: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
sleep 30
echo "--- post-start log ---" >> $LOG
grep -E 'polling|conflict|Connected|health' /root/.hermes/logs/gateway_restart.log 2>/dev/null | tail -5 >> $LOG
echo "=== GW RESET END $(date) ===" >> $LOG
