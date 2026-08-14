#!/bin/bash
# gw_stop_test.sh - stop gw, then long-poll test
LOG=/tmp/gw_stop_test.log
echo "=== $(date) ===" >> $LOG
pkill -f 'hermes gateway run' 2>/dev/null
sleep 10
echo "gw stopped: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
# long poll test with gw stopped
timeout 32 curl -s --max-time 30 'https://api.telegram.org/bot8862875681:AAHxAyFUp-kaBXnEVhDeoTqbyWBTXg7KvlI/getUpdates?timeout=25&limit=1' -o /tmp/lp2.json 2>>$LOG
python3 -c "
import json
d = json.load(open('/tmp/lp2.json'))
print('LONG-POLL gw stopped: ok=%s desc=%s' % (d.get('ok'), d.get('description','')[:90]))
" >> $LOG 2>&1
echo "=== END $(date) ===" >> $LOG
