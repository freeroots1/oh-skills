#!/usr/bin/env python3
import os, sys, json

HERMES_HOME = "/root/.hermes"
loader = os.path.join(HERMES_HOME, "skills/red-teaming/godmode/scripts/load_godmode.py")

# Load env
from dotenv import load_dotenv
env_path = os.path.join(HERMES_HOME, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

exec(open(loader).read())

api_key = os.getenv("DEEPSEEK_API_KEY", "")
print(f"DeepSeek key: {'found' if api_key else 'MISSING'}")

result = auto_jailbreak(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
)
print("=" * 50)
print(json.dumps({k: v for k, v in result.items() if k != 'attempts'}, ensure_ascii=False, indent=2, default=str)[:2000])
if result.get("attempts"):
    print("attempts:", json.dumps(result["attempts"], ensure_ascii=False)[:500])
print("=" * 50)
