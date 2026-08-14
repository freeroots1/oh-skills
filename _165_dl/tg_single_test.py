#!/usr/bin/env python3
"""单 getUpdates 长轮询挂 30s：检测是否有外部抢占者"""
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

async def main():
    token = get_token()
    req = HTTPXRequest()
    bot = Bot(token=token, get_updates_request=req)
    me = await bot.get_me()
    print(f"bot: @{me.username}", flush=True)

    print("[T1] 单 getUpdates timeout=28 挂起（无第二个请求），观察是否被外部 409", flush=True)
    try:
        ups = await asyncio.wait_for(bot.get_updates(timeout=28), timeout=32)
        print(f"[T1] 正常返回: updates={len(ups)} — 无外部抢占者", flush=True)
    except asyncio.TimeoutError:
        print("[T1] 超时（32s）— 连接挂起未返回，异常", flush=True)
    except Exception as e:
        print(f"[T1] ERR {type(e).__name__}: {str(e)[:200]} — 被外部抢占/409！", flush=True)

asyncio.run(main())
