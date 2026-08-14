#!/bin/bash
# fix2_gateway.sh - add DISABLE_FALLBACK_IPS to gateway env, clean restart, verify
LOG=/tmp/fix2.log
echo "=== FIX2 $(date) ===" >> $LOG

# 1. add fallback disable to opt env (gateway reads this)
if ! grep -q 'HERMES_TELEGRAM_DISABLE_FALLBACK_IPS' /opt/hermes-gateway/.env; then
  echo 'HERMES_TELEGRAM_DISABLE_FALLBACK_IPS=1' >> /opt/hermes-gateway/.env
  echo "added DISABLE_FALLBACK_IPS to opt/.env" >> $LOG
fi

# 2. stop gw
pkill -f 'hermes gateway run' 2>/dev/null
sleep 8
echo "stopped: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG

# 3. verify clean long-poll before start
timeout 32 curl -s --max-time 30 'https://api.telegram.org/bot8862875681:AAHxAyFUp-kaBXnEVhDeoTqbyWBTXg7KvlI/getUpdates?timeout=25&limit=1' -o /tmp/fix2_lp.json
python3 -c "
import json
d = json.load(open('/tmp/fix2_lp.json'))
print('pre-start long-poll: ok=%s desc=%s' % (d.get('ok'), d.get('description','')[:60]))
" >> $LOG 2>&1

# 4. start gateway (HERMES_HOME=opt)
cd /usr/local/lib/hermes-agent
HERMES_HOME=/opt/hermes-gateway setsid nohup ./venv/bin/python3 ./hermes gateway run >> /root/.hermes/logs/gateway_fix2.log 2>&1 < /dev/null &
sleep 20
echo "running: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
echo "telegram conns: $(ss -tn 2>/dev/null | grep -c '149.154')" >> $LOG
sleep 60
echo "--- post-start (60s later) ---" >> $LOG
tail -6 /root/.hermes/logs/gateway_fix2.log 2>/dev/null | cut -c1-150 >> $LOG
echo "conns after 60s: $(ss -tn 2>/dev/null | grep -c '149.154')" >> $LOG
echo "=== FIX2 END $(date) ===" >> $LOG
