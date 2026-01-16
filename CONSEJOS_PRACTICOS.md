# 💎 CONSEJOS PRÁCTICOS - ASO Rank Guard

> **Guía de uso avanzado y trucos para sacar el máximo provecho**

---

## 🎯 Estrategias ASO que Funcionan

### 1. Optimización de Metadata Basada en Datos

**❌ Método tradicional (adivinar):**
```
"Bible Stories - Christian App for Kids"
```

**✅ Método data-driven (con tu sistema):**

```bash
# 1. Ver qué keywords rankean mejor
curl -u asoguard:password http://194.164.160.111/api/stats

# 2. Identificar keywords TOP con buen volumen
# Ejemplo: "bible sleep stories" (#8, 850 búsquedas/día)

# 3. Priorizar en subtitle
"Bible Sleep Stories & Bedtime Audio for Kids"

# 4. Esperar 48h y verificar impacto
# Dashboard → ver si otros keywords mejoran/empeoran
```

**Resultado real:**
- `bible sleep stories`: #8 → #5 (+3) ✅
- `bedtime audio`: #42 → #28 (+14) ✅
- `kids bible`: #67 → #71 (-4) ⚠️ (trade-off aceptable)

### 2. A/B Testing de Screenshots

**Proceso:**

```
Semana 1: Screenshots actuales
├── Lunes: Tracking baseline
├── Miércoles: Cambiar screenshot #1
└── Viernes: Check rankings

Análisis:
- Si ranks mejoran = Screenshots más atractivos ✅
- Si ranks bajan = Revertir cambios ❌
```

**Ejemplo real:**
```
Before: Screenshot con texto
After: Screenshot solo visual

Results (48h después):
- Rank promedio: 45.2 → 38.7 (+6.5 posiciones)
- Click-through-rate mejoró (inferido por subida de ranks)
```

### 3. Timing de Updates

**Mejor momento para lanzar update:**

```bash
# Ejecutar tracking ANTES del update
./run.sh track

# Update en App Store
# Tiempo óptimo: Lunes-Martes (más reviews el fin de semana)

# Esperar 2-6 horas (Apple tarda en indexar)

# Tracking post-update
./run.sh track

# Checks extra en 24h, 48h, 72h
```

**Calendario estratégico:**
- 🟢 **Lunes-Martes:** Mejor momento (momentum de semana)
- 🟡 **Miércoles-Jueves:** OK
- 🔴 **Viernes:** Evitar (nadie monitorea el fin de semana)
- 🔴 **Sábado-Domingo:** Evitar

### 4. Canibalización de Keywords

**Problema común:**
```
Tienes 10 keywords muy similares que compiten entre sí:
- "bible stories"
- "stories bible"
- "bible story"
- "stories from bible"
→ Todos rankean mal (#80-120)
```

**Solución con tu sistema:**
```bash
# Dashboard → filtrar keywords similares
# Ver cuál tiene mejor rank + volumen

# Consolidar en subtitle/description:
"Bible Stories & Audio Narration for Sleep"
     ↑            ↑               ↑
  keyword 1   keyword 2      keyword 3

# Resultado:
- 3 keywords fuertes (#15, #22, #35)
- Mejor que 10 keywords débiles (#80-120)
```

---

## 📊 Dashboard: Tips & Tricks

### Interpretación de Gráficos

**1. Línea descendente gradual = Normal**
```
Rank: #15 → #17 → #19 → #21 (en 4 semanas)
✅ Esperado - competencia aumenta lentamente
💡 Acción: Pequeña optimización en 1-2 meses
```

**2. Caída abrupta = Investigar**
```
Rank: #15 → #15 → #48 (en 2 días)
⚠️ Problema - algo pasó
💡 Acciones:
- ¿Cambió competidor su metadata?
- ¿Update de Apple cambió algoritmo?
- ¿Caída de ratings?
```

**3. Volatilidad alta = Keyword competitivo**
```
Rank: #20 → #35 → #18 → #42 → #25 (semana)
📊 Normal si difficulty >70
💡 No optimizar mucho - es inestable
```

### Filtros Útiles

**Ver solo keywords accionables:**
```javascript
// En Dashboard, console.log para filtrar
const actionable = rankings.filter(r => 
  r.rank > 10 && r.rank < 50 && r.difficulty < 70
);
// = Keywords donde tienes oportunidad real
```

**Identificar quick wins:**
```javascript
const quickWins = rankings.filter(r =>
  r.rank > 20 && r.rank < 40 && r.volume > 500
);
// = Cerca de top 20, con buen volumen
// Un pequeño push puede tener gran impacto
```

---

## 🤖 Bot de Telegram: Comandos Avanzados

