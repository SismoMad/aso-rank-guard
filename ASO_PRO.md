# 🚀 ASO Expert PRO - Documentación Profesional

**Versión**: 2.0  
**Actualizado**: 15 enero 2026  
**Status**: ✅ Production Ready

---

## 🎯 REGLAS FUNDAMENTALES (v2.0)

### ✅ REGLA #1: Comparación diaria (cada 24h)
**Funcionamiento**:
- Compara siempre **última ejecución vs anterior**
- Cada ejecución del monitor crea un punto de comparación
- Si ejecutas diariamente → comparas "today vs yesterday"
- Data quality: `✅ OK` (si hay 2+ mediciones) / `❌ No comparison` (primera vez)

### ✅ REGLA #2: Focus requiere evidencia completa
**NO PERMITIDO**: `Focus: scripture bedtime stories (Score 64)`

**OBLIGATORIO**:
```
🎯 Focus next 7d:
• scripture bedtime stories — #47 (Δ +3)
  Score 64/100 = I40+F10+R14−K0
  Vol: 500 | Diff: low | Intent: informational
  Action: Add to keywords field
  Goal: Top 30 | Confidence: MEDIUM
```

### 📊 REGLA #3: Score siempre con desglose
```
Score 64/100 = Impact(40) + Feasibility(10) + Relevance(14) − Risk(0)
```

### 📋 REGLA #4: Estructura DO NOW / NEXT / WATCHLIST / THREATS / CLEANUP
- **DO NOW** (Max 3): Con WHAT/WHY/HOW/MEASURE/CONF
- **NEXT** (Max 3): Con triggers para escalar
- **WATCHLIST** (Max 5): Con triggers específicos
- **THREATS** (Max 3): Solo si hay comparación válida
- **CLEANUP** (Max 5): Keywords ignorables con reasons

### 🧩 REGLA #5: Cannibalization = Head vs Tail
```
Cluster: bedtime bible stories
Head: bible sleep stories #16, bedtime bible stories #21
Tail: 15 variants avg #133
Status: Head strong / Tail weak
Fix: Keep head, prune tail
```

---

## ✅ Qué cambia respecto a la versión básica

La versión PRO implementa **TODAS** las mejores prácticas profesionales de ASO:

### 1️⃣ **EVIDENCIA REAL** (No más afirmaciones sin datos)

**Antes:**
```
"bible sleep stories está en posición #16"
```

**Ahora (PRO):**
```
bible sleep stories | #16 | #19 | +3 | vol:500 | medium | high

Significa:
- Rank actual: #16
- Rank anterior: #19
- Delta: +3 (mejoró 3 posiciones)
- Volumen estimado: 500 búsquedas/mes
- Dificultad: medium
- Confidence: high
```

---

### 2️⃣ **OPPORTUNITY SCORING 0-100** (Priorización inteligente)

**Fórmula:**
```
Score = Impact (0-40) + Feasibility (0-30) + Relevance (0-20) + Risk (-10-0)

Impact: Volumen normalizado × 40
Feasibility: Proximidad a top10 (15pts) + Tendencia (15pts)
Relevance: Match con tu producto (20pts)
Risk: -10 si es keyword sensible (religión, niños)
```

**Buckets:**
- **80-100**: DO NOW (hacer YA)
- **60-79**: NEXT (siguiente semana)
- **40-59**: WATCH (monitorizar)
- **<40**: IGNORE (no vale la pena)

**Ejemplo Real:**
```
bible sleep stories
Score: 63/100
├─ Impact: 40 (vol alto)
├─ Feasibility: 15 (posición #16, cerca del top10)
├─ Relevance: 18 (match perfecto con tu app)
└─ Risk: -10 (keyword sensible: "bible" + "kids")
Bucket: NEXT
```

---

###3️⃣ **INTENT DETECTION** (Qué busca el usuario + cómo optimizar)

**Intenciones detectadas:**

