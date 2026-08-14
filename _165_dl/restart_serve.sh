#!/bin/bash
# restart_serve.sh - restart hermes serve 9119 with new unified key
LOG=/tmp/restart_serve.log
echo "=== RESTART SERVE $(date) ===" >> $LOG

# 1. stop old serve
pkill -f 'hermes serve' 2>/dev/null
sleep 6
echo "serve stopped: $(ps aux | grep -c '[h]ermes serve')" >> $LOG

# 2. verify key in config
echo "key check: $(grep '^DEEPSEEK_API_KEY=' /root/.hermes/.env | cut -d= -f2 | cut -c1-8)..." >> $LOG

# 3. start serve (same args as before: --host 0.0.0.0 --port 9119 --skip-build)
cd /usr/local/lib/hermes-agent
HERMES_HOME=/root/.hermes setsid nohup ./venv/bin/python3 ./hermes serve --host 0.0.0.0 --port 9119 --skip-build >> /root/.hermes/logs/serve.log 2>&1 < /dev/null &
sleep 12
echo "serve running: $(ps aux | grep -c '[h]ermes serve')" >> $LOG

# 4. verify port 9119
ss -tlnp 2>/dev/null | grep 9119 >> $LOG

# 5. API health check
curl -s --max-time 8 -u admin:hermes123 http://127.0.0.1:9119/api/health -o /tmp/serve_health.json -w "health http: %{http_code}\n" >> $LOG 2>&1
head -c 200 /tmp/serve_health.json >> $LOG 2>&1
echo >> $LOG
echo "=== END $(date) ===" >> $LOG
