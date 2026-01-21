# FBOX Telegram Monitor

Sistema automatizado de monitoreo 24/7 para contenedores de minería FBOX con notificaciones en tiempo real vía Telegram.

**Desarrollado por:** [@blackmagenuit](https://github.com/blackmagenuit)

## 🚀 Características

### Monitoreo en Tiempo Real
- **Estado del contenedor**: Online/Offline
- **Tipo de contenedor**: Identificación del modelo
- **Temperatura del aceite**: Promedio de sensores de inmersión
- **Temperatura del contenedor**: Ambiente interno
- **Estado de inmersión**: Status y porcentaje de inmersión
- **Mineros**: Cantidad online/offline
- **Hashrate**: En tiempo real (PH/s)
- **Potencia**: Consumo actual en kW
- **Consumo diario**: kWh consumidos en el día

### Sistema de Alertas Automáticas Inteligente
El sistema compara el estado actual vs el anterior y detecta anomalías:
- 🔴 **Contenedor OFFLINE**: Notificación inmediata si el contenedor deja de responder
- 🌡️ **Temperatura alta**: Alerta cuando el aceite alcanza ≥55°C
- ⛏️ **Mineros caídos**: Alerta cuando caen ≥10 mineros entre reportes
- ⚡ **Potencia anormal**: Alerta cuando la potencia cae ≥30% respecto al reporte anterior

**Características:**
- Sistema de detección de cambios: compara estado anterior guardado en `fbox_state.json`
- Alertas separadas: mensajes críticos se envían antes del reporte regular
- Contexto completo: las alertas incluyen valores antiguos vs nuevos

### Automatización
- Ejecución automática cada hora mediante **GitHub Actions**
- Sin necesidad de servidor o PC encendida 24/7
- Completamente gratuito
- Notificaciones vía Telegram Bot

## 📊 Ejemplo de Reporte

```
📦 FBOX STATUS
2026-01-21 14:30:00

🔹 C01
🟢 ONLINE
📦 Tipo: Exhaust Fan
🔥 Aceite: 45.2 °C
🌡️ Contenedor: 41.7 °C
💧 Inmersión: On (95%)
⛏ Mineros: 150 online / 58 offline
⚙️ Hashrate: 46.89 PH/s
⚡ Potencia: 883.46 kW

🔹 C02
🟢 ONLINE
📦 Tipo: Exhaust Fan
🔥 Aceite: 42.5 °C
🌡️ Contenedor: 43.8 °C
💧 Inmersión: On (98%)
⛏ Mineros: 146 online / 14 offline
⚙️ Hashrate: 46.66 PH/s
⚡ Potencia: 971.78 kW
```

## ⚙️ Configuración

### Contenedores Monitoreados
- **C01**: Container ID 290
- **C02**: Container ID 291
- **Área**: 10000013

### Umbrales de Alertas
- Temperatura alta: ≥55°C
- Mineros caídos: ≥10 unidades
- Caída de potencia: ≥30%

### Zona Horaria
- **America/Asuncion** (UTC-3, Paraguay)

## 🔧 Tecnologías

- **Python 3.11**
- **Telegram Bot API** - Notificaciones
- **FBOX API** (america.fboxdata.com) - Datos de contenedores
- **GitHub Actions** - Automatización 24/7
- **pytz** - Manejo de zonas horarias

## 📡 API Endpoints

### Detalles del Contenedor
El sistema intenta múltiples endpoints para asegurar compatibilidad:
```
Endpoints intentados (en orden):
1. http://america.fboxdata.com/api/index/fbox.boxlist/detail
2. http://america.fboxdata.com/api/index/fbox.boxdetail/detail
3. http://america.fboxdata.com/api/index/fbox.boxinfo/detail
4. http://america.fboxdata.com/api/index/fbox.box/detail
5. http://america.fboxdata.com/api/index/fbox.boxlist/index

Params: output=json, area_id={AREA}, id={CONTAINER_ID}
```

**Datos extraídos del endpoint:**
- `realtime_power`: Hashrate en GH/s (convertido a PH/s)
- `total_realtime_power`: Potencia eléctrica en kW
- `fbox_temp`: Temperatura del contenedor
- `miner_online/offline`: Estado de mineros
- `sub_box_list`: Lista de sub-cajas con sensores de temperatura del aceite
- `today_use_power`: Consumo del día en kWh
- `fbox_type_name`: Tipo de contenedor
- `immersion_status`: Estado de inmersión (On/Off/Offline)
- `immersion_percent`: Porcentaje de inmersión

**Sistema de failover:**
Si un endpoint falla, el sistema automáticamente intenta el siguiente hasta encontrar uno que responda correctamente.

## 🔒 Seguridad

### Configuración de Credenciales

El sistema utiliza **GitHub Secrets** para proteger información sensible. Debes configurar las siguientes variables en tu repositorio:

**Pasos para configurar los secrets:**

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**
4. Agrega los siguientes secrets:

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `BOT_TOKEN` | Token del bot de Telegram | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `CHAT_ID` | ID del chat/grupo de Telegram | `-1001234567890` |
| `FBOX_SSID` | Cookie de sesión de FBOX | `abc123def456...` |

### Cómo obtener las credenciales

**BOT_TOKEN:**
- Habla con [@BotFather](https://t.me/BotFather) en Telegram
- Envía `/newbot` y sigue las instrucciones
- Copia el token que te proporciona

**CHAT_ID:**
- Agrega el bot a tu grupo
- Envía un mensaje al grupo
- Ve a: `https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates`
- Busca el `chat_id` en la respuesta

**FBOX_SSID:**
- Inicia sesión en http://america.fboxdata.com
- Abre las herramientas de desarrollador (F12)
- Ve a Application → Cookies
- Copia el valor de la cookie `ssid`

> ⚠️ **Importante**: Nunca compartas estos valores públicamente. Los GitHub Secrets están encriptados y solo son accesibles durante la ejecución del workflow.

## 🕐 Programación

GitHub Actions ejecuta el script:
- **Frecuencia**: Cada hora en el minuto 0
- **Cron**: `'0 * * * *'` (UTC)
- **Equivalente Paraguay**: Hora UTC - 3

Ejemplo:
- 17:00 UTC → 14:00 Paraguay
- 18:00 UTC → 15:00 Paraguay

## 📝 Logs y Debugging

### Archivos generados:
- **fbox_state.json**: Estado anterior completo para detectar cambios y anomalías
  - Contiene: estado de conexión, mineros online/offline, temperaturas, hashrate, potencia, etc.
  - Se actualiza en cada ejecución
  - Esencial para el sistema de alertas comparativas

### Logs disponibles:
- **GitHub Actions**: Pestaña "Actions" del repositorio
  - Salida completa de cada ejecución
  - Mensajes de alerta detectados
  - Estado guardado confirmado
  - Errores de API si los hay

### Salida de consola:
```
⏰ Ejecutando check: 2026-01-21 14:30:00
🚨 ALERTA ENVIADA: [si aplica]
✅ Reporte enviado
💾 Estado guardado
```

## 🚀 Ejecución Manual

### Para probar localmente:

Primero configura las variables de entorno:

```bash
# Windows PowerShell
$env:BOT_TOKEN="tu_token_aqui"
$env:CHAT_ID="tu_chat_id_aqui"
$env:FBOX_SSID="tu_ssid_aqui"
python fbox_telegram.py

# Linux/Mac
export BOT_TOKEN="tu_token_aqui"
export CHAT_ID="tu_chat_id_aqui"
export FBOX_SSID="tu_ssid_aqui"
python fbox_telegram.py
```

### Para ejecutar manualmente en GitHub:
1. Ve a la pestaña "Actions"
2. Selecciona "FBOX Monitor"
3. Click en "Run workflow"
4. Selecciona la rama "main"
5. Click en el botón verde "Run workflow"

## 📈 Próximas Mejoras

- [ ] Agregar gráficos de tendencias (temperatura, hashrate, potencia)
- [ ] Dashboard web con histórico de datos
- [ ] Alertas por email adicionales
- [ ] Notificaciones por niveles de prioridad (crítico, advertencia, info)
- [ ] Registro histórico en base de datos
- [ ] Predicción de mantenimiento basado en tendencias
- [ ] Alertas personalizables por contenedor

## 📄 Licencia

Proyecto desarrollado por **blackmagenuit** para monitoreo de infraestructura de minería.

---

**Autor**: [@blackmagenuit](https://github.com/blackmagenuit)  
**Última actualización**: 2026-01-21
