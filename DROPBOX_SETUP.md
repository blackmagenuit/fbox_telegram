# Configuración de Dropbox API para Render

## Variables de Entorno Requeridas

Una vez que hayas generado el **Access Token** en https://www.dropbox.com/developers/apps:

En Render, agrega esta nueva variable de entorno:

| Variable | Valor |
|----------|-------|
| `DROPBOX_ACCESS_TOKEN` | El token largo que generaste (empieza con `sl.` o similar) |

## IMPORTANTE: Seguridad

**NUNCA** incluyas estos valores en el código o en commits de Git:
- ❌ App key / Client ID
- ❌ App secret / Client Secret
- ❌ Access Token

Solo se usan como **variables de entorno** en Render y en tu archivo `.env` local.

Estos valores se obtienen de tu app en Dropbox Developers y deben mantenerse privados.

## ¿Qué hace esto?

Con Dropbox API configurado:
- ✅ El bot en Render lee `fbox_alerts_history.json` directamente desde tu Dropbox
- ✅ Los Excel generados se suben automáticamente a tu carpeta de Dropbox
- ✅ GitHub Actions y el bot comparten el mismo storage
- ✅ No saturamos GitHub con commits de datos

## Estructura

Todos los archivos se guardan en:
```
/Archivos de Informatica/Archivos de FBOX/
├── fbox_state.json
├── fbox_alerts_history.json
├── last_report_time.json
└── reporte_alertas_*.xlsx
```

Esta es la misma carpeta que usa tu GitHub Actions local.
