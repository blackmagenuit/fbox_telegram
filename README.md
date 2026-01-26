# FBOX Telegram Monitor

Sistema automatizado de monitoreo 24/7 para contenedores de minería FBOX con notificaciones en tiempo real vía Telegram, reportes Excel interactivos, y bot de comandos desplegado en la nube.

**Desarrollado por:** [@blackmagenuit](https://github.com/blackmagenuit)

## 🚀 Características Principales

### 🤖 Bot de Telegram Interactivo
Bot desplegado 24/7 en **Render.com** que responde comandos instantáneamente:
- `/resumen` - Resumen del día actual
- `/resumen7` - Excel de últimos 7 días
- `/resumen30` - Excel de últimos 30 días  
- `/resumentodo` - Excel completo de todo el historial
- `/semanal` - Reporte semanal de estadísticas
- `/ayuda` - Lista de comandos disponibles

### 📊 Reportes Excel Automáticos
Sistema de generación de reportes profesionales con 4 hojas:
- **Todas las alertas**: Registro completo cronológico
- **Por categoría**: Agrupado por tipo (OFFLINE, Temperatura, Mineros, Potencia)
- **Por contenedor**: Agrupado por C01, C02, etc.
- **Por día**: Resumen diario de alertas

### ☁️ Integración con Dropbox
Almacenamiento compartido entre sistemas locales y nube:
- Sincronización automática de historial de alertas
- Reportes Excel guardados en Dropbox
- Acceso desde GitHub Actions y Render

## 🎯 Características de Monitoreo

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

### Automatización
- Ejecución automática cada hora mediante **GitHub Actions**
- Sin necesidad de servidor o PC encendida 24/7
- Completamente gratuito
- Notificaciones vía Telegram Bot

## 📊 Ejemplos de Reportes

### Reporte FBOX
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

## 🔧 Tecnologías y Arquitectura

### Backend
- **Python 3.12** - Lenguaje principal
- **Telegram Bot API** - Notificaciones y bot interactivo
- **FBOX API** (america.fboxdata.com) - Datos de contenedores
- **pandas + openpyxl** - Generación de reportes Excel
- **Dropbox API** - Almacenamiento en la nube
- **pytz / zoneinfo** - Manejo de zonas horarias (Paraguay)

### Infraestructura
- **GitHub Actions** - Monitoreo automático cada 5 minutos (24/7 gratis)
- **Render.com** - Hosting del bot interactivo (plan gratuito)
- **Dropbox** - Storage compartido entre sistemas
- **GitHub Secrets** - Manejo seguro de credenciales

### Arquitectura del Sistema
```
┌─────────────────────────────────────────────────────────┐
│                    FBOX API                              │
│           (america.fboxdata.com)                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Cada 5 min
                 ▼
┌─────────────────────────────────────────────────────────┐
│           GitHub Actions Workflow                        │
│  - fbox_telegram.py ejecuta automáticamente             │
│  - Detecta alertas y envía notificaciones               │
│  - Guarda historial en Dropbox                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Guarda JSON
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  Dropbox Storage                         │
│  - fbox_alerts_history.json                             │
│  - fbox_state.json                                      │
│  - reportes Excel (.xlsx)                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Lee datos
                 ▼
┌─────────────────────────────────────────────────────────┐
│          Bot Render.com (24/7)                          │
│  - telegram_bot_handler.py                              │
│  - Responde comandos instantáneamente                   │
│  - Genera reportes Excel bajo demanda                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Envía reportes
                 ▼
┌─────────────────────────────────────────────────────────┐
│            Usuario en Telegram                           │
│  - Recibe alertas automáticas                           │
│  - Solicita reportes con comandos                       │
└─────────────────────────────────────────────────────────┘
```

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

## ⚙️ Configuración y Deployment

### 🔐 Paso 1: Configurar GitHub Secrets

En tu repositorio: **Settings** → **Secrets and variables** → **Actions**

| Secret Name | Descripción | Cómo obtenerlo |
|------------|-------------|----------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot | @BotFather en Telegram → `/newbot` |
| `CHAT_ID` | ID del canal/chat | Añade bot al canal → `/getUpdates` |
| `FBOX_SSID` | Cookie de sesión FBOX | F12 en fboxdata.com → Application → Cookies |
| `ADMIN_TOKEN` | Token admin de FBOX | Opcional, para funciones avanzadas |

### ☁️ Paso 2: Configurar Dropbox (Opcional pero recomendado)

1. Crea app en https://www.dropbox.com/developers/apps
2. Tipo: **Scoped access** → **Full Dropbox**
3. Permisos: `files.content.read` y `files.content.write`
4. Genera Access Token en Settings
5. Guarda el token para Render

### 🚀 Paso 3: Desplegar Bot en Render

**Guía completa:** Ver [DEPLOYMENT.md](DEPLOYMENT.md)

1. Crea cuenta en https://render.com
2. New → **Web Service** (gratuito)
3. Conecta tu repositorio de GitHub
4. Configuración:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot_handler.py`
   
5. Variables de entorno en Render:
   ```
   TELEGRAM_BOT_TOKEN = <tu_token>
   CHAT_ID = <tu_chat_id>
   FBOX_SSID = <tu_ssid>
   ADMIN_TOKEN = <tu_admin_token>
   DROPBOX_ACCESS_TOKEN = <token_de_dropbox>
   ```

6. Deploy! El bot estará corriendo 24/7 gratis

### 📋 Configuración Local (.env)

Para desarrollo local, crea archivo `.env`:
```bash
BOT_TOKEN=tu_token_aqui
CHAT_ID=tu_chat_id_aqui
FBOX_SSID=tu_ssid_aqui
ADMIN_TOKEN=tu_admin_token_aqui
DROPBOX_PATH=C:/Users/.../Dropbox/Archivos de FBOX  # Ruta local
DROPBOX_ACCESS_TOKEN=sl.xxx...  # Para Render
```

> ⚠️ **Importante**: El archivo `.env` está en `.gitignore` y nunca se sube a Git

## 🕐 Programación y Ejecución

### GitHub Actions (Monitoreo Automático)
- **Frecuencia**: Cada 5 minutos
- **Cron**: `*/5 * * * *` (UTC)
- **Función**: Detecta alertas y envía notificaciones
- **Gratuito**: GitHub Actions ofrece 2000 minutos/mes gratis

### Render Bot (Comandos Interactivos)
- **Disponibilidad**: 24/7 en la nube
- **Función**: Responde comandos de usuarios
- **Plan gratuito**: 750 horas/mes (suficiente para 24/7)
- **Nota**: Se duerme tras 15 min de inactividad, despierta automáticamente

## 🎮 Uso del Bot

### Comandos Disponibles

```
/resumen - Ver resumen de alertas del día actual
/resumen7 - Generar Excel de últimos 7 días
/resumen30 - Generar Excel de últimos 30 días
/resumentodo - Generar Excel completo (todo el historial)
/semanal - Reporte semanal de estadísticas
/ayuda - Mostrar esta lista de comandos
```

### Ejemplos de Uso

**Resumen rápido:**
```
Usuario: /resumen
Bot: 📊 Resumen de alertas de hoy
     Total: 3 alertas
     - 1 OFFLINE
     - 2 Temperatura alta
```

**Reporte Excel:**
```
Usuario: /resumen7
Bot: 📊 Generando reporte de últimos 7 días...
     ✅ Reporte generado
     [Envía archivo Excel]
```

## 📝 Archivos del Proyecto

### Scripts Principales
- **fbox_telegram.py** - Monitor principal con sistema de alertas
- **telegram_bot_handler.py** - Bot interactivo con comandos
- **generate_alerts_excel.py** - Generador de reportes Excel
- **dropbox_storage.py** - Cliente API de Dropbox

### Archivos de Configuración
- **requirements.txt** - Dependencias Python
- **Procfile** - Configuración para deployment
- **render.yaml** - Config específica de Render
- **.github/workflows/fbox_monitor.yml** - GitHub Actions workflow

### Documentación
- **README.md** - Documentación principal
- **DEPLOYMENT.md** - Guía de deployment en Render
- **DROPBOX_SETUP.md** - Configuración de Dropbox API
- **README_BOT.md** - Documentación del bot
- **README_EXCEL.md** - Documentación de reportes

### Datos (JSON en Dropbox)
- **fbox_state.json** - Estado anterior para comparación
- **fbox_alerts_history.json** - Historial completo de alertas
- **last_report_time.json** - Control de reportes semanales

### Utilities
- **start_bot.bat** - Lanzador Windows para bot local
- **verify_dropbox.py** - Verificar conexión a Dropbox
- **debug_bot.py** - Depurar bot de Telegram
- **get_chat_id.py** - Obtener Chat ID de Telegram

## 🚀 Ejecución Manual y Testing

### Testing Local del Monitor
```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="tu_token"
$env:CHAT_ID="tu_chat_id"
$env:FBOX_SSID="tu_ssid"
python fbox_telegram.py

# Linux/Mac
export TELEGRAM_BOT_TOKEN="tu_token"
export CHAT_ID="tu_chat_id"
export FBOX_SSID="tu_ssid"
python fbox_telegram.py
```

### Testing Local del Bot
```bash
# Asegúrate de tener .env configurado
python telegram_bot_handler.py

# O usa el launcher de Windows
start_bot.bat
```

### Trigger Manual en GitHub
1. Ve a **Actions** → **FBOX Monitor**
2. Click **"Run workflow"**
3. Selecciona rama **main**
4. Click botón verde **"Run workflow"**

### Ver Logs
- **GitHub Actions**: Pestaña Actions → Click en run específico
- **Render**: Dashboard → Tu servicio → Pestaña "Logs"
- **Local**: Salida de consola directa

## 🔍 Troubleshooting

### Bot no responde en Render
1. Verifica logs en Render
2. Confirma que todas las variables de entorno estén configuradas
3. Verifica que el servicio esté "Live" (verde)

### Alertas no llegan
1. Verifica que GitHub Actions esté ejecutándose
2. Revisa logs de la última ejecución
3. Confirma que los secrets estén configurados correctamente

### Excel no se genera
1. Verifica que exista `fbox_alerts_history.json` en Dropbox
2. Confirma `DROPBOX_ACCESS_TOKEN` en Render
3. Revisa permisos de la app en Dropbox Developers

### FBOX_SSID expiró
1. Vuelve a iniciar sesión en fboxdata.com
2. Copia nuevo valor de cookie `ssid`
3. Actualiza en GitHub Secrets y Render

## 📈 Roadmap y Mejoras Futuras

- [x] Bot interactivo con comandos
- [x] Reportes Excel profesionales
- [x] Integración con Dropbox
- [x] Deployment en Render (24/7 gratis)
- [x] Historial completo de alertas
- [ ] Dashboard web interactivo
- [ ] Gráficos de tendencias (temperatura, hashrate, potencia)
- [ ] Alertas por email
- [ ] Notificaciones multi-nivel (crítico, advertencia, info)
- [ ] Base de datos para históricos largos
- [ ] Predicción de mantenimiento con ML
- [ ] Alertas personalizables por contenedor
- [ ] API REST para integraciones

## 🤝 Contribuciones

Este es un proyecto privado desarrollado para monitoreo específico de infraestructura FBOX. Para sugerencias o mejoras, contacta al autor.

## 📄 Licencia

Proyecto privado desarrollado por **blackmagenuit** para monitoreo de infraestructura de minería FBOX.

---

**Autor**: [@blackmagenuit](https://github.com/blackmagenuit)  
**Última actualización**: 2026-01-26  
**Versión**: 2.0 - Bot en la nube + Reportes Excel + Dropbox API