| Intent | Patterns | Optimización | Visual |
|--------|----------|--------------|---------|
| **AUDIO** | audio, listen, podcast | Title: "Audio Bible" | Player UI en screenshots |
| **SLEEP/RELAX** | sleep, calm, bedtime | Subtitle: "Bedtime Bible & Sleep" | Night mode visuals |
| **KIDS/FAMILY** | kids, children, family | Subtitle: "Safe for Kids" | Kid-friendly screenshots |
| **CHAT/AI** | chat, ai, ask | Subtitle: "Chat with Bible AI" | Chat demo screenshots |
| **HABIT/ROUTINE** | daily, morning, plan | Subtitle: emphasizing routine | Screenshots con reminders |
| **INFORMATIONAL** | stories, what is, meaning | Description | Story library preview |

**Ejemplo:**
```
Keyword: "bedtime bible stories"
Intent: SLEEP_RELAX

Action: Add to subtitle: "Bedtime Bible & bedtime bible stories for Sleep"
Visual: Create screenshot with night mode UI + calming visuals
Expected: +5-10 ranks / +150 impressions
```

---

### 4️⃣ **ALERTAS CON SEVERIDAD Y CONTEXTO** (No más falsos alarmas)

**Niveles de severidad:**

#### 🔴 CRITICAL
- Top10 → >20 posiciones
- O caída >15 con volumen alto (>200)
- **Acción**: URGENTE - investigar HOY

**Ejemplo:**
```
🔴 CRITICAL: biblenow
  #2 → #25 (-23) | Vol: 500
  💭 Probable: Competitor update OR ratings drop
  ✅ URGENT: Check top 10 competitors, review ratings
  
  Checks:
  - Search "biblenow" in App Store - check top 10
  - Compare competitor screenshots/titles
  - Review ratings last 7 days
  - Verify no metadata change on your side
```

####🟡 HIGH
- Top30 → >60 posiciones
- O caída >20 en cualquier posición
- **Acción**: Investigar en 24-48h

#### 🟠 MEDIUM
- Caída 5-10 con volumen medio (>50)
- **Acción**: Monitorizar 2-3 días

#### ⚪ LOW (no reportado)
- Ruido normal (±5 posiciones)

---

### 5️⃣ **ANÁLISIS COMPETITIVO REAL** (No especulación)

**Detección de canibalización:**
```
🔄 CANNIBALIZATION DETECTED

⚠️ 18 keywords similares averaging #114
  Keywords: "bedtime bible stories", "bible bedtime stories", "bible sleep stories"
  
  💡 Consider consolidating 18 similar terms into 1-2 strong variants
  
  Why: Múltiples keywords similares = competencia contigo mismo
  Fix: Eliminar variaciones débiles, reforzar 1-2 fuertes
```

**Análisis de dificultad real:**
- **Low**: Posición media (<50), volumen bajo → fácil de mover
- **Medium**: Top 30 con volumen medio → necesitas esfuerzo
- **High**: Top 10 + volumen alto O >100 → muy competido

---

### 6️⃣ **TAREAS ACCIONABLES** (No consejos vagos)

**Formato backlog:**
```
**Task**: Add "bedtime bible stories" to subtitle
**Why**: bedtime bible stories #21 | Score:63 | Vol:500 | sleep_relax
**Expected**: +5-10 ranks / +150 impressions
**Owner**: ASO
**ETA**: Next release
**Measure**: Rank after 7 days + CVR change
**Confidence**: high
```

Cada tarea incluye:
- ✅ QUÉ hacer exactamente
- ✅ POR QUÉ (evidencia numérica)
- ✅ CUÁNTO impacto esperar
- ✅ CÓMO medirlo
- ✅ Nivel de confianza

---

### 7️⃣ **MÉTRICAS BIEN DEFINIDAS** (No numerología)

#### Visibility (Weighted)
```
Fórmula: (Σ vol_visible) / (Σ vol_total) × 100

Ejemplo:
Vol visible (top 250): 8,500
Vol total: 9,200
Visibility: 92.4%

NO es solo "% de keywords visibles"
SÍ es "% del volumen capturable que realmente captas"
```

#### Avg Rank (Weighted)
```
Fórmula: Σ(rank × volumen) / Σ volumen

Ejemplo:
Keyword A: rank 10, vol 500 → 10×500 = 5,000
Keyword B: rank 100, vol 50 → 100×50 = 5,000
Total: 10,000 / 550 = #18.2 (promedio ponderado)

Simple avg: (10+100)/2 = #55 ❌ ENGAÑOSO
Weighted avg: #18.2 ✅ REAL (keyword A pesa más)
```

