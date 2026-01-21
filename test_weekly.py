import sys
sys.path.insert(0, 'c:/Users/cabja/OneDrive/Documents/fbox_telegram_repo')

from fbox_telegram import generate_weekly_report, send_telegram, save_to_history
import json

# Crear datos de prueba
test_data = {
    "C01": {
        "code": 1,
        "miner_online": 150,
        "miner_offline": 10,
        "oil_temp": 45.5,
        "container_temp": 42.3,
        "hashrate_ph": 46.8,
        "power_kw": 885.2,
        "fan_status": "on",
        "fan_speed": 2500,
        "fan_temp": 35.0
    },
    "C02": {
        "code": 1,
        "miner_online": 148,
        "miner_offline": 12,
        "oil_temp": 43.2,
        "container_temp": 41.8,
        "hashrate_ph": 47.1,
        "power_kw": 920.5,
        "fan_status": "on",
        "fan_speed": 2600,
        "fan_temp": 34.5
    }
}

print("Generando 50 registros de prueba...")
for i in range(50):
    save_to_history(test_data)

print("\nGenerando reporte semanal...")
weekly_msg = generate_weekly_report()

print("\n" + "="*60)
print(weekly_msg)
print("="*60)

print("\nEnviando a Telegram...")
send_telegram(weekly_msg)
print("✅ Reporte semanal de prueba enviado!")
