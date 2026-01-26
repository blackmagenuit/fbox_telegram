# Guía de Despliegue en Render.com

## 📋 Requisitos Previos
- Cuenta en GitHub (ya tienes el repositorio)
- Cuenta gratuita en [Render.com](https://render.com)
- Tus tokens y credenciales listos

## 🚀 Pasos para Desplegar

### 1. Crear Cuenta en Render
1. Ve a https://render.com
2. Haz clic en "Get Started"
3. Registrate con tu cuenta de GitHub (recomendado)

### 2. Crear Nuevo Web Service
1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio de GitHub: `fbox_telegram_repo`
4. Render detectará automáticamente que es un proyecto Python

### 3. Configurar el Service
Usa estos valores:

- **Name**: `fbox-telegram-bot` (o el nombre que prefieras)
- **Region**: Selecciona la más cercana (Oregon o Ohio recomendados)
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python telegram_bot_handler.py`
- **Instance Type**: `Free`

### 4. Configurar Variables de Entorno
En la sección "Environment Variables", agrega las siguientes variables:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | Tu token del bot | Token de @BotFather |
| `CHAT_ID` | -1003693418265 | ID del canal de Telegram |
| `FBOX_SSID` | Tu SSID | Credencial para API de FBOX |
| `ADMIN_TOKEN` | Tu token | Credencial para API de FBOX |
| `DROPBOX_PATH` | Ruta completa | Ruta de Dropbox (ej: C:/Users/.../Dropbox/...) |
| `PYTHON_VERSION` | 3.12.0 | Versión de Python |

⚠️ **IMPORTANTE**: En Render, el `DROPBOX_PATH` no funcionará igual que en local porque el servidor no tiene acceso a tu Dropbox local. Ver sección de alternativas abajo.

### 5. Desplegar
1. Haz clic en "Create Web Service"
2. Render automáticamente:
   - Clonará tu repositorio
   - Instalará las dependencias
   - Iniciará el bot
3. Espera 2-3 minutos para el primer deploy

### 6. Verificar que Funciona
1. Ve a tu bot en Telegram: @fbox_status_bot
2. Envía el comando `/ayuda`
3. El bot debería responder inmediatamente

## 🔧 Alternativas para Almacenamiento (Sin Dropbox Local)

Como el servidor de Render no puede acceder a tu Dropbox local, tienes estas opciones:

### Opción A: Usar Dropbox API (Recomendado para producción)
Modificar el código para usar la API de Dropbox en lugar de acceso local:
- Crear app en Dropbox Developers
- Usar token de acceso de la API
- Archivos se sincronizan automáticamente

### Opción B: Almacenamiento en el Servidor (Más simple)
Dejar que Render almacene los archivos JSON localmente:
- Quita la variable `DROPBOX_PATH` de las variables de entorno
- Los archivos se guardarán en el sistema de archivos de Render
- ⚠️ Render puede reiniciar el servicio y perder los archivos (plan gratuito)

### Opción C: Sistema Híbrido (Recomendación actual)
- **GitHub Actions**: Sigue enviando alertas automáticas cada 5 minutos (ACTUAL)
- **Render Bot**: Solo para comandos interactivos (/resumen, etc.)
- **Dropbox Local**: Archivos JSON siguen en tu PC, sincronizados por GitHub Actions

## 📊 Monitoreo

### Ver Logs en Tiempo Real
1. En Render dashboard, ve a tu servicio
2. Pestaña "Logs"
3. Verás todos los prints y errores del bot

### Reiniciar el Bot
1. En el dashboard, pestaña "Settings"
2. Botón "Manual Deploy" → "Clear build cache & deploy"

## 💰 Límites del Plan Gratuito
- **750 horas/mes gratis** (suficiente para 24/7)
- El servicio se duerme después de 15 minutos sin actividad
- Despierta automáticamente cuando recibe una solicitud
- Puede tardar 30-60 segundos en responder el primer comando después de dormir

## 🆘 Solución de Problemas

### Bot no responde después de desplegar
1. Revisa los logs en Render
2. Verifica que todas las variables de entorno estén correctas
3. Asegúrate de que el bot esté corriendo (no debe mostrar errores en logs)

### Errores de "Module not found"
- Verifica que `requirements.txt` esté en el repositorio
- Haz un "Clear build cache & deploy"

### Bot se duerme muy seguido
- Es normal en el plan gratuito
- Considera upgrade a plan pagado ($7/mes) si necesitas respuestas instantáneas

## 📝 Próximos Pasos

Una vez desplegado:
1. Prueba todos los comandos: `/resumen`, `/resumen7`, `/semanal`
2. El bot responderá 24/7 desde la nube
3. GitHub Actions sigue enviando alertas automáticas
4. Ya no necesitas tener tu PC encendida para usar el bot

---

**¿Necesitas ayuda?** Revisa los logs en Render o consulta la documentación oficial: https://render.com/docs
