#!/usr/bin/env python3
"""
Script para enviar mensaje de actualización a Telegram
"""
import os
from pathlib import Path
from fbox_telegram import send_telegram

# Cargar variables de entorno
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

mensaje = """🔧 ACTUALIZACIÓN DEL BOT

Se ha corregido el problema del reporte semanal que se enviaba cada hora.

✅ Cambios:
• Simplificada la lógica de verificación
• Agregado seguimiento persistente del último reporte
• Ahora se envía UNA SOLA VEZ por semana (cada lunes)

📅 Próximo reporte semanal: Próximo lunes a las 00:00 UTC

¡Gracias por reportar el issue! 🚀"""

print("📤 Enviando mensaje a Telegram...")
send_telegram(mensaje)
print("✅ Mensaje enviado")
