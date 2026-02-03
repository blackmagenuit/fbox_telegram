# 🔒 Guía de Seguridad - FBOX Telegram Bot

## ⚠️ IMPORTANTE: Protección de Credenciales

Este documento explica cómo mantener tus credenciales seguras cuando uses GitHub.

## ✅ Verificación de Seguridad

Antes de subir a GitHub, verifica:

### 1. Archivo `.gitignore` configurado
El archivo `.gitignore` ya está configurado para **NO** subir:
- ✅ `.env` (con tus credenciales reales)
- ✅ Archivos de estado (`.json`)
- ✅ Reportes Excel generados

### 2. Usar `.env.example` (sin credenciales)
El archivo `.env.example` debe tener **SOLO placeholders**:
```
BOT_TOKEN=TU_BOT_TOKEN_AQUI
CHAT_ID=TU_CHAT_ID_AQUI
FBOX_SSID=TU_SSID_AQUI
FBOX_ADMIN_TOKEN=TU_ADMIN_TOKEN_AQUI
DROPBOX_PATH=
```

### 3. GitHub Secrets para Actions
Tus credenciales reales se configuran en GitHub como **Secrets**:
1. Ve a tu repo → Settings → Secrets and variables → Actions
2. Agrega como secrets (nunca visibles públicamente):
   - `BOT_TOKEN`
   - `CHAT_ID`
   - `FBOX_SSID`
   - `FBOX_ADMIN_TOKEN`

## 🚫 NUNCA Subas a GitHub

- ❌ Archivo `.env` con credenciales reales
- ❌ Screenshots con tokens visibles
- ❌ Archivos de log con credenciales
- ❌ Archivos de backup de `.env`

## ✅ Comandos Seguros para Git

Antes de hacer push, verifica:
```bash
# Ver qué archivos se van a subir
git status

# Verificar que .env NO esté en la lista
git ls-files | grep .env
# Debe mostrar SOLO: .env.example

# Si accidentalmente agregaste .env, removelo:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

## 🔄 Actualizar Credenciales en GitHub

Cuando necesites actualizar las cookies de FBOX:

**Opción 1: Desde el navegador**
1. Abre DevTools (F12) → Application → Cookies
2. Copia `ssid` y `Admin-Token`
3. Actualiza los secrets en GitHub (Settings → Secrets)

**Opción 2: Script local (sin subir)**
```bash
python update_cookies.py  # Actualiza .env localmente
# NO hagas git push del .env
# Solo actualiza los secrets en GitHub manualmente
```

## 📋 Checklist Antes de Subir a GitHub

- [ ] Verificar que `.env` está en `.gitignore`
- [ ] Archivo `.env.example` solo tiene placeholders
- [ ] README no contiene credenciales reales
- [ ] Screenshots no muestran tokens
- [ ] Ejecutar `git status` para ver qué se va a subir
- [ ] Confirmar que `.env` NO aparece en `git status`

## 🆘 Si Subiste Credenciales por Error

1. **Rotar las credenciales inmediatamente:**
   - Telegram: Revoca el bot token con @BotFather
   - FBOX: Cierra sesión y genera nuevas cookies

2. **Eliminar del historial de Git:**
```bash
# Remover archivo del historial
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Forzar push
git push origin --force --all
```

3. **Actualizar con nuevas credenciales**

## 📞 Soporte

Si tienes dudas sobre seguridad, consulta antes de hacer push.
