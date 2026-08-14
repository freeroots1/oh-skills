#!/usr/bin/env python3
import sqlite3, sys, time
from datetime import datetime, timezone

def ts2str(ts):
    try:
        return datetime.fromtimestamp(float(ts), timezone.utc).strftime('%m-%d %H:%M')
    except Exception:
        return str(ts)

def show_tables(path):
    conn = sqlite3.connect(path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    print(f"=== {path} tables: {tables}")
    return conn, tables

# 1. state.db 表结构
conn, tables = show_tables('/root/.hermes/state.db')
for t in tables:
    try:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})")]
        cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {len(cols)} cols, {cnt} rows | {cols}")
    except Exception as e:
        print(f"  {t}: ERR {e}")

# 2. cron executions.db
conn2, tables2 = show_tables('/root/.hermes/cron/executions.db')
for t in tables2:
    try:
        cols = [r[1] for r in conn2.execute(f"PRAGMA table_info({t})")]
        cnt = conn2.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {len(cols)} cols, {cnt} rows | {cols}")
    except Exception as e:
        print(f"  {t}: ERR {e}")