#### Share of Voice (SOV)
```
Fórmula: (Σ vol_top20) / (Σ vol_total) × 100

Ejemplo:
Vol en top 20: 800
Vol total: 9,200
SOV: 8.7%

Interpretación: Captas 8.7% del "tráfico premium"
Objetivo: >15% para apps de nicho
```

---

### 8️⃣ **TEMPLATE PROFESIONAL TELEGRAM**

```
🎯 ASO PRO ANALYSIS - BibleNow
========================================

📅 Period: 2026-01-14 → 2026-01-15
🌎 Market: US EN
📊 Data: 83 keywords tracked

────────────────────────────────────────

📋 EXECUTIVE SUMMARY

🏆 Biggest Win: audio bible +12 ranks (#45→#33)
⚠️ Biggest Risk: bible chat HIGH (#42→#89)
🎯 Focus Next 7d: bedtime bible stories (Score: 78/100)

────────────────────────────────────────

📊 KEY METRICS

✅ Visibility (weighted): 92.5%
   % of search volume captured in top 250

📈 Avg Rank (weighted): #76.1
   Average position weighted by volume

🎯 Share of Voice: 3.7%
   % of volume in top 20 positions

────────────────────────────────────────

🔥 DO NOW (Top 3)

**bedtime bible stories**
  📍 Rank: #21 (+2) | Vol: 500 | Score: 78/100
  💡 Add to subtitle: "Bedtime Bible & bedtime bible stories for Sleep"
  🎯 Intent: sleep_relax | Confidence: high

[... 2 más]

────────────────────────────────────────

👀 WATCHLIST (Next 5)

bible sleep | #19 | Score:65 | subtitle
audio bible stories | #24 | Score:62 | subtitle

⚡ If any drops >5 ranks → escalate to DO NOW

────────────────────────────────────────

⚠️ THREATS

🔴 CRITICAL: biblenow
  #2 → #45 (-43) | Vol: 500
  💭 Probable: Competitor update OR algorithm change
  ✅ URGENT: Check top 10, verify metadata, review ratings

────────────────────────────────────────

📊 TOP MOVERS

⬆️ Gainers:
  • audio bible +12 (#33)
  • bible stories +8 (#28)

⬇️ Losers:
  • bible chat -47 (#89)

────────────────────────────────────────

🔄 CANNIBALIZATION DETECTED

⚠️ 18 similar keywords averaging #114
  Keywords: bedtime stories, bible bedtime, sleep stories
  💡 Consolidate into 1-2 strong variants

────────────────────────────────────────

⏰ 15/01/2026 12:30
ASO Rank Guard PRO - Evidence-Based Analysis
```

---

### 9️⃣ **FEATURES PRO ADICIONALES**

#### A) Detección de Canibalización
- Agrupa keywords similares
- Detecta cuando compites contigo mismo
- Sugiere consolidación

#### B) Business Impact (no solo vanity metrics)
```
Keyword: "free bible app"
Score: 45/100
Rank: #25
Volume: 20

💡 Impact likely LOW (vol: 20) → de-prioritize
✅ Better focus on higher-volume keywords
```

#### C) Keywords Sensibles (políticas)
```
Keyword: "kids bible stories"
Risk: -10 (sensible: kids + religion)

⚠️ Use in metadata but NOT in paid targeting
⚠️ Ensure compliance with kids policies
```

---

### 🔟 **PROMPT SYSTEM INSTRUCTIONS**

El sistema PRO sigue estas reglas:

1. **No generar recomendaciones sin evidencia**
   - Siempre mostrar: rank_now, rank_prev, Δ, vol, diff
   
2. **Priorizar con Opportunity Score 0-100**
   - No usar "quick win" sin score numérico
   
3. **Máximo 3 DO NOW, 5 WATCHLIST, 3 THREATS**
   - Evitar overwhelm, enfoque en lo importante
   
4. **Cada acción debe incluir: what/why/how/measure/confidence**
   - No frases genéricas como "optimiza metadata"
   - SÍ propuestas concretas de copy
   
