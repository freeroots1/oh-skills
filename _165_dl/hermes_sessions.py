#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('/root/.hermes/state.db')
conn.row_factory = sqlite3.Row

def ts(ts):
    try:
        return datetime.fromtimestamp(float(ts), timezone.utc).strftime('%m-%d %H:%M:%S')
    except Exception:
        return str(ts)

print("=" * 100)
print("SESSIONS (全部)")
print("=" * 100)
for r in conn.execute("SELECT id, source, title, model, started_at, ended_at, message_count, api_call_count, input_tokens, output_tokens, reasoning_tokens, cache_read_tokens, cache_write_tokens, estimated_cost_usd, end_reason FROM sessions ORDER BY started_at"):
    print(f"ID: {r['id']}")
    print(f"  source={r['source']} | title={r['title']!r} | model={r['model']}")
    print(f"  时间: {ts(r['started_at'])} -> {ts(r['ended_at']) if r['ended_at'] else 'N/A'} | end_reason={r['end_reason']}")
    print(f"  消息={r['message_count']} | API调用={r['api_call_count']}")
    print(f"  tokens: in={r['input_tokens']} out={r['output_tokens']} reasoning={r['reasoning_tokens']} cache_read={r['cache_read_tokens']} cache_write={r['cache_write_tokens']}")
    print(f"  费用≈${r['estimated_cost_usd']}")
    print("-" * 60)

print()
print("=" * 100)
print("SESSION_MODEL_USAGE (按session+model)")
print("=" * 100)
for r in conn.execute("SELECT session_id, model, task, api_call_count, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens, estimated_cost_usd, first_seen, last_seen FROM session_model_usage ORDER BY first_seen"):
    print(f"session={r['session_id'][:20]}... model={r['model']} task={r['task']}")
    print(f"  api={r['api_call_count']} in={r['input_tokens']} out={r['output_tokens']} cache_r={r['cache_read_tokens']} cache_w={r['cache_write_tokens']} reasoning={r['reasoning_tokens']} cost=${r['estimated_cost_usd']}")
    print(f"  first={ts(r['first_seen'])} last={ts(r['last_seen'])}")
    print("-" * 60)

print()
print("=" * 100)
print("MESSAGES 按小时聚合 (昨天=08-07 16:00 UTC ~ 08-08 16:00 UTC)")
print("=" * 100)
rows = conn.execute("SELECT timestamp, token_count, role, session_id, substr(content,1,60) AS c FROM messages ORDER BY timestamp").fetchall()
from collections import Counter
hourly = Counter()
for r in rows:
    t = ts(r['timestamp'])[:5] if r['timestamp'] else '??'
    hourly[t] += 1
for h in sorted(hourly):
    print(f"  {h} UTC: {hourly[h]} 条消息")
