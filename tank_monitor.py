import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path

# ---------------- CARGAR .env SI EXISTE ----------------
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# ---------------- TELEGRAM ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ---------------- TIMEZONE ----------------
PARAGUAY_TZ = ZoneInfo("America/Asuncion")

def now_paraguay():
    """Retorna la hora actual en el huso horario de Paraguay"""
    return datetime.now(PARAGUAY_TZ)

def send_telegram(msg):
    """Envía un mensaje a Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ---------------- CONFIGURACIÓN FBOX ----------------
AREA = "10000013"
BASE = "http://america.fboxdata.com/api/index/fbox.boxlist"

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

# ============ UMBRALES DE ALERTA PARA TANQUES ============
TANK_TEMP_ALERT = 58  # °C - temperatura crítica del aceite
TANK_TEMP_WARNING = 52  # °C - temperatura de advertencia
TANK_LEVEL_MIN = 75   # % - nivel mínimo de aceite
TANK_LEVEL_CRITICAL = 60  # % - nivel crítico de aceite
IMMERSION_MIN = 88    # % - porcentaje mínimo de inmersión
IMMERSION_CRITICAL = 80  # % - porcentaje crítico de inmersión
OIL_FLOW_MIN = 8  # L/min - flujo mínimo de aceite
OIL_FLOW_CRITICAL = 3  # L/min - flujo crítico
PRESSURE_MIN = 0.8  # bar - presión mínima
PRESSURE_MAX = 4.5  # bar - presión máxima
TEMP_DIFF_MAX = 15  # °C - diferencia máxima temp aceite vs tanque
COOLING_EFFICIENCY_MIN = 70  # % - eficiencia mínima de enfriamiento

# ============ ARCHIVO DE ESTADO ============
TANK_STATE_FILE = "tank_state.json"

def fetch_json(url):
    """Obtiene JSON desde la API"""
    r = requests.get(url, headers=headers, cookies=cookies, timeout=30)
    ct = r.headers.get("Content-Type", "")
    if r.status_code != 200 or "application/json" not in ct:
        return {
            "__error__": True,
            "status": r.status_code,
            "content_type": ct,
            "body_head": r.text[:200]
        }
    try:
        return r.json()
    except Exception:
        return {
            "__error__": True,
            "status": r.status_code,
            "content_type": ct,
            "body_head": r.text[:200]
        }

def get_detail(container_id):
    """Obtiene detalle del contenedor desde la API"""
    candidates = [
        "http://america.fboxdata.com/api/index/fbox.boxlist/detail",
        "http://america.fboxdata.com/api/index/fbox.boxdetail/detail",
        "http://america.fboxdata.com/api/index/fbox.boxinfo/detail",
        "http://america.fboxdata.com/api/index/fbox.box/detail",
        "http://america.fboxdata.com/api/index/fbox.boxlist/index",
    ]

    params = f"?output=json&area_id={AREA}&id={container_id}"

    last_err = None
    for base_url in candidates:
        url = base_url + params
        out = fetch_json(url)
        if isinstance(out, dict) and not out.get("__error__"):
            out["__endpoint__"] = base_url
            return out
        last_err = out

    if isinstance(last_err, dict):
        last_err["__tried__"] = candidates
    return last_err

def to_float(x):
    """Convierte a float, retorna None si es inválido"""
    try:
        v = float(x)
        return None if v <= -900 else v
    except:
        return None

def calc_oil_temp(detail_json):
    """Calcula temperatura promedio del aceite"""
    data = detail_json.get("data") or {}
    sub_boxes = data.get("sub_box_list") or []

    temps = []
    for sb in sub_boxes:
        for t in (sb.get("main_temperatures") or []):
            v = to_float(t.get("num"))
            if v is not None:
                temps.append(v)

    if not temps:
        return None

    return round(sum(temps) / len(temps), 1)

def extract_tank_data(detail_json):
    """Extrae datos específicos del tanque desde el JSON"""
    data = detail_json.get("data")
    if not data:
        info_str = detail_json.get("info")
        if info_str and isinstance(info_str, str):
            try:
                data = json.loads(info_str)
            except:
                data = {}
        else:
            data = info_str if isinstance(info_str, dict) else {}
    
    if not isinstance(data, dict):
        data = {}
    
    # Temperatura del aceite
    oil_temp = calc_oil_temp(detail_json)
    
    # Estado de inmersión
    immersion_status = data.get("immersion_status") or data.get("immersion")
    immersion_str = str(immersion_status) if immersion_status else "N/A"
    
    # Porcentaje de inmersión
    immersion_percent = to_float(data.get("immersion_percent"))
    
    # Nivel del tanque (si está disponible)
    tank_level = to_float(data.get("tank_level") or data.get("oil_level"))
    
    # Flujo de aceite (si está disponible)
    oil_flow = to_float(data.get("oil_flow") or data.get("flow_rate"))
    
    # Presión del sistema (si está disponible)
    pressure = to_float(data.get("pressure") or data.get("system_pressure"))
    
    # Temperatura del tanque/ambiente
    tank_temp = to_float(data.get("fbox_temp"))
    
    # Estado de bombas
    pump_status = data.get("pump_status") or data.get("pump_state")
    pump_str = str(pump_status) if pump_status else "N/A"
    
    # RPM de bombas
    pump_rpm = to_float(data.get("pump_rpm"))
    
    # Estado de filtros
    filter_status = data.get("filter_status") or data.get("filter_state")
    filter_str = str(filter_status) if filter_status else "N/A"
    
    # Presión diferencial del filtro
    filter_diff_pressure = to_float(data.get("filter_diff_pressure"))
    
    # Temperatura de entrada y salida (para calcular eficiencia)
    temp_inlet = to_float(data.get("temp_inlet") or data.get("inlet_temp"))
    temp_outlet = to_float(data.get("temp_outlet") or data.get("outlet_temp"))
    
    # Calcular diferencia de temperatura y eficiencia de enfriamiento
    temp_diff = None
    cooling_efficiency = None
    if oil_temp is not None and tank_temp is not None:
        temp_diff = round(abs(oil_temp - tank_temp), 1)
        # Eficiencia de enfriamiento = cuánto se enfría respecto a la diferencia ideal
        if oil_temp > tank_temp:
            ideal_diff = 20  # diferencia ideal de temperatura
            actual_cooling = oil_temp - tank_temp
            cooling_efficiency = round((actual_cooling / ideal_diff) * 100, 1)
            if cooling_efficiency > 100:
                cooling_efficiency = 100
    
    # Obtener más temperaturas del sub_box_list para análisis
    sub_boxes = data.get("sub_box_list") or []
    all_temps = []
    for sb in sub_boxes:
        for t in (sb.get("main_temperatures") or []):
            v = to_float(t.get("num"))
            if v is not None:
                all_temps.append(v)
    
    temp_min = min(all_temps) if all_temps else None
    temp_max = max(all_temps) if all_temps else None
    temp_range = round(temp_max - temp_min, 1) if (temp_max and temp_min) else None
    
    return {
        "oil_temp": oil_temp,
        "immersion_status": immersion_str,
        "immersion_percent": immersion_percent,
        "tank_level": tank_level,
        "oil_flow": oil_flow,
        "pressure": pressure,
        "tank_temp": tank_temp,
        "pump_status": pump_str,
        "pump_rpm": pump_rpm,
        "filter_status": filter_str,
        "filter_diff_pressure": filter_diff_pressure,
        "temp_inlet": temp_inlet,
        "temp_outlet": temp_outlet,
        "temp_diff": temp_diff,
        "cooling_efficiency": cooling_efficiency,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "temp_range": temp_range
    }

def check_tank_status():
    """Verifica el estado de los tanques de todos los contenedores"""
    containers_data = {"C01": 290, "C02": 291}
    msg = "🛢️ ESTADO DE TANQUES\n"
    msg += f"{now_paraguay().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    state = {}

    for name, cid in containers_data.items():
        detail = get_detail(cid)

        if isinstance(detail, dict) and detail.get("__error__"):
            msg += f"🔹 {name}\n"
            msg += "⚠️ Error leyendo datos del tanque\n\n"
            state[name] = {"error": True}
            continue

        # Extraer datos del tanque
        tank_data = extract_tank_data(detail)
        
        status_icon = "🟢 ONLINE" if (detail.get("code") == 1) else "🔴 OFFLINE"
        
        msg += f"🔹 {name}\n"
        msg += f"{status_icon}\n"
        
        # Temperatura del aceite
        if tank_data["oil_temp"] is not None:
            if tank_data["oil_temp"] >= TANK_TEMP_ALERT:
                temp_icon = "🔴"
            elif tank_data["oil_temp"] >= TANK_TEMP_WARNING:
                temp_icon = "🟡"
            else:
                temp_icon = "🔥"
            msg += f"{temp_icon} Aceite: {tank_data['oil_temp']} °C"
            # Mostrar rango de temperaturas si está disponible
            if tank_data["temp_min"] and tank_data["temp_max"]:
                msg += f" (rango: {tank_data['temp_min']}-{tank_data['temp_max']} °C)\n"
            else:
                msg += "\n"
        else:
            msg += "🔥 Aceite: N/A\n"
        
        # Temperatura del tanque/ambiente
        if tank_data["tank_temp"] is not None:
            msg += f"🌡️ Tanque: {tank_data['tank_temp']} °C"
            # Mostrar diferencia de temperatura
            if tank_data["temp_diff"] is not None:
                diff_icon = "⚠️" if tank_data["temp_diff"] > TEMP_DIFF_MAX else ""
                msg += f" (Δ{tank_data['temp_diff']}°C) {diff_icon}\n"
            else:
                msg += "\n"
        
        # Eficiencia de enfriamiento
        if tank_data["cooling_efficiency"] is not None:
            eff_icon = "⚠️" if tank_data["cooling_efficiency"] < COOLING_EFFICIENCY_MIN else "❄️"
            msg += f"{eff_icon} Enfriamiento: {tank_data['cooling_efficiency']}%\n"
        
        # Estado de inmersión
        msg += f"💧 Inmersión: {tank_data['immersion_status']}"
        if tank_data["immersion_percent"] is not None:
            if tank_data["immersion_percent"] < IMMERSION_CRITICAL:
                immersion_icon = "🔴"
            elif tank_data["immersion_percent"] < IMMERSION_MIN:
                immersion_icon = "⚠️"
            else:
                immersion_icon = "✅"
            msg += f" ({tank_data['immersion_percent']}%) {immersion_icon}\n"
        else:
            msg += "\n"
        
        # Nivel del tanque
        if tank_data["tank_level"] is not None:
            if tank_data["tank_level"] < TANK_LEVEL_CRITICAL:
                level_icon = "🔴"
            elif tank_data["tank_level"] < TANK_LEVEL_MIN:
                level_icon = "⚠️"
            else:
                level_icon = "📊"
            msg += f"{level_icon} Nivel: {tank_data['tank_level']}%\n"
        
        # Flujo de aceite
        if tank_data["oil_flow"] is not None:
            if tank_data["oil_flow"] < OIL_FLOW_CRITICAL:
                flow_icon = "🔴"
            elif tank_data["oil_flow"] < OIL_FLOW_MIN:
                flow_icon = "⚠️"
            else:
                flow_icon = "🌊"
            msg += f"{flow_icon} Flujo: {tank_data['oil_flow']} L/min\n"
        
        # Presión del sistema
        if tank_data["pressure"] is not None:
            if tank_data["pressure"] < PRESSURE_MIN or tank_data["pressure"] > PRESSURE_MAX:
                pressure_icon = "🔴"
            else:
                pressure_icon = "💪"
            msg += f"{pressure_icon} Presión: {tank_data['pressure']} bar\n"
        
        # Estado de bombas
        if tank_data["pump_status"] != "N/A":
            pump_icon = "⚙️" if "on" in tank_data["pump_status"].lower() else "⚠️"
            msg += f"{pump_icon} Bombas: {tank_data['pump_status']}"
            if tank_data["pump_rpm"]:
                msg += f" ({tank_data['pump_rpm']} RPM)"
            msg += "\n"
        
        # Estado de filtros
        if tank_data["filter_status"] != "N/A":
            filter_icon = "🔍" if "ok" in tank_data["filter_status"].lower() else "⚠️"
            msg += f"{filter_icon} Filtros: {tank_data['filter_status']}"
            if tank_data["filter_diff_pressure"]:
                msg += f" (ΔP: {tank_data['filter_diff_pressure']} bar)"
            msg += "\n"
        
        # Temperaturas de entrada/salida si están disponibles
        if tank_data["temp_inlet"] is not None or tank_data["temp_outlet"] is not None:
            msg += "🔄 "
            if tank_data["temp_inlet"] is not None:
                msg += f"In: {tank_data['temp_inlet']}°C "
            if tank_data["temp_outlet"] is not None:
                msg += f"Out: {tank_data['temp_outlet']}°C"
            msg += "\n"
        
        msg += "\n"

        # Guardar estado completo
        state[name] = {
            "code": detail.get("code"),
            "oil_temp": tank_data["oil_temp"],
            "tank_temp": tank_data["tank_temp"],
            "immersion_status": tank_data["immersion_status"],
            "immersion_percent": tank_data["immersion_percent"],
            "tank_level": tank_data["tank_level"],
            "oil_flow": tank_data["oil_flow"],
            "pressure": tank_data["pressure"],
            "pump_status": tank_data["pump_status"],
            "pump_rpm": tank_data["pump_rpm"],
            "filter_status": tank_data["filter_status"],
            "filter_diff_pressure": tank_data["filter_diff_pressure"],
            "temp_diff": tank_data["temp_diff"],
            "cooling_efficiency": tank_data["cooling_efficiency"],
            "temp_range": tank_data["temp_range"]
        }

    return msg, state

def detect_tank_alerts(old_state, new_state):
    """Detecta alertas críticas en los tanques"""
    alerts = []
    
    for name, new_data in new_state.items():
        if new_data.get("error"):
            continue
            
        old_data = old_state.get(name, {})
        
        # 🔴 Contenedor offline
        if new_data.get("code") != 1:
            alerts.append(f"🚨 CRÍTICO: Tanque {name} - Contenedor OFFLINE")
        
        # 🔥 Temperatura del aceite
        oil_temp = new_data.get("oil_temp")
        if oil_temp is not None:
            if oil_temp >= TANK_TEMP_ALERT:
                old_temp = old_data.get("oil_temp")
                temp_trend = f" (anterior: {old_temp}°C)" if old_temp else ""
                alerts.append(
                    f"🔥 CRÍTICO: Tanque {name}\n"
                    f"📊 Temperatura aceite: {oil_temp}°C{temp_trend}\n"
                    f"⚠️ Límite: {TANK_TEMP_ALERT}°C"
                )
            elif oil_temp >= TANK_TEMP_WARNING:
                alerts.append(f"🟡 ADVERTENCIA: Tanque {name} - Temperatura {oil_temp}°C (límite advertencia: {TANK_TEMP_WARNING}°C)")
        
        # 💧 Inmersión
        immersion_percent = new_data.get("immersion_percent")
        if immersion_percent is not None:
            if immersion_percent < IMMERSION_CRITICAL:
                alerts.append(
                    f"🔴 CRÍTICO: Tanque {name}\n"
                    f"💧 Inmersión: {immersion_percent}%\n"
                    f"⚠️ Nivel crítico (mínimo: {IMMERSION_CRITICAL}%)"
                )
            elif immersion_percent < IMMERSION_MIN:
                alerts.append(f"⚠️ Tanque {name} - Inmersión baja: {immersion_percent}% (mínimo: {IMMERSION_MIN}%)")
        
        # 📊 Nivel del tanque
        tank_level = new_data.get("tank_level")
        if tank_level is not None:
            if tank_level < TANK_LEVEL_CRITICAL:
                alerts.append(
                    f"🔴 CRÍTICO: Tanque {name}\n"
                    f"📊 Nivel tanque: {tank_level}%\n"
                    f"⚠️ Nivel crítico (mínimo: {TANK_LEVEL_CRITICAL}%)"
                )
            elif tank_level < TANK_LEVEL_MIN:
                alerts.append(f"⚠️ Tanque {name} - Nivel bajo: {tank_level}% (mínimo: {TANK_LEVEL_MIN}%)")
        
        # 🌊 Flujo de aceite
        oil_flow = new_data.get("oil_flow")
        old_flow = old_data.get("oil_flow")
        if oil_flow is not None:
            if oil_flow < OIL_FLOW_CRITICAL:
                flow_trend = f" (anterior: {old_flow} L/min)" if old_flow else ""
                alerts.append(
                    f"🔴 CRÍTICO: Tanque {name}\n"
                    f"🌊 Flujo aceite: {oil_flow} L/min{flow_trend}\n"
                    f"⚠️ Flujo crítico (mínimo: {OIL_FLOW_CRITICAL} L/min)"
                )
            elif oil_flow < OIL_FLOW_MIN:
                alerts.append(f"⚠️ Tanque {name} - Flujo bajo: {oil_flow} L/min (mínimo: {OIL_FLOW_MIN} L/min)")
        
        # 💪 Presión del sistema
        pressure = new_data.get("pressure")
        if pressure is not None:
            if pressure < PRESSURE_MIN:
                alerts.append(
                    f"🔴 CRÍTICO: Tanque {name}\n"
                    f"💪 Presión baja: {pressure} bar\n"
                    f"⚠️ Mínimo: {PRESSURE_MIN} bar"
                )
            elif pressure > PRESSURE_MAX:
                alerts.append(
                    f"🔴 CRÍTICO: Tanque {name}\n"
                    f"💪 Presión alta: {pressure} bar\n"
                    f"⚠️ Máximo: {PRESSURE_MAX} bar"
                )
        
        # ❄️ Eficiencia de enfriamiento baja
        cooling_eff = new_data.get("cooling_efficiency")
        if cooling_eff is not None and cooling_eff < COOLING_EFFICIENCY_MIN:
            alerts.append(
                f"⚠️ Tanque {name}\n"
                f"❄️ Eficiencia enfriamiento baja: {cooling_eff}%\n"
                f"📊 Mínimo esperado: {COOLING_EFFICIENCY_MIN}%"
            )
        
        # 🌡️ Diferencia de temperatura alta
        temp_diff = new_data.get("temp_diff")
        if temp_diff is not None and temp_diff > TEMP_DIFF_MAX:
            alerts.append(
                f"⚠️ Tanque {name}\n"
                f"🌡️ Diferencia temperatura alta: {temp_diff}°C\n"
                f"📊 Máximo recomendado: {TEMP_DIFF_MAX}°C"
            )
        
        # ⚙️ Estado de bombas
        pump_status = new_data.get("pump_status", "").lower()
        if pump_status and pump_status != "n/a":
            if any(word in pump_status for word in ["off", "offline", "error", "fault", "stop"]):
                alerts.append(f"⚙️ CRÍTICO: Tanque {name} - Bomba OFFLINE o con error: {new_data.get('pump_status')}")
        
        # 🔍 Estado de filtros
        filter_status = new_data.get("filter_status", "").lower()
        if filter_status and filter_status != "n/a":
            if any(word in filter_status for word in ["dirty", "clogged", "blocked", "error", "fault"]):
                alerts.append(f"🔍 ADVERTENCIA: Tanque {name} - Filtros requieren mantenimiento: {new_data.get('filter_status')}")
        
        # Presión diferencial de filtro alta
        filter_diff = new_data.get("filter_diff_pressure")
        if filter_diff is not None and filter_diff > 0.5:  # más de 0.5 bar de diferencia
            alerts.append(f"🔍 Tanque {name} - Presión diferencial filtro alta: {filter_diff} bar (filtros sucios)")
    
    return alerts

def load_tank_state():
    """Carga el estado anterior de los tanques"""
    try:
        if os.path.exists(TANK_STATE_FILE):
            with open(TANK_STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_tank_state(state):
    """Guarda el estado actual de los tanques"""
    try:
        with open(TANK_STATE_FILE, 'w') as f:
            json.dump(state, f)
    except:
        pass

def main():
    """Función principal"""
    print("Iniciando monitoreo de tanques...")
    
    # Obtener estado actual
    msg, new_state = check_tank_status()
    
    # Cargar estado anterior
    old_state = load_tank_state()
    
    # Detectar alertas
    alerts = detect_tank_alerts(old_state, new_state)
    
    # Enviar alertas primero (si existen)
    if alerts:
        alert_msg = "🚨 ALERTAS DE TANQUES\n\n" + "\n\n".join(alerts)
        send_telegram(alert_msg)
        print("Alertas enviadas:")
        print(alert_msg)
    
    # Enviar reporte completo
    send_telegram(msg)
    print("Reporte enviado:")
    print(msg)
    
    # Guardar estado actual
    save_tank_state(new_state)
    print("Estado guardado")

if __name__ == "__main__":
    main()
