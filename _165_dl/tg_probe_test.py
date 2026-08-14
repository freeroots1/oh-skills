#!/usr/bin/env python3
"""最小复现：并发两个 getUpdates 长轮询，观察 409 行为"""
import asyncio
import sys

sys.path.insert(0, '/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages')
from telegram import Bot
from telegram.request import HTTPXRequest

def get_token():
    for line in open('/root/.hermes/.env'):
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            return line.strip().split('=', 1)[1]
    raise SystemExit('no token')

async def poll_once(bot, i, timeout):
    try:
        ups = await bot.get_updates(timeout=timeout)
        print(f"[poll {i}] OK updates={len(ups)} (timeout={timeout})", flush=True)
        return ('ok', i)
    except Exception as e:
        print(f"[poll {i}] ERR {type(e).__name__}: {str(e)[:180]}", flush=True)
        return ('err', i, str(e)[:180])

async def main():
    token = get_token()
    req = HTTPXRequest()
    bot = Bot(token=token, get_updates_request=req)
    me = await bot.get_me()
    print(f"bot: @{me.username} (id={me.id})", flush=True)

    print("=== 测试1: 串行两次长轮询（第一次挂起中第二次发起）===", flush=True)
    # 第一次长轮询挂起（25s），1秒后第二次发起
    t1 = asyncio.create_task(poll_once(bot, 'A-25s', 25))
    await asyncio.sleep(1)
    t2 = asyncio.create_task(poll_once(bot, 'B-0s', 0))
    r = await asyncio.gather(t1, t2, return_exceptions=True)
    print(f"结果: {r}", flush=True)

    await asyncio.sleep(3)
    print("=== 测试2: 两个并发长轮询（25s）===", flush=True)
    r2 = await asyncio.gather(
        asyncio.create_task(poll_once(bot, 'C-25s', 25)),
        asyncio.create_task(poll_once(bot, 'D-25s', 25)),
        return_exceptions=True,
    )
    print(f"结果: {r2}", flush=True)

asyncio.run(main())