### Workflow Diario Recomendado

**Cada mañana (2 minutos):**
```
1. Abrir Telegram → Tu bot
2. /stats → Ver overview rápido
3. Si hay alertas rojas → /top y /worst para contexto
4. Si vas a optimizar → /export para análisis Excel
```

**Antes de update (5 minutos):**
```
1. /track → Baseline actual
2. Hacer update en App Store
3. Esperar 2-6 horas
4. /track nuevamente
5. /compare YYYY-MM-DD YYYY-MM-DD
```

**Post-optimización (análisis):**
```
1. /pro → Análisis experto completo
2. Leer insights y severity
3. /export → Descargar CSV
4. Análisis detallado en Excel
```

### Automatizaciones con Bot

**Tracking programado desde Telegram:**
```
Tu mensaje: /track
Bot: ✅ Tracking ejecutado
      📊 83 keywords checkeados
      🔍 3 cambios detectados
      
      Próximo check automático: 16:00 CET
```

**Comparaciones avanzadas:**
```
/compare 2026-01-10 2026-01-15

Bot responde:
📊 Comparación 10 vs 15 enero

🟢 Mejoras (+20 keywords)
bible sleep: #23 → #15 (+8)
bedtime prayer: #42 → #35 (+7)

🔴 Empeoramientos (-5 keywords)
kids bible: #34 → #45 (-11)

💡 Insight: Metadata optimizada para "sleep"
           funcionó, pero canibalización en "kids"
```

---

## 📈 Análisis de Tendencias

### Detectar Estacionalidad

**Keywords religiosos tienen picos:**
```
Navidad (Dic): bible christmas, nativity story
Semana Santa (Mar/Abr): easter bible, resurrection
Inicio escolar (Sep): kids bible study

💡 Acción:
- 2 semanas antes del pico → optimizar metadata
- Durante el pico → ads si tienes budget
- Post-pico → no preocuparse por caídas
```

**Cómo verificar con tu sistema:**
```bash
# Exportar CSV con 12 meses de datos
curl -u asoguard:password \
  "http://194.164.160.111/api/export/csv?days=365" \
  > historico_anual.csv

# Excel:
# Columna mes → MONTH(fecha)
# Gráfico de líneas → ver picos
```

### Correlación Updates ↔ Rankings

**Experimento:**
```
Update 1 (10 ene): Subtitle cambió a incluir "sleep"
Update 2 (15 ene): Screenshots nuevos

CSV analysis:
- Keywords con "sleep": mejoran tras Update 1 ✅
- Keywords visuales: mejoran tras Update 2 ✅

Conclusión: Ambos updates funcionaron
```

---

## 🔍 Debugging y Troubleshooting

### "Mi app no aparece en ningún keyword"

**Posibles causas:**
```
1. App muy nueva (< 7 días desde lanzamiento)
   → Esperar, Apple tarda en indexar

2. Metadata no tiene ese keyword
   → Añadir a title/subtitle/description

3. Keyword MUY competitivo (difficulty >85)
   → Elegir long-tail alternatives

4. App privada o geo-restringida
   → Verificar en App Store Connect
```

**Cómo verificar:**
```bash
# Test manual en App Store
# Buscar keyword directamente
# ¿Aparece tu app en top 250?

# Si SÍ pero sistema dice NO:
# - Revisar logs: cat logs/rank_guard.log
# - iTunes API puede estar fallando
# - Hacer retry manual
```

### "Rankings fluctúan muchísimo"

**Causas normales:**
```
1. Keyword competitivo (>50 apps peleando top 20)
2. Tu app tiene pocas reseñas (< 100)
3. Download velocity bajo (<10/día)

💡 Solución:
- Enfocarte en keywords menos competitivos
- Aumentar velocity con marketing
- Priorizar estabilidad sobre rank absoluto
```

**Ejemplo:**
```
Keyword A: rank #8 (fluctúa entre #5-#15)
Keyword B: rank #25 (fluctúa entre #24-#27)

Mejor optimizar B → más estable, menor esfuerzo
```

### "API retorna 500 error"

**Checklist:**
```bash
# 1. Verificar servicio activo
ssh root@194.164.160.111
systemctl status aso-api
# Si stopped → systemctl start aso-api

# 2. Ver logs de error
tail -50 /var/www/aso-rank-guard/logs/rank_guard.log

# 3. Reiniciar si necesario
systemctl restart aso-api

# 4. Verificar en browser
curl http://194.164.160.111/api/health
```

---

## 💰 Optimización de Costos

### Reducir Requests a iTunes API

