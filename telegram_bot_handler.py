"""
Bot handler para comandos de Telegram
Ejecutar este script para activar el bot y responder a comandos como /resumen
"""

import requests
import os
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Importar módulo de Dropbox storage
try:
    from dropbox_storage import storage as dropbox_storage
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False
    dropbox_storage = None

# Cargar variables de entorno
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
PARAGUAY_TZ = ZoneInfo("America/Asuncion")

# Archivo para rastrear último update procesado
LAST_UPDATE_FILE = "last_telegram_update.json"

def now_paraguay():
    """Retorna la hora actual en el huso horario de Paraguay"""
    return datetime.now(PARAGUAY_TZ)

def send_telegram_message(text, chat_id=None):
    """Envía un mensaje de texto a Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id or CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return None

def send_telegram_document(file_path, caption=None, chat_id=None):
    """Envía un archivo (documento) a Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    
    try:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': chat_id or CHAT_ID}
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, data=data, files=files, timeout=30)
            return response.json()
    except Exception as e:
        print(f"Error enviando documento: {e}")
        return None

def set_bot_commands():
    """Configura la lista de comandos del bot para que aparezcan en Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    
    commands = [
        {"command": "resumen", "description": "Ver resumen de alertas"},
        {"command": "resumen7", "description": "Excel de últimos 7 días"},
        {"command": "resumen30", "description": "Excel de últimos 30 días"},
        {"command": "resumentodo", "description": "Excel completo"},
        {"command": "semanal", "description": "Reporte semanal de estadísticas"},
        {"command": "ayuda", "description": "Mostrar ayuda"}
    ]
    
    try:
        response = requests.post(url, json={"commands": commands}, timeout=10)
        result = response.json()
        if result.get("ok"):
            print("✅ Comandos del bot configurados correctamente")
        else:
            print(f"⚠️ Error configurando comandos: {result}")
        return result
    except Exception as e:
        print(f"❌ Error configurando comandos: {e}")
        return None

def generate_excel_report(days=7):
    """Genera el reporte Excel y retorna la ruta del archivo"""
    from generate_alerts_excel import generate_excel_report as gen_excel
    
    try:
        output_file = gen_excel(days=days)
        return output_file
    except Exception as e:
        print(f"Error generando Excel: {e}")
        return None

def get_alerts_summary():
    """Obtiene un resumen de las alertas registradas"""
    ALERTS_HISTORY_FILE = "fbox_alerts_history.json"
    
    try:
        # Intentar leer desde Dropbox primero
        history = None
        if DROPBOX_AVAILABLE and dropbox_storage and dropbox_storage.is_available():
            history = dropbox_storage.read_json(ALERTS_HISTORY_FILE)
        
        # Fallback a archivo local
        if history is None:
            if not os.path.exists(ALERTS_HISTORY_FILE):
                return "📊 No hay alertas registradas aún."
            
            with open(ALERTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        if not history:
            return "📊 No hay alertas registradas aún."
        
        total_alerts = sum(len(a.get('alerts', [])) for a in history)
        
        first = datetime.fromisoformat(history[0]['timestamp'])
        last = datetime.fromisoformat(history[-1]['timestamp'])
        
        msg = "📊 RESUMEN DE ALERTAS\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Total eventos: {len(history)}\n"
        msg += f"Total alertas: {total_alerts}\n"
        msg += f"Primer registro: {first.strftime('%Y-%m-%d %H:%M')}\n"
        msg += f"Último registro: {last.strftime('%Y-%m-%d %H:%M')}\n\n"
        msg += "📥 Usa /resumen7 para Excel de 7 días\n"
        msg += "📥 Usa /resumen30 para Excel de 30 días\n"
        msg += "📥 Usa /resumentodo para todas las alertas"
        
        return msg
    except Exception as e:
        return f"❌ Error obteniendo resumen: {e}"

def load_last_update_id():
    """Carga el último update_id procesado"""
    try:
        if os.path.exists(LAST_UPDATE_FILE):
            with open(LAST_UPDATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("last_update_id", 0)
    except:
        pass
    return 0

def save_last_update_id(update_id):
    """Guarda el último update_id procesado"""
    try:
        with open(LAST_UPDATE_FILE, 'w') as f:
            json.dump({"last_update_id": update_id}, f)
    except:
        pass

def get_telegram_updates(offset=None):
    """Obtiene actualizaciones (mensajes) del bot"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {
        "timeout": 30,
        "allowed_updates": ["message"]
    }
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Error obteniendo updates: {e}")
        return None

