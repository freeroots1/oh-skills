cd /usr/local/lib/hermes-agent
HASH=$(venv/bin/python -c 'from plugins.dashboard_auth.basic import hash_password; print(hash_password("hermes123"))')
echo "$HASH" > /tmp/hash.txt
echo "HASH_SAVED"
