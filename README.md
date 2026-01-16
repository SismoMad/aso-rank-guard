# 🛡️ ASO Rank Guard

**Herramienta personal de monitorización de rankings en App Store para indie developers**

Rastreador automático de keywords + alertas inteligentes vía Telegram para tu app **Audio Bible Stories & Chat** (BibleNow, id6749528117)

---

## 🎯 ¿Qué hace ASO Rank Guard?

Monitoriza **automáticamente** el ranking de tu app en el App Store para 10-20 keywords clave, detecta caídas/subidas importantes (>5 posiciones) y te envía **alertas inmediatas** por Telegram.

**100% gratis, ético y diseñado para indie developers** que no pueden pagar $50-300/mes en tools profesionales (AppTweak, Sensor Tower, etc.)

### Características principales

✅ **Monitorización automática 24/7** de keywords en múltiples países (ES, US, MX, etc.)  
📊 **Histórico en CSV** fácil de analizar en Excel  
🚨 **Alertas Telegram** solo cuando hay cambios reales (sin spam)  
🚀 **ASO Expert PRO** con scoring 0-100 y evidencia real  
💡 **Opportunity scoring** (Impact + Feasibility + Relevance + Risk)  
🎯 **Intent detection** (8 tipos: audio, sleep, kids, chat, etc.)  
⚠️ **Alertas con severidad** (CRITICAL/HIGH/MEDIUM/LOW + causas)  
📈 **Análisis competitivo** (canibalización, business impact)  
🔮 **Tareas accionables** (formato backlog con expected impact)  
⏰ **Checks automáticos** diarios a la hora que elijas  
📱 **Reportes profesionales** con evidencia numérica  

---

## 🚀 Inicio Rápido (Setup 15 minutos)

### 1. Requisitos previos

- Python 3.8+ instalado
- Cuenta de Telegram (para alertas)

### 2. Instalar dependencias

```bash
cd /Users/javi/aso-rank-guard
pip install -r requirements.txt
```

**Nota:** Si solo quieres lo esencial (sin Google Trends ni IA):

```bash
pip install requests pandas pyyaml schedule python-telegram-bot
```

### 3. Configurar Telegram Bot

1. Abre Telegram y busca `@BotFather`
2. Envía `/newbot` y sigue instrucciones
3. Copia el **BOT_TOKEN** que te da
4. Para obtener tu **CHAT_ID**:
   - Busca `@userinfobot` en Telegram
   - Envía cualquier mensaje
   - Copia el ID que te responde

### 4. Editar configuración

Abre `config/config.yaml` y modifica:

```yaml
app:
  id: 6749528117  # Tu App ID (ya configurado para BibleNow)

keywords:
  # Añade/quita los keywords que quieras monitorizar
  - "audio bible stories"
  - "christian bedtime prayer"
  - "bible chat ai"
  # ... hasta 20 keywords recomendado

countries:
  - ES
  - US
  # Añade: MX, AR, CO, etc.

alerts:
  telegram:
    enabled: true
    bot_token: "PEGA_AQUI_TU_BOT_TOKEN"
    chat_id: "PEGA_AQUI_TU_CHAT_ID"
```

### 5. Primer test

Ejecuta un check manual para verificar que todo funciona:

```bash
cd /Users/javi/aso-rank-guard
python src/rank_tracker.py
```

Deberías ver:
- Logs de búsqueda de keywords
- Resultados guardados en `data/ranks.csv`
- Mensaje en Telegram (si está configurado)

---

## 📖 Uso diario

### Comandos Disponibles

```bash
./run.sh track       # Solo tracking de keywords
./run.sh monitor     # Tracking + análisis experto a Telegram
./run.sh expert      # Ver análisis experto en terminal
./run.sh status      # Ver últimos resultados
./run.sh test        # Probar Telegram
./run.sh schedule    # Iniciar scheduler automático
```

### 🎓 Análisis Experto (NUEVO - PRO VERSION)

Ahora recibes insights profundos de nivel profesional directamente en Telegram:

```bash
./run.sh monitor  # Usa PRO automáticamente
./run.sh pro      # Solo análisis PRO en terminal
```

