#!/bin/bash
# stop165gw.sh - stop 165 gateway permanently (local desktop polls TG)
# 165 cron pushes use direct sendMessage API - not affected
LOG=/tmp/stop165gw.log
echo "=== STOP 165 GW $(date) ===" >> $LOG
pkill -f 'hermes gateway run' 2>/dev/null
sleep 8
echo "165 gw stopped: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
# verify no polling from 165
timeout 32 curl -s --max-time 30 'https://api.telegram.org/bot8862875681:AAHxAyFUp-kaBXnEVhDeoTqbyWBTXg7KvlI/getUpdates?timeout=25&limit=1' -o /tmp/stop_lp.json
python3 -c "
import json
d = json.load(open('/tmp/stop_lp.json'))
print('long-poll after stop: ok=%s desc=%s' % (d.get('ok'), d.get('description','')[:70]))
" >> $LOG 2>&1
echo "=== END $(date) ===" >> $LOG
