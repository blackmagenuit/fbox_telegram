import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path

# ---------------- CARGAR .env SI EXISTE (PARA DESARROLLO LOCAL) ----------------
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
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

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

# ============ UMBRALES DE ALERTAS ============
TEMP_ALERT_THRESHOLD = 55  # °C
MINERS_DROP_THRESHOLD = 1  # cantidad de mineros (alerta con 1 solo minero caído)
POWER_DROP_THRESHOLD = 30  # porcentaje
IMMERSION_MIN_PERCENT = 90  # porcentaje mínimo de inmersión

# ============ CONFIGURACIÓN DE TIEMPO ============
ALERT_CHECK_INTERVAL = 5  # minutos - revisar alertas cada 5 minutos
FULL_REPORT_INTERVAL = 60  # minutos - enviar reporte completo cada hora
WEEKLY_REPORT_DAY = 0  # día de la semana para reporte semanal (0=Lunes, 6=Domingo)

def fetch_json(url):
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

def get_power(container_id):
    candidates = [
        "http://america.fboxdata.com/api/index/fbox.boxlist/getelectricity",
        "http://america.fboxdata.com/api/index/fbox.electricity/getelectricity",
        "http://america.fboxdata.com/api/index/fbox.power/getelectricity",
        "http://america.fboxdata.com/api/index/fbox.elec/getelectricity",
        "http://america.fboxdata.com/api/index/fbox.boxdetail/getelectricity",
        "http://america.fboxdata.com/api/index/fbox.boxlist/electricity",
        "http://america.fboxdata.com/api/index/fbox.electricity/index",
    ]

    params = f"?output=json&area_id={AREA}&fbox_id={container_id}"

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
    try:
        v = float(x)
        return None if v <= -900 else v
    except:
        return None

def calc_oil_temp(detail_json):
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

def extract_container_data(detail_json):
    """Extrae datos del contenedor: tipo, inmersión, temperatura, etc."""
    # Los datos pueden estar en 'data' o en 'info' (como string JSON)
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
    
    # Tipo de contenedor (ej: "Exhaust Fan")
    container_type = data.get("fbox_type_name") or data.get("type_name") or "N/A"
    
    # Estado de inmersión
    immersion_status = data.get("immersion_status") or data.get("immersion")
    immersion_str = str(immersion_status) if immersion_status else "N/A"
    
    # Porcentaje de inmersión
    immersion_percent = to_float(data.get("immersion_percent"))
    
    # Temperatura del contenedor
    container_temp = to_float(data.get("fbox_temp"))
    
    # Hashrate en tiempo real (GH/s a PH/s)
    try:
        hashrate_gh = float(data.get("realtime_power", 0))
        hashrate_ph = round(hashrate_gh / 1000.0, 2) if hashrate_gh > 0 else None
    except:
        hashrate_ph = None
    
    # Potencia real en kW
    power_kw = to_float(data.get("total_realtime_power"))
    
    return {
        "container_type": container_type,
        "immersion_status": immersion_str,
        "immersion_percent": immersion_percent,
        "container_temp": container_temp,
        "hashrate_ph": hashrate_ph,
        "power_kw": power_kw
    }


