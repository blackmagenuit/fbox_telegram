# 🤖 Bot de Telegram para Reportes FBOX

## Descripción

Bot interactivo de Telegram que permite solicitar reportes de alertas mediante comandos.

## Instalación

```bash
pip install requests pandas openpyxl
```

## Cómo usar

### 1. Iniciar el bot en tu PC

```bash
cd c:\Users\cabja\OneDrive\Documents\fbox_telegram_repo
python telegram_bot_handler.py
```

El bot quedará corriendo y esperando comandos. Verás:
```
🤖 Bot iniciado - 2026-01-26 14:30:00
Esperando comandos...
```

### 2. Enviar comandos desde Telegram

Abre tu chat de Telegram y envía cualquiera de estos comandos:

#### 📊 **Comandos Disponibles:**

| Comando | Descripción |
|---------|-------------|
| `/resumen` | Ver resumen de alertas (texto) |
| `/resumen7` | Recibir Excel de últimos 7 días |
| `/resumen30` | Recibir Excel de últimos 30 días |
| `/resumentodo` | Recibir Excel con todas las alertas |
| `/ayuda` | Ver lista de comandos |

### 3. Detener el bot

Presiona `Ctrl+C` en la terminal donde corre el bot.

## Ejemplo de uso

1. **Ver resumen rápido:**
   ```
   Tú: /resumen
   Bot: 📊 RESUMEN DE ALERTAS
        Total eventos: 45
        Total alertas: 67
        ...
   ```

2. **Solicitar Excel:**
   ```
   Tú: /resumen7
   Bot: ⏳ Generando reporte de últimos 7 días...
   Bot: [Envía archivo Excel]
   Bot: ✅ Reporte enviado correctamente
   ```

## Modo de ejecución

### Opción 1: Ejecutar manualmente cuando necesites
- Inicias el bot cuando quieras recibir comandos
- Lo detienes cuando termines

### Opción 2: Mantenerlo corriendo siempre
- Ejecutar en segundo plano (recomendado para servidor)
- En Windows, puedes crear un servicio o tarea programada

### Opción 3: Ejecutar en GitHub Actions (futuro)
- Se puede configurar para que responda a comandos desde la nube
- Requiere configuración adicional de webhook

## Notas importantes

- El bot solo responde a mensajes del `CHAT_ID` configurado
- Necesita que `fbox_alerts_history.json` exista con datos
- Los archivos Excel se envían como documentos descargables
- Los archivos temporales se eliminan automáticamente después de enviar

## Seguridad

- Solo responde al chat autorizado (tu `CHAT_ID`)
- Otros usuarios no pueden usar el bot
- No expone información sensible

## Troubleshooting

**Error: "Falta instalar dependencias"**
```bash
pip install pandas openpyxl
```

**Error: "Falta configurar BOT_TOKEN"**
- Verifica que tu archivo `.env` tenga `BOT_TOKEN` y `CHAT_ID`

**Bot no responde:**
- Verifica que esté corriendo (`python telegram_bot_handler.py`)
- Verifica que uses el comando correcto (debe empezar con `/`)