**🚀 VERSION PRO incluye:**
- 📊 **Evidencia real**: rank_now + rank_prev + delta + volume + confidence
- 🎯 **Opportunity Scoring 0-100**: Impact + Feasibility + Relevance + Risk
- 💡 **Intent Detection**: 8 tipos (audio, sleep, kids, chat, etc.)
- ⚠️ **Severidad contextual**: CRITICAL/HIGH/MEDIUM/LOW con causas
- 🔄 **Detección de canibalización**: keywords similares compitiendo
- ✅ **Tareas accionables**: formato backlog con expected impact
- 📈 **Métricas weighted**: por volumen, no simples promedios

**Ejemplo de output:**
```
🎯 Focus Next 7d: bedtime bible stories (Score: 63/100)

📊 KEY METRICS
✅ Visibility (weighted): 92.5%
🎯 Share of Voice: 3.7%

👀 WATCHLIST
bedtime bible stories | #21 | Score:63 | subtitle
  Action: Add to subtitle: "Bedtime Bible & stories for Sleep"
  Expected: +5-10 ranks / +150 impressions
  Confidence: high

🔄 CANNIBALIZATION
⚠️ 18 similar keywords averaging #114
  💡 Consolidate into 1-2 strong variants
```

**Documentación completa:**
- [ASO_PRO.md](ASO_PRO.md) - **NUEVA** Documentación PRO completa
- [Guía Rápida](QUICK_START_EXPERT.md)
- [Ejemplos](EJEMPLO_ANALISIS.md)

### Opción A: Ejecución manual

Cada vez que quieras hacer un check:

```bash
./run.sh track
```

O con análisis completo:

```bash
./run.sh monitor
```

### Opción B: Automático con cron (macOS/Linux)

Para ejecutar **automáticamente cada día a las 9:00 AM**:

1. Abre terminal y escribe:

```bash
crontab -e
```

2. Añade esta línea (ajusta la ruta):

```bash
0 9 * * * cd /Users/javi/aso-rank-guard && ./run.sh monitor >> logs/cron.log 2>&1
```

3. Guarda y cierra

Ahora recibirás el análisis experto cada mañana en Telegram.

### Opción C: Scheduler integrado

```bash
./run.sh schedule
```

Mantiene el proceso corriendo y ejecuta checks automáticos.

---

## 📊 Analizar histórico

Los datos se guardan en `data/ranks.csv`. Puedes:

1. **Abrirlo en Excel/Numbers** para ver evolución
2. **Crear gráficos** de ranking por keyword
3. **Detectar tendencias** semanales/mensuales

Columnas del CSV:
- `date`: Fecha y hora del check
- `keyword`: Keyword buscado
- `country`: País (ES, US, etc.)
- `rank`: Posición (1-250, o 999 si no aparece)
- `app_id`: ID de tu app

---

## 🔔 Tipos de alertas

### Alerta de caída ⬇️

```
⬇️🚨 ¡CAMBIO DETECTADO!

🔴 Keyword: audio bible stories
🌍 País: ES
📊 Ranking: #42 → #49 (-7 posiciones)
⏰ 15/01/2026 09:05
```

### Alerta de subida ⬆️

```
⬆️🎉 ¡CAMBIO DETECTADO!

🟢 Keyword: bible chat ai
🌍 País: US
📊 Ranking: #87 → #72 (+15 posiciones)
⏰ 15/01/2026 09:05
```

### Resumen diario 📊

Si no hay cambios significativos, puedes habilitar resúmenes diarios (editar código para activar).

---

## 🧪 Testing & Debug

### Test de alertas Telegram

```bash
python src/telegram_alerts.py
```

Enviará un mensaje de prueba para verificar que Telegram funciona.

### Test de Google Trends

```bash
python src/trend_analyzer.py
```

Analizará tendencias de ejemplo (requiere `pytrends` instalado).

### Modo debug

En `config/config.yaml`:

```yaml
debug:
  enabled: true
  test_mode: true  # No envía alertas reales, solo muestra en logs
```

---