def check_status():
    containers_data = {"C01": 290, "C02": 291}
    msg = "📦 FBOX STATUS\n"
    msg += f"{now_paraguay().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    state = {}

    for name, cid in containers_data.items():
        detail = get_detail(cid)
        power = get_power(cid)

        if isinstance(power, dict) and power.get("__error__"):
            msg += f"🔹 {name}\n"
            msg += "⚠️ Error leyendo potencia\n\n"
            continue

        if isinstance(detail, dict) and detail.get("__error__"):
            msg += f"🔹 {name}\n"
            msg += "⚠️ Error leyendo detalle\n\n"
            continue

        is_online = (detail.get("code") == 1)
        status_icon = "🟢 ONLINE" if is_online else "🔴 OFFLINE"
        
        d = (detail.get("data") or {})
        
        # Si el contenedor está OFFLINE, usar N/A para todo
        if not is_online:
            msg += f"🔹 {name}\n"
            msg += f"{status_icon}\n"
            msg += f"🔥 Aceite: N/A °C\n"
            msg += f"⛏ Mineros: N/A\n"
            msg += "⚡ Potencia: N/A\n\n"
            
            state[name] = {
                "code": detail.get("code", -1),
                "miner_online": "N/A",
                "miner_offline": "N/A",
                "oil_temp": None,
                "container_temp": None,
                "hashrate_ph": None,
                "power_kw": None
            }
            continue
        
        # Si está ONLINE, procesar los datos normalmente
        oil_temp = calc_oil_temp(detail)
        temp_txt = f"{oil_temp}" if oil_temp is not None else "N/A"
        
        # Convertir mineros a int, si no se puede usar 0
        try:
            m_on = int(d.get("miner_online", 0))
        except (ValueError, TypeError):
            m_on = 0
        
        try:
            m_off = int(d.get("miner_offline", 0))
        except (ValueError, TypeError):
            m_off = 0

        # Extraer datos adicionales del contenedor
        container_data = extract_container_data(detail)

        msg += f"🔹 {name}\n"
        msg += f"{status_icon}\n"
        msg += f"🔥 Aceite: {temp_txt} °C\n"
        
        # Temperatura del contenedor
        if container_data["container_temp"] is not None:
            msg += f"🌡️ Contenedor: {container_data['container_temp']} °C\n"
        
        msg += f"⛏ Mineros: {m_on} online / {m_off} offline\n"
        
        # Hashrate
        if container_data["hashrate_ph"] is not None:
            msg += f"⚙️ Hashrate: {container_data['hashrate_ph']} PH/s\n"
        
        # Potencia real desde API
        if container_data["power_kw"] is not None:
            msg += f"⚡ Potencia: {container_data['power_kw']} kW\n"
        else:
            msg += "⚡ Potencia: N/A\n"
        
        msg += "\n"

        state[name] = {
            "code": detail.get("code"),
            "miner_online": m_on,
            "miner_offline": m_off,
            "oil_temp": oil_temp,
            "container_temp": container_data["container_temp"],
            "hashrate_ph": container_data["hashrate_ph"],
            "power_kw": container_data["power_kw"]
        }

    return msg, state


