#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('/root/.hermes/state.db')
conn.row_factory = sqlite3.Row

def ts(t):
    try:
        return datetime.fromtimestamp(float(t), timezone.utc).strftime('%m-%d %H:%M:%S')
    except Exception:
        return str(t)

print('=== MESSAGES 时间分布（全部 173 条，只看 8/7 之后）===')
n = 0
for r in conn.execute("SELECT timestamp, role, token_count, session_id, substr(content,1,70) AS c FROM messages ORDER BY timestamp"):
    t = ts(r['timestamp'])
    if t >= '08-07':
        n += 1
        print(f"{t} {r['role']:10s} tok={r['token_count']} sess={r['session_id'][:14]} | {r['c']!r}")
print(f"8/7 之后共 {n} 条")

print()
print('=== 8/8 02:00-05:00 UTC 前后的消息（含前后各几条做参考）===')
rows = conn.execute("SELECT timestamp, role, token_count, session_id, substr(content,1,90) AS c FROM messages ORDER BY timestamp").fetchall()
for r in rows:
    t = ts(r['timestamp'])
    if '08-08 01:5' <= t <= '08-08 05:30':
        print(f"{t} {r['role']:10s} tok={r['token_count']} sess={r['session_id'][:14]} | {r['c']!r}")

print()
print('=== 最后一条消息时间 ===')
r = conn.execute("SELECT MAX(timestamp) FROM messages").fetchone()
print(f"MAX(timestamp) = {r[0]} -> {ts(r[0])}")
