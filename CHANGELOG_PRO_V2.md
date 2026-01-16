# ASO Expert PRO v2.0 - Changelog

## 🎯 Cambios Recientes

### 📊 v2.1 - Volume y Difficulty en /track (15/01/2026)

**Nueva funcionalidad:**
- El comando `/track` ahora muestra **volume** (popularidad) y **difficulty** (dificultad) para cada keyword
- Visualización mediante emojis: 🔥📊📉 para volume, 🔴🟡🟢 para difficulty
- Leyenda incluida en el mensaje para interpretación rápida

**Beneficios:**
- Identifica oportunidades de un vistazo (🔥🟢 o 📊🟢 = alto potencial)
- Contextualiza cada ranking con su volumen estimado
- Ayuda a priorizar keywords para optimización
- No requiere ejecutar el análisis PRO completo

**Archivos modificados:**
- `src/report_formatter.py` - Cálculo y display de métricas
- `BOT_TELEGRAM.md` - Documentación actualizada
- Nuevo: `FEATURE_VOLUME_DIFFICULTY.md` - Guía detallada

**Ejemplo visual:**
```
🏆 TOP 10
#3 ↑5 🔥🔴 · `bedtime bible stories`
#7 = 📊🟡 · `bible sleep`
#18 ↓2 📉🟢 · `peaceful bible sleep`
```

---

## 🎯 Cambios Anteriores

### 1. ✅ Validación de Periodos de Comparación (15/01/2026)

**Problema anterior:**
- Comparaba "today vs today" sin sentido real
- Mostraba "NEW" para todo incluso cuando había datos

**Solución:**
- El análisis ahora requiere **mínimo 7 días de diferencia** entre periodos
- Si no hay comparación válida, muestra: `❌ No comparison` o `⚠️ No 7d comparison`
- **NO muestra tendencias, movers o deltas** si no hay comparación válida
- Formato del periodo: `Last 7d vs Prev 7d` (o el número de días real)

**Código modificado:**
- `analyze_comprehensive()`: Validación de periodos
- Busca fecha al menos 7 días anterior
- Flag `has_valid_comparison` controla qué secciones mostrar

---

### 2. ✅ Focus Next 7d con Evidencia Completa

**Problema anterior:**
- Decía "Focus: keyword (Score 64)" sin explicar nada
- Parecía una decisión arbitraria

**Solución:**
El "Focus Next 7d" ahora incluye:
- ✅ Rank actual: `#47`
- ✅ Delta vs periodo anterior: `Δ +5` o `NEW`
- ✅ Volumen (proxy): `Vol: 500`
- ✅ Dificultad: `Diff: low/medium/high`
- ✅ Intent detectado: `Intent: audio/sleep/chat...`
- ✅ Desglose del Score: `Score 64/100 = I40+F10+R14−K0`
- ✅ Acción exacta: `Add "keyword" to subtitle prominently`
- ✅ Goal específico: `Goal: Top 30`
- ✅ Confidence: `HIGH/MEDIUM/LOW`

**Ejemplo en Telegram:**
```
🎯 *Focus next 7d*:
• `scripture bedtime stories` — #47 (Δ +3)
  Score 64/100 = I40+F10+R14−K0
  Vol: 500 | Diff: low | Intent: informational
  ✅ Action: Add "scripture bedtime stories" to keywords field
  🎯 Goal: Top 30
  Confidence: MEDIUM
```

---

### 3. ✅ Score Explicable con Desglose

**Problema anterior:**
- Score 64/100 sin saber de dónde sale

**Solución:**
Cada score ahora muestra:
```
Score 64/100 = I40+F10+R14−K0
```

**Definiciones:**
- **Impact (I: 0-40)**: Volumen de búsqueda / potencial de tráfico
- **Feasibility (F: 0-30)**: Facilidad de ranking (proximidad top10 + tendencia)
- **Relevance (R: 0-20)**: Match con las features de tu app
- **Risk (K: 0-10)**: Políticas sensibles (religion+kids) - RESTA puntos

**Fórmula:**
```python
total = Impact + Feasibility + Relevance - Risk
```

---

### 4. ✅ Watchlist con Triggers y Acciones

**Problema anterior:**
- Solo listaba keywords sin decir qué hacer ni cuándo

**Solución:**
Cada keyword en Watchlist ahora tiene:
- **Trigger de escalamiento**: `If Δ ≤ -5 → move to THREATS`
- **Trigger de acción**: `If rank ≤ 25 → push metadata + creatives`
- **Score visible**: Para entender prioridad

**Ejemplo:**
```
• `bible sleep` — #19 (Δ -2) — Score 59
  Trigger: If Δ ≤ -5 → move to THREATS
  Trigger: If rank ≤ 25 → push metadata + creatives
```

---

### 5. ✅ Estructura DO NOW / NEXT / WATCHLIST / THREATS / CLEANUP

**Problema anterior:**
- Demasiado listado de keywords
- Poca decisión accionable

**Solución:**
Nuevo formato estructurado:

1. **DO NOW (Max 3)**: Acciones para esta semana
   - Evidence completa: Vol, Diff, Intent
   - Action específica con texto exacto
   - Goal claro (Top 10/20/30)
   - Measure + timeframe (ej: "check rank in 7d")
   - Confidence level

2. **NEXT (Max 3)**: Queue para después
   - Action resumida
   - Trigger para escalar a DO NOW

3. **WATCHLIST (Max 5)**: Vigilancia con triggers
   - Triggers específicos de cuando actuar
   - Conditions de escalamiento

