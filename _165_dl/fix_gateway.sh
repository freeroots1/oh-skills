#!/bin/bash
# fix_gateway.sh - stop gw, dedupe token, disable weixin, clean restart
LOG=/tmp/fix_gateway.log
echo "=== FIX GATEWAY $(date) ===" >> $LOG

# 1. stop gateway
pkill -f 'hermes gateway run' 2>/dev/null
sleep 8
echo "gw stopped: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG

# 2. dedupe: comment TELEGRAM_BOT_TOKEN in /root/.hermes/.env (keep /opt/hermes-gateway/.env as single source)
if grep -q '^TELEGRAM_BOT_TOKEN=' /root/.hermes/.env; then
  sed -i 's/^TELEGRAM_BOT_TOKEN=/#TELEGRAM_BOT_TOKEN=/' /root/.hermes/.env
  echo "deduped /root/.hermes/.env token" >> $LOG
fi

# 3. disable weixin (session expired, waste API)
if grep -q '^WEIXIN_' /opt/hermes-gateway/.env; then
  sed -i 's/^WEIXIN_/#WEIXIN_/' /opt/hermes-gateway/.env
  echo "disabled weixin in /opt/hermes-gateway/.env" >> $LOG
fi
if grep -q '^WEIXIN_' /root/.hermes/.env; then
  sed -i 's/^WEIXIN_/#WEIXIN_/' /root/.hermes/.env
  echo "disabled weixin in /root/.hermes/.env" >> $LOG
fi

# 4. clean start gateway with explicit HERMES_HOME=/opt/hermes-gateway (single config)
cd /usr/local/lib/hermes-agent
HERMES_HOME=/opt/hermes-gateway setsid nohup ./venv/bin/python3 ./hermes gateway run >> /root/.hermes/logs/gateway_fix.log 2>&1 < /dev/null &
sleep 15
echo "gw running: $(ps aux | grep -c '[h]ermes gateway')" >> $LOG
sleep 45
echo "--- gateway log (polling check) ---" >> $LOG
tail -10 /root/.hermes/logs/gateway_fix.log 2>/dev/null | cut -c1-160 >> $LOG
echo "=== FIX END $(date) ===" >> $LOG
