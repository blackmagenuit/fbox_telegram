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

AREA = "10000013"

cookies = {
    "lang": "en-us",
    "language": "en",
    "ssid": os.environ.get("FBOX_SSID"),
    "Admin-Token": os.environ.get("FBOX_ADMIN_TOKEN")
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "http://america.fboxdata.com/"
}

print("🔍 Testing API connection...")
print(f"SSID: {cookies['ssid'][:10]}...")
print(f"Admin-Token: {cookies['Admin-Token'][:10]}...\n")

# Test C01
container_id = 290
url = f"http://america.fboxdata.com/api/index/fbox.boxlist/detail?output=json&area_id={AREA}&id={container_id}"

print(f"📡 Testing C01 (ID: {container_id})")
print(f"URL: {url}\n")

try:
    print("Cookies being sent:")
    print(f"  ssid={cookies['ssid']}")
    print(f"  Admin-Token={cookies['Admin-Token']}")
    print()
    
    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    # Verificar cookies en la respuesta
    print(f"Set-Cookie header: {response.headers.get('Set-Cookie', 'None')}")
    
    print("\nResponse JSON:")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    print("\n" + "="*50 + "\n")
    
    if data.get("code") == 1:
        print("✅ API respondió correctamente")
        d = data.get("data", {})
        print(f"Mineros online: {d.get('miner_online')}")
        print(f"Mineros offline: {d.get('miner_offline')}")
    else:
        print("❌ API respondió con error")
        print(f"Code: {data.get('code')}")
        print(f"Message: {data.get('msg')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