def process_command(command, chat_id):
    """Procesa un comando recibido"""
    command = command.lower().strip()
    
    if command == "/resumen":
        # Enviar resumen de texto
        summary = get_alerts_summary()
        send_telegram_message(summary, chat_id)
    
    elif command == "/resumen7":
        # Generar y enviar Excel de 7 días
        send_telegram_message("⏳ Generando reporte de últimos 7 días...", chat_id)
        excel_file = generate_excel_report(days=7)
        if excel_file and os.path.exists(excel_file):
            send_telegram_document(excel_file, caption="📊 Reporte de alertas - Últimos 7 días", chat_id=chat_id)
            send_telegram_message(f"✅ Reporte guardado en: {excel_file}", chat_id)
        else:
            send_telegram_message("❌ Error generando el reporte. Verifica que haya alertas registradas.", chat_id)
    
    elif command == "/resumen30":
        # Generar y enviar Excel de 30 días
        send_telegram_message("⏳ Generando reporte de últimos 30 días...", chat_id)
        excel_file = generate_excel_report(days=30)
        if excel_file and os.path.exists(excel_file):
            send_telegram_document(excel_file, caption="📊 Reporte de alertas - Últimos 30 días", chat_id=chat_id)
            send_telegram_message(f"✅ Reporte guardado en: {excel_file}", chat_id)
        else:
            send_telegram_message("❌ Error generando el reporte. Verifica que haya alertas registradas.", chat_id)
    
    elif command == "/resumentodo":
        # Generar y enviar Excel con todas las alertas
        send_telegram_message("⏳ Generando reporte completo...", chat_id)
        excel_file = generate_excel_report(days=0)
        if excel_file and os.path.exists(excel_file):
            send_telegram_document(excel_file, caption="📊 Reporte de alertas - Historial completo", chat_id=chat_id)
            send_telegram_message(f"✅ Reporte guardado en: {excel_file}", chat_id)
        else:
            send_telegram_message("❌ Error generando el reporte. Verifica que haya alertas registradas.", chat_id)
    
    elif command == "/semanal":
        # Enviar reporte semanal de estadísticas
        try:
            # Importar las funciones necesarias
            import sys
            sys.path.insert(0, os.path.dirname(__file__))
            from fbox_telegram import generate_weekly_report
            
            send_telegram_message("⏳ Generando reporte semanal...", chat_id)
            weekly_msg = generate_weekly_report()
            send_telegram_message(weekly_msg, chat_id)
            send_telegram_message("✅ Reporte semanal enviado", chat_id)
        except Exception as e:
            send_telegram_message(f"❌ Error generando reporte semanal: {e}", chat_id)
    
    elif command == "/ayuda" or command == "/help":
        help_msg = "🤖 COMANDOS DISPONIBLES\n"
        help_msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        help_msg += "/resumen - Ver resumen de alertas\n"
        help_msg += "/resumen7 - Excel de últimos 7 días\n"
        help_msg += "/resumen30 - Excel de últimos 30 días\n"
        help_msg += "/resumentodo - Excel completo\n"
        help_msg += "/semanal - Reporte semanal de estadísticas\n"
        help_msg += "/ayuda - Mostrar esta ayuda"
        send_telegram_message(help_msg, chat_id)
    
    else:
        send_telegram_message(f"❓ Comando desconocido: {command}\nUsa /ayuda para ver comandos disponibles.", chat_id)

def run_bot():
    """Ejecuta el bot en modo polling"""
    print(f"🤖 Bot iniciado - {now_paraguay()}")
    
    # Configurar comandos del bot
    set_bot_commands()
    
    print("Esperando comandos...")
    
    offset = load_last_update_id() + 1
    
    while True:
        try:
            updates = get_telegram_updates(offset=offset)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    update_id = update.get("update_id")
                    message = update.get("message", {})
                    text = message.get("text", "")
                    chat_id = message.get("chat", {}).get("id")
                    chat_type = message.get("chat", {}).get("type", "")
                    
                    # Procesar comandos de cualquier chat privado O del canal/grupo configurado
                    if text.startswith("/") and (chat_type == "private" or str(chat_id) == str(CHAT_ID)):
                        print(f"📩 Comando recibido de {chat_id}: {text}")
                        # Enviar respuesta al mismo chat que envió el comando
                        process_command(text, chat_id)
                    
                    # Actualizar offset
                    offset = update_id + 1
                    save_last_update_id(update_id)
            
            time.sleep(1)  # Esperar 1 segundo antes de la próxima consulta
        
        except KeyboardInterrupt:
            print("\n👋 Bot detenido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error en el bot: {e}")
            time.sleep(5)  # Esperar 5 segundos antes de reintentar

if __name__ == "__main__":
    # Verificar que las dependencias estén instaladas
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("❌ Error: Falta instalar dependencias")
        print("Ejecuta: pip install pandas openpyxl")
        exit(1)
    
    # Verificar configuración
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Error: Falta configurar BOT_TOKEN y CHAT_ID en .env")
        exit(1)
    
    # Health check handler para Render
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running')
        
        def log_message(self, format, *args):
            pass  # Silenciar logs de HTTP
    
    # Iniciar servidor HTTP en thread separado para health checks
    def start_http_server():
        port = int(os.environ.get('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"✅ Health check server running on port {port}")
        server.serve_forever()
    
    # Iniciar servidor HTTP en background
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Iniciar bot (este es el proceso principal)
    run_bot()
