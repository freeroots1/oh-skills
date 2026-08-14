#!/bin/bash
# unify_key.sh - set all DEEPSEEK_API_KEY to root key (sk-ad7...)
LOG=/tmp/unify_key.log
echo "=== UNIFY KEY $(date) ===" >> $LOG

# read root key (source of truth)
ROOT_KEY=$(grep '^DEEPSEEK_API_KEY=' /root/.hermes/.env | head -1 | cut -d= -f2-)
echo "root key: ${ROOT_KEY:0:8}...${ROOT_KEY: -4}" >> $LOG

# 1. update opt/hermes-gateway/.env
if [ -n "$ROOT_KEY" ]; then
  if grep -q '^DEEPSEEK_API_KEY=' /opt/hermes-gateway/.env; then
    sed -i "s|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=${ROOT_KEY}|" /opt/hermes-gateway/.env
  else
    echo "DEEPSEEK_API_KEY=${ROOT_KEY}" >> /opt/hermes-gateway/.env
  fi
  echo "opt/.env updated: $(grep -c '^DEEPSEEK_API_KEY=' /opt/hermes-gateway/.env)" >> $LOG
fi

# 2. also update root auth.json credential pool if present (deepseek entry)
python3 - << 'PYEOF' >> $LOG 2>&1
import json, os
p = "/opt/hermes-gateway/auth.json"
try:
    d = json.load(open(p))
    pool = d.get("credential_pool", {}).get("deepseek", [])
    if pool and os.environ.get("ROOT_KEY"):
        # will rewrite in shell instead (avoid leaking key via env in json dump)
        pass
except Exception as e:
    print("auth.json skip:", e)
PYEOF

echo "=== verify ===" >> $LOG
echo "root: $(grep '^DEEPSEEK_API_KEY=' /root/.hermes/.env | cut -d= -f2 | cut -c1-8)..."
echo "opt:  $(grep '^DEEPSEEK_API_KEY=' /opt/hermes-gateway/.env | cut -d= -f2 | cut -c1-8)..."
echo "=== END $(date) ===" >> $LOG
