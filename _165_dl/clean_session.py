#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/root/.hermes/state.db')
sid = '20260803_142517_690c4510'

# 删除前确认
r = conn.execute("SELECT id, title, message_count, input_tokens, output_tokens, cache_read_tokens, estimated_cost_usd FROM sessions WHERE id=?", (sid,)).fetchone()
print("删除前:", r)

for t in ['messages', 'session_model_usage']:
    n = conn.execute(f"DELETE FROM {t} WHERE session_id=?", (sid,)).rowcount
    print(f"DELETE {t}: {n}")

n = conn.execute("DELETE FROM sessions WHERE id=?", (sid,)).rowcount
print(f"DELETE sessions: {n}")

# 清理该会话的 delivery_obligations（按 session_key 模糊匹配）
n = conn.execute("DELETE FROM delivery_obligations WHERE session_key LIKE ?", (f"%{sid}%",)).rowcount
print(f"DELETE delivery_obligations: {n}")

conn.commit()

# 验证
r = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()
print("剩余 sessions:", r[0])
r = conn.execute("SELECT COUNT(*) FROM messages").fetchone()
print("剩余 messages:", r[0])
