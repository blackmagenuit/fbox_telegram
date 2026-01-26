"""
Script para obtener tu CHAT_ID de Telegram
"""
import requests
import os
from pathlib import Path

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

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

print("\n" + "="*50)
print("CHAT IDs detectados:")
print("="*50)

if data.get("ok") and data.get("result"):
    chat_ids = set()
    for update in data["result"]:
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            chat_type = update["message"]["chat"]["type"]
            chat_title = update["message"]["chat"].get("title", update["message"]["chat"].get("first_name", ""))
            chat_ids.add((chat_id, chat_type, chat_title))
    
    for chat_id, chat_type, title in chat_ids:
        print(f"\nChat ID: {chat_id}")
        print(f"Tipo: {chat_type}")
        print(f"Nombre: {title}")
else:
    print("No se detectaron mensajes recientes")
    print("Envía un mensaje al bot primero (ej: /start)")

print("\n" + "="*50)
print("\nTu CHAT_ID configurado actualmente:")
print(f"CHAT_ID = {os.environ.get('CHAT_ID')}")
print("="*50 + "\n")
