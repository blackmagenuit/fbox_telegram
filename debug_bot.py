import requests
import os
from pathlib import Path
import json

# Cargar .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print(f"BOT_TOKEN: {BOT_TOKEN[:20]}...")
print(f"CHAT_ID: {CHAT_ID}")
print("\nObteniendo updates...")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

print(f"\nStatus: {data.get('ok')}")
print(f"Updates recibidos: {len(data.get('result', []))}")

if data.get('result'):
    print("\nÚltimos 3 mensajes:")
    for update in data['result'][-3:]:
        print(json.dumps(update, indent=2))