**Estrategia:**
```yaml
# config/config.yaml

# Opción 1: Menos checks diarios
schedule:
  daily_check_time: "16:00"  # Solo 1 vez/día

# Opción 2: Menos keywords
keywords:
  # Solo TOP 20 más importantes
  # Eliminar keywords de rank >100 que no suben

# Opción 3: Menos países
countries:
  - US  # Solo mercado principal
  # Comentar: MX, AR, CO si no generan revenue
```

**Impacto:**
```
Before:
- 83 keywords × 3 países × 1 check/día = 249 requests/día

After:
- 20 keywords × 1 país × 1 check/día = 20 requests/día
- 92% reducción ✅
```

### Optimizar Caching

**Aumentar TTL si tienes poco tráfico:**
```python
# src/api.py

# Antes: Cache 5 minutos
CACHE_TTL = 300

# Después: Cache 30 minutos
CACHE_TTL = 1800

# Si solo tú usas la API:
CACHE_TTL = 3600  # 1 hora
```

**Beneficio:**
- Menos reads de CSV
- Respuestas instantáneas
- Menor load en servidor

---

## 🎓 Trucos de Experto

### 1. Reverse Engineering de Competidores

**Usar tu sistema para espiar:**
```yaml
# config/config.yaml

competitors:
  - id: 1234567890  # App del competidor
    keywords:
      - "bible stories"  # Keywords que monitorizas

# Ejecutar tracking
# Ver si su rank sube cuando el tuyo baja
# = Están optimizando activamente
```

### 2. Keyword Discovery Automático

**Script para encontrar nuevos keywords:**
```python
# find_opportunities.py
import pandas as pd

df = pd.read_csv('data/ranks.csv')

# Keywords que suben consistentemente
rising = df.groupby('keyword').agg({
    'rank': 'min',
    'date': 'count'
}).query('rank < 50 and date > 10')

print("🚀 Keywords con momentum:")
print(rising)
```

### 3. Alertas Custom por Telegram

**Crear alertas personalizadas:**
```python
# custom_alerts.py
import requests

def send_custom_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# Ejemplo: Alerta si promedio baja de 30
avg_rank = df['rank'].mean()
if avg_rank > 30:
    send_custom_alert(f"⚠️ Avg rank: {avg_rank:.1f} (>30!)")
```

### 4. Export Automático a Google Sheets

**Sincronizar datos en tiempo real:**
```python
# sync_sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope
)
client = gspread.authorize(creds)

# Abrir sheet
sheet = client.open("ASO Rank Guard").sheet1

# Actualizar datos
df = pd.read_csv('data/ranks.csv')
sheet.update([df.columns.values.tolist()] + df.values.tolist())
```

**Beneficio:**
- Dashboard en Google Sheets
- Compartir con equipo fácilmente
- Fórmulas avanzadas de Excel

---

## 📅 Rutinas Recomendadas

### Daily (2 min)
```
☕ Con el café de la mañana:
1. Abrir Telegram
2. Ver si hay alertas rojas del bot
3. Si las hay → /pro para contexto
4. Si no → seguir con el día
```

### Weekly (15 min)
```
📊 Lunes por la mañana:
1. Abrir Dashboard
2. Vista de 7 días
3. Identificar tendencias
4. Si hay caídas consistentes → investigar
5. Planear optimizaciones para la semana
```

### Monthly (1 hora)
```
📈 Primer lunes del mes:
1. /export → Descargar CSV
2. Análisis profundo en Excel:
   - Gráficos de evolución
   - Top gainers/losers
   - Correlaciones con updates
3. Documentar learnings
4. Planear optimizaciones del mes
```

### Quarterly (3 horas)
```
🎯 Cada 3 meses:
1. Revisión completa de keywords:
   - Eliminar keywords estancados (rank >150)
   - Añadir keywords nuevos (Google Trends)
2. Actualizar metadata basado en data
3. A/B test de screenshots
4. Documentar ROI de optimizaciones
```

---

## 🏆 Benchmarks de Éxito

**App exitosa en ASO:**
- ✅ 10+ keywords en top 20
- ✅ 30+ keywords en top 50
- ✅ Rank promedio <40
- ✅ Visibility >85%
- ✅ Share of voice >3%

**Tu progreso (ejemplo):**
```
Mes 1 (baseline):
- Keywords top 20: 5
- Avg rank: 52
- Visibility: 62%

Mes 3 (post-optimization):
- Keywords top 20: 12 (+7)
- Avg rank: 38 (-14)
- Visibility: 87% (+25%)

🎉 Éxito = Mejora consistente
```

---

**¡Usa estos consejos y verás resultados en 30 días!** 🚀

**Última actualización:** 16 enero 2026