4. **THREATS (Max 3)**: Solo si hay comparación válida
   - Severity: CRITICAL/HIGH/MEDIUM/LOW
   - Likely causes
   - Response action

5. **CLEANUP (Max 5)**: Keywords ignorables
   - Reasons: "Rank >200", "Vol low", "Relevance low"

---

### 6. ✅ Cannibalization: Head vs Tail

**Problema anterior:**
- Decía "18 keywords promedio #114" pero algunas estaban en #16-#22
- Confundía qué keywords eran el problema

**Solución:**
Ahora separa claramente:

**Head (Top 1-3)**: Las mejores del cluster
```
Head: `bible sleep stories` #16, `bedtime bible stories` #21
```

**Tail (Resto)**: Las variantes débiles
```
Tail: 15 variants avg #133
```

**Status**: Diagnóstico automático
```
Status: Head strong / Tail weak
```

**Recommendation**:
```
Fix: Keep 3 head variants in metadata, prune 15 tail variants
```

---

### 7. ✅ Formato de Tareas (WHAT/WHY/HOW/MEASURE/CONF)

**Problema anterior:**
- Acciones genéricas sin estructura

**Solución:**
Cada acción importante incluye:

```
*1) scripture bedtime stories*
   #47 (Δ +3) — Score 64/100
   
   Evidence: Vol 500 | Diff low | Intent: informational
   
   ✅ Action: Add "scripture bedtime stories" to keywords field. 
      Create screenshot highlighting this feature
   
   🎯 Goal: Reach top 30
   
   📏 Measure: Rank + impressions in 14d
   
   Confidence: MEDIUM
```

**Estructura:**
- **WHAT**: La keyword y qué cambiar
- **WHY**: Evidence (rank/Δ/vol/diff/intent/score)
- **HOW**: Texto exacto o cambio exacto
- **MEASURE**: Qué métrica medir y en cuánto tiempo
- **CONFIDENCE**: Alto/Medio/Bajo

---

## 📋 Nuevo Formato Telegram

```
╔══════════════════════════════════════╗
║ 📈 ASO WEEKLY DECISION REPORT (US EN) ║
╚══════════════════════════════════════╝

🗓️ Period: Last 7d vs Prev 7d
📦 Keywords tracked: 82
🧾 Data quality: ✅ OK

────────────────────────────────────────

🏁 EXECUTIVE SUMMARY (3 bullets)

✅ Biggest win:
• {kw} — #{rank} (Δ {delta})
  Why: {reason}

⚠️ Biggest risk:
• {kw} — #{rank} (Δ {delta})
  Risk: {reason}

🎯 Focus next 7d:
• {kw} — #{rank} (Δ {delta})
  Score {score}/100 = I{impact}+F{feas}+R{rel}−K{risk}
  Vol: {vol} | Diff: {diff} | Intent: {intent}
  ✅ Action: {exact_action}
  🎯 Goal: {goal}
  Confidence: {High/Med/Low}

────────────────────────────────────────

🔥 DO NOW (Max 3) — This week actions

...

⏭️ NEXT (Max 3) — Queue for later

...

👀 WATCHLIST (Max 5) — Triggers

...

🧨 THREATS (Max 3)

...

🧩 CANNIBALIZATION (Clusters)

• Cluster: {name}
  Head: {kw1} #{r1}, {kw2} #{r2}
  Tail: {n} variants avg #{avg}
  Status: Head strong / Tail weak
  Fix: {recommendation}

────────────────────────────────────────

🧹 CLEANUP (Low impact)

• Ignore/prune: {kw} (reasons)

────────────────────────────────────────

🕒 Generated: {timestamp}
```

---

## 🎯 Reglas del Sistema (Checklist)

✅ **Si no hay comparación 7d vs prev 7d** → NO usar "NEW", "trend", "movers"

✅ **"Focus next 7d"** requiere: rank + Δ + vol + diff + acción + objetivo + confidence

✅ **Score** siempre con desglose (Impact/Feasibility/Relevance/Risk)

✅ **DO NOW** max 3 y deben traer "texto exacto" de cambio

✅ **Cannibalization** separa Head vs Tail

✅ **Cada acción** incluye Measure + timeframe (ej: "check rank in 7-14d")

---

## 📝 Archivos Modificados

1. **src/aso_expert_pro.py**
   - `analyze_comprehensive()`: Validación de periodos (min 7 días)
   - `_detect_cannibalization()`: Separación Head vs Tail
   - `format_telegram_report()`: Completamente reescrito con nuevo formato

2. **ASO_PRO.md**
   - Documentación actualizada (si aplica)

---

## 🚀 Cómo Usar

```bash
# Ejecutar análisis PRO
./run.sh pro

# Ejecutar monitor completo (tracking + análisis + Telegram)
./run.sh monitor
```

---

## 📊 Ejemplo Real de Output

Ver mensaje enviado a Telegram el 15/01/2026 13:15

**Highlights:**
- Data quality: ❌ No comparison (primera ejecución)
- Focus: scripture bedtime stories (Score 64/100)
- Cannibalization detectada: 2 clusters con Head/Tail
- CLEANUP: 5 keywords para ignorar (rank >200)

---

## 🔄 Próximos Pasos

1. **Esperar tracking de 7+ días** para ver comparaciones reales
2. **Ajustar volúmenes proxy** si tienes datos de API (actualmente estimados)
3. **Validar triggers** de Watchlist en producción
4. **Refinar buckets** de scoring según resultados reales

---

*Creado: 15 enero 2026*
*Versión: 2.0*
*Status: ✅ Production Ready*
