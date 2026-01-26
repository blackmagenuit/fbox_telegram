"""
Módulo para generar reportes de alertas en Excel
Uso: python generate_alerts_excel.py [--days 7]
"""

import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import argparse
import pandas as pd
from pathlib import Path

# Importar módulo de Dropbox storage
try:
    from dropbox_storage import storage as dropbox_storage
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False
    dropbox_storage = None

PARAGUAY_TZ = ZoneInfo("America/Asuncion")

# Cargar variables de entorno para ruta de Dropbox
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

DROPBOX_PATH = os.environ.get("DROPBOX_PATH", "")
STORAGE_PATH = Path(DROPBOX_PATH) if DROPBOX_PATH else Path(__file__).parent

ALERTS_HISTORY_FILE = str(STORAGE_PATH / "fbox_alerts_history.json")

def now_paraguay():
    """Retorna la hora actual en el huso horario de Paraguay"""
    return datetime.now(PARAGUAY_TZ)

def load_alerts_history():
    """Carga el historial de alertas desde el archivo JSON"""
    try:
        # Intentar leer desde Dropbox primero
        history = None
        if DROPBOX_AVAILABLE and dropbox_storage and dropbox_storage.is_available():
            history = dropbox_storage.read_json("fbox_alerts_history.json")
            if history:
                return history
        
        # Fallback a archivo local
        if os.path.exists(ALERTS_HISTORY_FILE):
            with open(ALERTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando historial de alertas: {e}")
    return []

def filter_alerts_by_days(alerts, days):
    """Filtra alertas por número de días hacia atrás"""
    if days <= 0:
        return alerts
    
    cutoff_date = now_paraguay() - timedelta(days=days)
    filtered = []
    
    for alert in alerts:
        try:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time >= cutoff_date:
                filtered.append(alert)
        except:
            continue
    
    return filtered

def categorize_alert(alert_text):
    """Categoriza el tipo de alerta basado en el texto"""
    alert_lower = alert_text.lower()
    
    if "offline" in alert_lower or "crítico" in alert_lower:
        return "CRÍTICO - Offline"
    elif "temperatura" in alert_lower:
        return "Temperatura Alta"
    elif "mineros caídos" in alert_lower:
        return "Mineros Caídos"
    elif "potencia" in alert_lower:
        return "Potencia Anormal"
    elif "inmersión" in alert_lower:
        return "Sistema Inmersión"
    elif "ventilador" in alert_lower:
        return "Ventilador"
    else:
        return "Otro"

def extract_container_from_alert(alert_text):
    """Extrae el nombre del contenedor de la alerta"""
    if "C01" in alert_text:
        return "C01"
    elif "C02" in alert_text:
        return "C02"
    else:
        return "N/A"

def generate_excel_report(days=7, output_file=None):
    """
    Genera un reporte de alertas en formato Excel
    
    Args:
        days: Número de días hacia atrás para incluir (0 = todas)
        output_file: Nombre del archivo de salida (opcional)
    """
    print(f"📊 Generando reporte de alertas...")
    
    # Cargar historial
    alerts = load_alerts_history()
    
    if not alerts:
        print("❌ No hay alertas registradas en el historial")
        return None
    
    # Filtrar por días si es necesario
    if days > 0:
        alerts = filter_alerts_by_days(alerts, days)
        print(f"📅 Filtrando alertas de los últimos {days} días")
    
    if not alerts:
        print(f"❌ No hay alertas en los últimos {days} días")
        return None
    
    # Preparar datos para DataFrame
    data = []
    for alert in alerts:
        timestamp = alert.get('timestamp', '')
        alert_messages = alert.get('alerts', [])
        
        try:
            dt = datetime.fromisoformat(timestamp)
            date_str = dt.strftime('%Y-%m-%d')
            time_str = dt.strftime('%H:%M:%S')
            weekday = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][dt.weekday()]
        except:
            date_str = timestamp
            time_str = ""
            weekday = ""
        
        for alert_msg in alert_messages:
            data.append({
                'Fecha': date_str,
                'Hora': time_str,
                'Día': weekday,
                'Contenedor': extract_container_from_alert(alert_msg),
                'Categoría': categorize_alert(alert_msg),
                'Alerta': alert_msg
            })
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Generar nombre de archivo si no se especifica
    if output_file is None:
        timestamp_str = now_paraguay().strftime('%Y%m%d_%H%M%S')
        output_file = str(STORAGE_PATH / f"fbox_alertas_{timestamp_str}.xlsx")
    
    # Crear archivo Excel con formato
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Hoja principal con todas las alertas
        df.to_excel(writer, sheet_name='Todas las Alertas', index=False)
        
        # Hoja de resumen por categoría
        summary_by_category = df.groupby('Categoría').size().reset_index(name='Cantidad')
        summary_by_category = summary_by_category.sort_values('Cantidad', ascending=False)
        summary_by_category.to_excel(writer, sheet_name='Resumen por Categoría', index=False)
        
        # Hoja de resumen por contenedor
        summary_by_container = df.groupby('Contenedor').size().reset_index(name='Cantidad')
        summary_by_container = summary_by_container.sort_values('Cantidad', ascending=False)
        summary_by_container.to_excel(writer, sheet_name='Resumen por Contenedor', index=False)
        
        # Hoja de resumen por día
        summary_by_date = df.groupby(['Fecha', 'Día']).size().reset_index(name='Cantidad')
        summary_by_date.to_excel(writer, sheet_name='Resumen por Día', index=False)
        
        # Ajustar ancho de columnas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 80)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Reporte generado: {output_file}")
    print(f"📊 Total de alertas: {len(data)}")
    print(f"📅 Período: {df['Fecha'].min()} - {df['Fecha'].max()}")
    
    return output_file

def print_summary():
    """Imprime un resumen de las alertas sin generar Excel"""
    alerts = load_alerts_history()
    
    if not alerts:
        print("❌ No hay alertas registradas")
        return
    
    total_alerts = sum(len(a.get('alerts', [])) for a in alerts)
    
    print(f"\n📊 RESUMEN DE ALERTAS")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total de eventos: {len(alerts)}")
    print(f"Total de alertas: {total_alerts}")
    
    if alerts:
        first = datetime.fromisoformat(alerts[0]['timestamp'])
        last = datetime.fromisoformat(alerts[-1]['timestamp'])
        print(f"Primer registro: {first.strftime('%Y-%m-%d %H:%M')}")
        print(f"Último registro: {last.strftime('%Y-%m-%d %H:%M')}")
    
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generar reporte de alertas FBOX en Excel')
    parser.add_argument('--days', type=int, default=7, 
                       help='Número de días hacia atrás (0 = todas las alertas)')
    parser.add_argument('--output', type=str, default=None,
                       help='Nombre del archivo de salida')
    parser.add_argument('--summary', action='store_true',
                       help='Solo mostrar resumen sin generar Excel')
    
    args = parser.parse_args()
    
    if args.summary:
        print_summary()
    else:
        generate_excel_report(days=args.days, output_file=args.output)
