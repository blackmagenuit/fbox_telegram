# 📊 Generador de Reportes de Alertas en Excel

## Descripción

Este módulo permite generar reportes de alertas FBOX en formato Excel con múltiples hojas de análisis.

## Instalación de Dependencias

```bash
pip install pandas openpyxl
```

## Uso

### 1. Generar reporte de los últimos 7 días (por defecto)

```bash
python generate_alerts_excel.py
```

### 2. Generar reporte de los últimos 30 días

```bash
python generate_alerts_excel.py --days 30
```

### 3. Generar reporte con todas las alertas registradas

```bash
python generate_alerts_excel.py --days 0
```

### 4. Especificar nombre de archivo de salida

```bash
python generate_alerts_excel.py --days 7 --output reporte_alertas.xlsx
```

### 5. Ver solo un resumen sin generar Excel

```bash
python generate_alerts_excel.py --summary
```

## Contenido del Excel Generado

El archivo Excel contiene **4 hojas**:

### 📋 Hoja 1: "Todas las Alertas"
- **Fecha**: Fecha de la alerta
- **Hora**: Hora de la alerta
- **Día**: Día de la semana
- **Contenedor**: C01 o C02
- **Categoría**: Tipo de alerta (Crítico, Temperatura, Mineros, etc.)
- **Alerta**: Texto completo de la alerta

### 📊 Hoja 2: "Resumen por Categoría"
- Cantidad de alertas por cada categoría
- Ordenado de mayor a menor

### 🏗️ Hoja 3: "Resumen por Contenedor"
- Cantidad de alertas por contenedor (C01, C02)
- Ordenado de mayor a menor

### 📅 Hoja 4: "Resumen por Día"
- Cantidad de alertas por día
- Incluye día de la semana

## Categorías de Alertas

- **CRÍTICO - Offline**: Contenedor completamente offline
- **Temperatura Alta**: Temperatura del aceite ≥55°C
- **Mineros Caídos**: Uno o más mineros dejaron de funcionar
- **Potencia Anormal**: Caída de potencia ≥30%
- **Sistema Inmersión**: Problemas con inmersión
- **Ventilador**: Ventilador offline o con fallas
- **Otro**: Otras alertas

## Ejemplo de Uso Completo

```bash
# Ver resumen actual
python generate_alerts_excel.py --summary

# Generar reporte mensual
python generate_alerts_excel.py --days 30 --output alertas_enero_2026.xlsx
```

## Archivo de Historial

Las alertas se guardan automáticamente en:
- **fbox_alerts_history.json** (máximo 30 días de historial)

Este archivo se actualiza cada vez que se detecta una alerta.

## Notas

- El reporte se genera en la carpeta actual
- Las columnas se ajustan automáticamente al contenido
- El archivo Excel es compatible con Excel 2010+
- Los datos se ordenan cronológicamente

## Automatización

Para generar reportes semanales automáticos, puedes crear un script o agregarlo al workflow de GitHub Actions.