def detect_alerts(old_state, new_state):
    """Detecta situaciones críticas que requieren alerta inmediata"""
    alerts = []
    
    for name, new_data in new_state.items():
        old_data = old_state.get(name, {})
        
        # 🔴 ALERTA: Contenedor OFFLINE
        if new_data.get("code") != 1:
            alerts.append(f"🚨 CRÍTICO: {name} está OFFLINE")
        
        # 🌡️ ALERTA: Temperatura alta (≥55°C)
        temp = new_data.get("oil_temp")
        if temp is not None and temp >= TEMP_ALERT_THRESHOLD:
            alerts.append(f"⚠️ TEMPERATURA ALTA: {name} - {temp}°C (umbral: {TEMP_ALERT_THRESHOLD}°C)")
        
        # ⛏️ ALERTA: Mineros caídos - DETECTAR CUALQUIER CAMBIO
        old_online = old_data.get("miner_online", 0)
        new_online = new_data.get("miner_online", 0)
        old_offline = old_data.get("miner_offline", 0)
        new_offline = new_data.get("miner_offline", 0)
        
        # Detectar si cayeron mineros
        if isinstance(old_online, int) and isinstance(new_online, int) and isinstance(old_offline, int) and isinstance(new_offline, int):
            # Solo alertar si el estado anterior era válido (contenedor estaba online)
            if old_online > 0 or old_offline > 0:
                drop_online = old_online - new_online
                increase_offline = new_offline - old_offline
                
                # Alertar si cayeron online O aumentaron offline
                if drop_online >= MINERS_DROP_THRESHOLD or increase_offline >= MINERS_DROP_THRESHOLD:
                    change = max(drop_online, increase_offline)
                    alerts.append(
                        f"⚠️ 🔻 ALERTA: MINEROS CAÍDOS\n"
                        f"📍 Contenedor: {name}\n"
                        f"📉 Cantidad caída: {change} minero(s)\n"
                        f"📊 Estado actual: {new_online} online / {new_offline} offline"
                    )
        
        # ⚡ ALERTA: Potencia anormalmente baja
        old_kw = old_data.get("power_kw")
        new_kw = new_data.get("power_kw")
        
        if old_kw and new_kw and old_kw > 0:
            drop_percent = ((old_kw - new_kw) / old_kw) * 100
            if drop_percent >= POWER_DROP_THRESHOLD:
                alerts.append(f"⚡ POTENCIA ANORMAL: {name} - Cayó {drop_percent:.1f}% ({old_kw} → {new_kw} kW)")
        
        # 💧 ALERTA: Inmersión offline o porcentaje bajo
        immersion_status = new_data.get("immersion_status", "")
        immersion_percent = new_data.get("immersion_percent")
        
        if immersion_status and "offline" in immersion_status.lower():
            alerts.append(f"💧 INMERSIÓN OFFLINE: {name} - Sistema de inmersión no responde")
        elif immersion_percent is not None and immersion_percent < IMMERSION_MIN_PERCENT:
            alerts.append(f"💧 INMERSIÓN BAJA: {name} - {immersion_percent}% (mínimo: {IMMERSION_MIN_PERCENT}%)")
        
        # 🌀 ALERTA: Ventilador offline o con problemas
        fan_status = new_data.get("fan_status")
        if fan_status:
            fan_status_str = str(fan_status).lower()
            if fan_status_str in ["off", "offline", "0", "error", "fault"]:
                alerts.append(f"🌀 VENTILADOR OFFLINE: {name} - Fan status: {fan_status}")
    
    return alerts


def has_changes(old_state, new_state):
    if not old_state:
        return True
    
    for name in new_state:
        if name not in old_state:
            return True
        
        old = old_state[name]
        new = new_state[name]
        
        if old.get("code") != new.get("code"):
            return True
        
        if old.get("miner_online") != new.get("miner_online"):
            return True
        
        if old.get("miner_offline") != new.get("miner_offline"):
            return True
        
        old_temp = old.get("oil_temp")
        new_temp = new.get("oil_temp")
        if old_temp is not None and new_temp is not None:
            if abs(old_temp - new_temp) > 3:
                return True
    
    return False


# ============ CONFIGURACIÓN DE ALMACENAMIENTO ============
# Configura la ruta de Dropbox aquí (deja vacío para usar carpeta actual)
DROPBOX_PATH = os.environ.get("DROPBOX_PATH", "")  # Ejemplo: "C:/Users/TU_USUARIO/Dropbox/FBOX"

# Si hay ruta de Dropbox configurada, úsala; si no, usa la carpeta actual
STORAGE_PATH = Path(DROPBOX_PATH) if DROPBOX_PATH else Path(__file__).parent

# Crear carpeta de almacenamiento si no existe
if DROPBOX_PATH:
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)

# Estado persistente en archivo
STATE_FILE = str(STORAGE_PATH / "fbox_state.json")
TIME_FILE = str(STORAGE_PATH / "last_report_time.json")
HISTORY_FILE = str(STORAGE_PATH / "fbox_history.json")
WEEKLY_TIME_FILE = str(STORAGE_PATH / "last_weekly_report.json")
ALERTS_HISTORY_FILE = str(STORAGE_PATH / "fbox_alerts_history.json")

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except:
        pass

