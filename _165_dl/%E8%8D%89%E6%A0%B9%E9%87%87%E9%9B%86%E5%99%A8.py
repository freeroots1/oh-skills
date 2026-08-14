#!/usr/bin/env python3
"""
仿草根万能采集器规则引擎
支持: 站长之家/爱站权重榜 自动采集域名
规则语法: 与草根采集器兼容
"""
import subprocess, re, json, sys

# ============================================
# 采集规则定义 (类似草根采集器规则格式)
# ============================================
RULES = {
    # 规则1: 站长之家权重榜采集
    "chinaz_top": {
        "url": "https://top.chinaz.com/",
        "method": "GET",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "list_selector": 'href="https?://([^/"]+)"',  # 正则提取
        "filter": r"^(?!.*chinaz\.com|.*baidu\.com|.*google\.).*\\.[a-z]{2,}$",
        "output_field": "domain",
    },
    
    # 规则2: 爱站权重榜采集  
    "aizhan_top": {
        "url": "https://top.aizhan.com/",
        "method": "GET", 
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "list_selector": 'href="https?://([^/"]+)"',
        "filter": r"^(?!.*aizhan\.com|.*baidu\.com).*\\.[a-z]{2,}$",
        "output_field": "domain",
    },

    # 规则3: 爱站百度权重榜
    "aizhan_baidu": {
        "url": "https://baidurank.aizhan.com/",
        "method": "GET",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "list_selector": 'href="https?://([^/"]+)"',
        "filter": r"^(?!.*aizhan\.com|.*baidu\.com).*\\.[a-z]{2,}$",
        "output_field": "domain",
    },

    # 规则4: 站长之家Alexa排名
    "chinaz_alexa": {
        "url": "https://alexa.chinaz.com/",
        "method": "GET",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "list_selector": 'href="https?://([^/"]+)"',
        "filter": r"^(?!.*chinaz\.com|.*baidu\.com).*\\.[a-z]{2,}$",
        "output_field": "domain",
    },

    # 规则5: SEO综合查询-批量网站
    "5118_seo": {
        "url": "https://www.5118.com/baidu/",
        "method": "GET",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "list_selector": 'href="https?://([^/"]+)"',
        "filter": r"^(?!.*5118\.com|.*baidu\.com).*\\.[a-z]{2,}$",
        "output_field": "domain",
    },
}

def run_rule(rule_name, rule_config):
    """执行单条采集规则"""
    print(f"[规则] {rule_name}: {rule_config['url']}")
    try:
        r = subprocess.run(['curl', '-sk', '--connect-timeout', '15', '--max-time', '20',
            rule_config['url'], '-H', f"User-Agent: {rule_config['headers']['User-Agent']}"],
            capture_output=True, text=True, timeout=25)
        
        html = r.stdout
        if len(html) < 1000:
            print(f"  ⚠️ 页面太小({len(html)}B)")
            return set()
        
        # 应用CSS选择器(正则)
        pattern = rule_config['list_selector']
        matches = re.findall(pattern, html)
        
        # 过滤
        filter_pattern = rule_config.get('filter', '')
        domains = set()
        for m in matches:
            m_clean = m.replace("www.", "").strip()
            if not filter_pattern or re.match(filter_pattern, m_clean):
                domains.add(m_clean)
        
        print(f"  ✅ {len(domains)} 域名")
        return domains
    except Exception as e:
        print(f"  ❌ {e}")
        return set()

def main():
    """主程序 - 执行所有规则"""
    print("=" * 50)
    print("  草根采集器规则引擎 - 域名采集")
    print("=" * 50)
    
    all_domains = set()
    
    # 指定规则
    if len(sys.argv) > 1:
        for rule_name in sys.argv[1:]:
            if rule_name in RULES:
                all_domains.update(run_rule(rule_name, RULES[rule_name]))
    else:
        # 全部规则
        for rule_name, rule in RULES.items():
            all_domains.update(run_rule(rule_name, rule))
    
    # 去重输出
    with open("/tmp/collected_domains.txt", "w") as f:
        for d in sorted(all_domains):
            f.write(d + "\n")
    
    print(f"\n{'='*50}")
    print(f"总计: {len(all_domains)} 域名 → /tmp/collected_domains.txt")

if __name__ == "__main__":
    main()