5. **Distinguir intent y ajustar acción**
   - Intent AUDIO → video + screenshots player
   - Intent SLEEP → night mode visuals
   - Intent KIDS → safety features + parental controls
   
6. **Evitar frases genéricas**
   - NO: "Añade keyword al subtitle"
   - SÍ: 'Add to subtitle: "BibleNow - Audio Bible Stories & bedtime sleep for Kids"'

---

## 📊 Comparativa: Básico vs PRO

| Feature | Versión Básica | Versión PRO |
|---------|---------------|-------------|
| Evidencia | ❌ Solo rank actual | ✅ Rank + prev + delta + vol + diff + confidence |
| Scoring | ❌ Categorías simples | ✅ Opportunity Score 0-100 con fórmula |
| Priorización | ⚠️ Top10/30/50 | ✅ DO NOW / NEXT / WATCH / IGNORE |
| Intent | ❌ No detecta | ✅ 8 tipos de intención + acciones específicas |
| Amenazas | ⚠️ "Cayó X posiciones" | ✅ CRITICAL/HIGH/MEDIUM + causas + checks |
| Acciones | ⚠️ "Añade a subtitle" | ✅ Template exacto + expected impact + measure |
| Métricas | ⚠️ Promedio simple | ✅ Weighted por volumen + SOV + definiciones |
| Competencia | ❌ No analiza | ✅ Detecta canibalización + business impact |
| Sensibilidad | ❌ No considera | ✅ Marca keywords sensibles + risk score |
| Reporte | ⚠️ Genérico | ✅ Executive summary + top movers + evidencia |

---

## 🚀 Cómo Usar

### Terminal
```bash
./run.sh pro
```

### Telegram (automático)
```bash
./run.sh monitor
```
El sistema usa PRO automáticamente si está disponible, fallback a básico si hay error.

### Automatizar (cron)
```bash
crontab -e

# Análisis PRO diario 9 AM
0 9 * * * cd /Users/javi/aso-rank-guard && ./run.sh monitor
```

---

## 🎯 Ejemplo de Workflow con PRO

### Lunes 9:00 AM
✅ Recibes análisis PRO en Telegram

### Lunes 10:00 AM
📖 Leer sección "DO NOW":
```
bedtime bible stories | Score: 78/100
Action: Add to subtitle
Expected: +5-10 ranks / +150 impressions
```

### Martes
✍️ Implementar:
- Cambiar subtitle a: "BibleNow - Audio Bible Stories & Bedtime Sleep for Kids"
- Crear screenshot de night mode mostrando "bedtime stories"

### Miércoles
🚀 Subir update a App Store

### Lunes siguiente
📊 Verificar:
```bash
./run.sh pro
```
Buscar en "TOP MOVERS":
```
⬆️ Gainers:
  • bedtime bible stories +7 (#21 → #14)
```

✅ Funcionó! Continuar con siguiente DO NOW

---

## 💡 Tips Pro

1. **Enfócate en Score >60**
   - Scores <40 suelen ser "vanity metrics"
   - Better ROI en 60-80 que en múltiples <40

2. **Respeta las Severidades**
   - CRITICAL = drop everything
   - HIGH = planear esta semana
   - MEDIUM = monitorizar

3. **No hagas todo a la vez**
   - 2-3 cambios por update máximo
   - Permite medir qué funciona

4. **Mide siempre después de 7 días**
   - App Store tarda 3-7 días en indexar cambios
   - No juzgues antes

5. **Usa canibalización para consolidar**
   - Si tienes 10 variantes de "bedtime bible" mal posicionadas
   - Elimina 8, refuerza 2
   - Resultado: 2 keywords fuertes vs 10 débiles

---

## 📚 Recursos Adicionales

- [ANALISIS_EXPERTO.md](ANALISIS_EXPERTO.md) - Conceptos base
- [QUICK_START_EXPERT.md](QUICK_START_EXPERT.md) - Guía rápida
- [EJEMPLO_ANALISIS.md](EJEMPLO_ANALISIS.md) - Casos de uso

---

**¡Ahora tienes un sistema de ASO nivel profesional!** 🚀

El mismo que usan agencias que cobran $5,000-10,000/mes.

Totalmente gratis, basado en evidencia, con scoring real.