## 📈 Funciones avanzadas (opcional)

### 1. Análisis de tendencias con Google Trends

Habilita en `config/config.yaml`:

```yaml
trends:
  google_trends:
    enabled: true
    region: "US"  # o "ES"
```

Luego puedes usar:

```python
from src.trend_analyzer import TrendAnalyzer
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

analyzer = TrendAnalyzer(config)

# Analizar un keyword
trend = analyzer.get_keyword_trend('bible stories for sleep', region='US')
print(trend)

# Análisis estacional (útil para keywords religiosos)
seasonal = analyzer.predict_seasonal_interest('christian bedtime prayer')
print(f"Meses pico: {seasonal['peak_months']}")
```

### 2. Integración con Google Calendar (próximamente)

Detectar eventos de "app update" en tu calendario y hacer checks extras automáticamente.

### 3. Insights con IA (OpenAI)

Si quieres análisis cualitativos de keywords (cuesta dinero):

```yaml
trends:
  ai_analysis:
    enabled: true
    api_key: "tu-api-key-openai"
    model: "gpt-4o-mini"
```

---

## 🗂️ Estructura del proyecto

```
aso-rank-guard/
├── config/
│   ├── config.yaml              # ⚙️ Configuración principal
│   ├── credentials.json         # 🔐 Google Calendar (opcional)
│   └── token.json               # 🔐 Google Calendar (opcional)
├── data/
│   └── ranks.csv                # 📊 Histórico de rankings
├── logs/
│   └── rank_guard.log           # 📝 Logs de ejecución
├── src/
│   ├── rank_tracker.py          # 🎯 Script principal
│   ├── telegram_alerts.py       # 🔔 Módulo de alertas
│   └── trend_analyzer.py        # 📈 Análisis de tendencias
├── requirements.txt             # 📦 Dependencias Python
└── README.md                    # 📖 Esta guía
```

---

## ❓ FAQ

### ¿Es legal usar iTunes Search API?

**Sí**, es 100% legal y pública. Es la API oficial de Apple para búsquedas. Solo evita hacer miles de requests/hora.

### ¿Cuántos keywords puedo monitorizar?

Recomendamos **10-20 keywords** para:
- No saturar la API (rate limits)
- Mantener checks rápidos (<5 min)
- Alertas relevantes (no spam)

Si necesitas más, puedes ejecutar en batches o añadir delays.

### ¿Funciona en Windows?

Sí, solo cambia los comandos de terminal por PowerShell. El código Python es multiplataforma.

### ¿Puedo monitorizar varias apps?

Sí, puedes duplicar la configuración o modificar el código para iterar sobre múltiples app IDs.

### ¿Qué pasa si mi app no aparece en top 250?

Se marca como `rank: 999` en el CSV. Considera optimizar metadata o elegir keywords menos competitivos.

### ¿Cómo añado más países?

Edita `config/config.yaml` → `countries: [ES, US, MX, AR, CO, ...]`

Códigos ISO: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

---

## 🛠️ Roadmap / Mejoras futuras

- [ ] Interfaz web con Streamlit para visualizar gráficos
- [ ] Soporte multi-app (trackear varias apps simultáneamente)
- [ ] Detector de competidores nuevos
- [ ] Integración con Google Search Console
- [ ] Exportar reportes PDF mensuales
- [ ] Predicción de rankings con ML

---

## 🙌 Créditos

Desarrollado con ❤️ para **Audio Bible Stories & Chat** (BibleNow)

**Autor:** Javi (indie developer)  
**App:** [Audio Bible Stories & Chat en App Store](https://apps.apple.com/app/id6749528117)  
**Versión:** 1.0.0  
**Fecha:** Enero 2026

---

## 📄 Licencia

Uso personal. Si lo compartes o lo conviertes en producto, menciona la fuente.

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa logs en `logs/rank_guard.log`
2. Verifica que `config/config.yaml` tiene BOT_TOKEN correcto
3. Prueba `python src/telegram_alerts.py` para test
4. Abre un issue si algo falla

**¡Feliz tracking y que tus rankings suban! 🚀📈**
