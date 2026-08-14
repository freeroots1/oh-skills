#!/bin/bash
# gw_clean_restart.sh - stop gateway, verify API, clean start
LOG=/tmp/gw_restart.log
echo "=== GW RESTART $(date) ===" >> $LOG

# 1. stop all gateway instances
pkill -f 'hermes gateway run' 2>/dev/null
pkill -f 'screen -dmS gw' 2>/dev/null
screen -S gw -X quit 2>/dev/null
sleep 5
echo "gateway stopped: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG

# 2. verify no conflict on Telegram API
curl -s --max-time 12 'https://api.telegram.org/bot8862875681:AAHxAyFUp-kaBXnEVhDeoTqbyWBTXg7KvlI/getUpdates?timeout=3&limit=1' -o /tmp/tg_verify.json 2>>$LOG
python3 -c "
import json
try:
    d = json.load(open('/tmp/tg_verify.json'))
    ok = d.get('ok')
    desc = d.get('description','')
    print('API ok=%s conflict=%s' % (ok, 'Conflict' in desc))
except Exception as e:
    print('API read err', e)
" >> $LOG 2>&1

# 3. clean start gateway (detached, survives ssh)
cd /usr/local/lib/hermes-agent
sleep 2
setsid nohup ./venv/bin/python3 ./hermes gateway run >> /root/.hermes/logs/gateway_restart.log 2>&1 < /dev/null &
sleep 6
echo "gateway restarted: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
sleep 25
echo "=== post-start polling check ===" >> $LOG
tail -6 /root/.hermes/logs/gateway_restart.log 2>/dev/null >> $LOG
echo "=== GW RESTART END $(date) ===" >> $LOG