def save_to_history(state):
    """Guarda el estado actual en el historial semanal"""
    try:
        # Cargar historial existente
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        
        # Agregar timestamp al estado actual
        record = {
            "timestamp": now_paraguay().isoformat(),
            "data": state
        }
        history.append(record)
        
        # Mantener solo los últimos 7 días (cada 5 min = 288 registros/día * 7 = 2016)
        max_records = 2016
        if len(history) > max_records:
            history = history[-max_records:]
        
        # Guardar historial actualizado
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception:
        pass

def save_alerts_to_history(alerts):
    """Guarda las alertas en el historial para reportes Excel"""
    if not alerts:
        return
    
    try:
        # Cargar historial existente
        history = []
        if os.path.exists(ALERTS_HISTORY_FILE):
            with open(ALERTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # Agregar nuevo registro de alertas
        record = {
            "timestamp": now_paraguay().isoformat(),
            "alerts": alerts
        }
        history.append(record)
        
        # Mantener solo los últimos 30 días de alertas
        # (estimado: ~100 alertas/día * 30 = 3000 registros máx)
        max_records = 3000
        if len(history) > max_records:
            history = history[-max_records:]
        
        # Guardar historial actualizado
        with open(ALERTS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando alertas: {e}")

def load_last_report_time():
    """Carga el timestamp del último reporte completo"""
    try:
        if os.path.exists(TIME_FILE):
            with open(TIME_FILE, 'r') as f:
                data = json.load(f)
                return data.get("last_report_time")
    except:
        pass
    return None

def save_last_report_time():
    """Guarda el timestamp actual como último reporte completo"""
    try:
        with open(TIME_FILE, 'w') as f:
            json.dump({"last_report_time": now_paraguay().isoformat()}, f)
    except:
        pass

def should_send_full_report():
    """Determina si debe enviarse el reporte completo (cada hora)"""
    last_time = load_last_report_time()
    if not last_time:
        return True  # Primera ejecución
    
    try:
        last_dt = datetime.fromisoformat(last_time)
        now = now_paraguay()
        elapsed_minutes = (now - last_dt).total_seconds() / 60
        return elapsed_minutes >= FULL_REPORT_INTERVAL
    except:
        return True  # Si hay error, enviar reporte


def load_last_weekly_report():
    """Carga el timestamp del último reporte semanal"""
    try:
        if os.path.exists(WEEKLY_TIME_FILE):
            with open(WEEKLY_TIME_FILE, 'r') as f:
                data = json.load(f)
                return data.get("last_weekly_report")
    except:
        pass
    return None

def save_last_weekly_report():
    """Guarda el timestamp actual como último reporte semanal"""
    try:
        with open(WEEKLY_TIME_FILE, 'w') as f:
            json.dump({"last_weekly_report": now_paraguay().isoformat()}, f)
    except:
        pass

def should_send_weekly_report():
    """Determina si debe enviarse el reporte semanal (una vez por semana, los lunes)"""
    now = now_paraguay()
    
    # Verificar si es el día configurado para el reporte
    if now.weekday() != WEEKLY_REPORT_DAY:
        return False
    
    last_time = load_last_weekly_report()
    if not last_time:
        return True  # Primera ejecución
    
    try:
        last_dt = datetime.fromisoformat(last_time)
        
        # Calcular horas transcurridas desde el último reporte
        hours_elapsed = (now - last_dt).total_seconds() / 3600
        
        # Solo enviar si han pasado al menos 6 días (144 horas)
        # Esto evita que se envíe múltiples veces el mismo día
        if hours_elapsed < 144:  # 6 días = 144 horas
            return False
        
        # Verificar que estamos en una semana diferente
        now_week = now.isocalendar()[1]  # Número de semana del año
        now_year = now.isocalendar()[0]  # Año
        last_week = last_dt.isocalendar()[1]
        last_year = last_dt.isocalendar()[0]
        
        # Enviar solo si estamos en una semana diferente Y han pasado 6+ días
        return (now_year, now_week) != (last_year, last_week)
    except:
        return True

def calculate_weekly_stats():
    """Calcula estadísticas semanales del historial"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return None
        
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        if not history:
            return None
        
        # Preparar estructura para estadísticas
        stats = {}
        
        # Procesar cada registro
        for record in history:
            data = record.get("data", {})
            
            for container_name, container_data in data.items():
                if container_name not in stats:
                    stats[container_name] = {
                        "oil_temps": [],
                        "container_temps": [],
                        "hashrates": [],
                        "powers": [],
                        "miners_online": [],
                        "miners_offline": [],
                        "online_count": 0,
                        "offline_count": 0,
                        "fan_online_count": 0,
                        "fan_offline_count": 0
                    }
                
                # Recolectar datos válidos
                if container_data.get("oil_temp") is not None:
                    stats[container_name]["oil_temps"].append(container_data["oil_temp"])
                
                if container_data.get("container_temp") is not None:
                    stats[container_name]["container_temps"].append(container_data["container_temp"])
                
                if container_data.get("hashrate_ph") is not None:
                    stats[container_name]["hashrates"].append(container_data["hashrate_ph"])
                
                if container_data.get("power_kw") is not None:
                    stats[container_name]["powers"].append(container_data["power_kw"])
                
                if isinstance(container_data.get("miner_online"), int):
                    stats[container_name]["miners_online"].append(container_data["miner_online"])
                
                if isinstance(container_data.get("miner_offline"), int):
                    stats[container_name]["miners_offline"].append(container_data["miner_offline"])
                
                # Contador de estado online/offline
                if container_data.get("code") == 1:
                    stats[container_name]["online_count"] += 1
                else:
                    stats[container_name]["offline_count"] += 1
                
                # Contador de ventilador
                fan_status = container_data.get("fan_status")
                if fan_status:
                    fan_str = str(fan_status).lower()
                    if fan_str in ["on", "online", "1", "running"]:
                        stats[container_name]["fan_online_count"] += 1
                    else:
                        stats[container_name]["fan_offline_count"] += 1
        
        # Calcular promedios
        summary = {}
        for container_name, data in stats.items():
            summary[container_name] = {
                "avg_oil_temp": round(sum(data["oil_temps"]) / len(data["oil_temps"]), 1) if data["oil_temps"] else None,
                "max_oil_temp": round(max(data["oil_temps"]), 1) if data["oil_temps"] else None,
                "min_oil_temp": round(min(data["oil_temps"]), 1) if data["oil_temps"] else None,
                "avg_container_temp": round(sum(data["container_temps"]) / len(data["container_temps"]), 1) if data["container_temps"] else None,
                "avg_hashrate": round(sum(data["hashrates"]) / len(data["hashrates"]), 2) if data["hashrates"] else None,
                "avg_power": round(sum(data["powers"]) / len(data["powers"]), 1) if data["powers"] else None,
                "avg_miners_online": round(sum(data["miners_online"]) / len(data["miners_online"]), 1) if data["miners_online"] else None,
                "avg_miners_offline": round(sum(data["miners_offline"]) / len(data["miners_offline"]), 1) if data["miners_offline"] else None,
                "uptime_percent": round((data["online_count"] / (data["online_count"] + data["offline_count"])) * 100, 1) if (data["online_count"] + data["offline_count"]) > 0 else 0,
                "fan_uptime_percent": round((data["fan_online_count"] / (data["fan_online_count"] + data["fan_offline_count"])) * 100, 1) if (data["fan_online_count"] + data["fan_offline_count"]) > 0 else None,
                "total_records": len(history)
            }
        
        return summary
    except Exception:
        return None

def generate_weekly_report():
    """Genera el reporte semanal resumido"""
    stats = calculate_weekly_stats()
    
    if not stats:
        return "📊 REPORTE SEMANAL\n\nNo hay datos suficientes para generar el reporte."
    
    msg = "📊 REPORTE SEMANAL FBOX\n"
    msg += f"📅 {now_paraguay().strftime('%Y-%m-%d')}\n"
    msg += f"Período: Últimos 7 días\n\n"
    
    for container_name, data in stats.items():
        msg += f"━━━━━ {container_name} ━━━━━\n"
        
        # Uptime
        msg += f"✅ Uptime: {data['uptime_percent']}%\n"
        
        # Temperatura del aceite
        if data['avg_oil_temp']:
            msg += f"🔥 Temp. Aceite:\n"
            msg += f"   • Promedio: {data['avg_oil_temp']}°C\n"
            msg += f"   • Máxima: {data['max_oil_temp']}°C\n"
            msg += f"   • Mínima: {data['min_oil_temp']}°C\n"
        
        # Temperatura del contenedor
        if data['avg_container_temp']:
            msg += f"🌡️ Temp. Contenedor: {data['avg_container_temp']}°C (prom)\n"
        
        # Mineros
        if data['avg_miners_online']:
            msg += f"⛏ Mineros:\n"
            msg += f"   • Online: {data['avg_miners_online']} (prom)\n"
            msg += f"   • Offline: {data['avg_miners_offline']} (prom)\n"
        
        # Hashrate
        if data['avg_hashrate']:
            msg += f"⚙️ Hashrate: {data['avg_hashrate']} PH/s (prom)\n"
        
        # Potencia
        if data['avg_power']:
            msg += f"⚡ Potencia: {data['avg_power']} kW (prom)\n"
        
        # Ventilador
        if data['fan_uptime_percent'] is not None:
            msg += f"🌀 Fan Uptime: {data['fan_uptime_percent']}%\n"
        
        msg += "\n"
    
    msg += f"📈 Total de mediciones: {stats[list(stats.keys())[0]]['total_records']}\n"
    msg += f"⏱️ Frecuencia: Cada {ALERT_CHECK_INTERVAL} minutos"
    
    return msg


# ============ EJECUCIÓN ÚNICA ============
if __name__ == "__main__":
    print(f"⏰ Ejecutando check: {now_paraguay()}")
    print(f"📋 Configuración: Alertas cada {ALERT_CHECK_INTERVAL} min, Reporte completo cada {FULL_REPORT_INTERVAL} min")
    
    msg, current_state = check_status()
    old_state = load_state()
    
    # SIEMPRE detectar y enviar alertas críticas (cada 5 minutos)
    alerts = detect_alerts(old_state, current_state)
    
    if alerts:
        alert_msg = "🚨 ALERTA FBOX\n"
        alert_msg += f"{now_paraguay().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for alert in alerts:
            alert_msg += f"{alert}\n"
        
        send_telegram(alert_msg)
        save_alerts_to_history(alerts)  # Guardar alertas en historial
        print("🚨 ALERTA ENVIADA:")
        print(alert_msg)
    else:
        print("✅ Sin alertas detectadas")
    
    # Enviar reporte completo solo cada hora
    if should_send_full_report():
        send_telegram(msg)
        save_last_report_time()
        print("📊 REPORTE COMPLETO ENVIADO (cada hora)")
        print(msg)
    else:
        last_time = load_last_report_time()
        if last_time:
            try:
                last_dt = datetime.fromisoformat(last_time)
                elapsed = (datetime.now() - last_dt).total_seconds() / 60
                print(f"⏭️ Reporte completo omitido (último hace {elapsed:.1f} min, se envía cada {FULL_REPORT_INTERVAL} min)")
            except:
                print("⏭️ Reporte completo omitido")
    
    # Reporte semanal: solo se envía bajo demanda con comando /semanal
    # (no se envía automáticamente)
    
    # Guardar estado actual y agregar al historial
    save_state(current_state)
    save_to_history(current_state)
    print("💾 Estado guardado")
