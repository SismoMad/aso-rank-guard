# 📊 Feature: Volume y Difficulty en /track

## ✨ Nueva Funcionalidad

Ahora el comando `/track` muestra **información adicional** para cada keyword:
- **📊 Volume (Popularidad)**: Estimación del volumen de búsquedas
- **🔴 Difficulty (Dificultad)**: Nivel de competencia estimada

## 🎯 Formato Visual

### Ejemplo de salida:
```
🏆 TOP 10
#5 ↑2 🔥🔴 · `biblenow`
#8 = 📊🟡 · `bedtime bible stories`
#10 ↓1 📉🟢 · `peaceful bible sleep`
```

### Leyenda:

**Volume (Popularidad):**
- 🔥 **Alto** (400+ búsquedas estimadas)
- 📊 **Medio** (100-399 búsquedas)
- 📉 **Bajo** (<100 búsquedas)

**Difficulty (Dificultad):**
- 🔴 **High** - Muy competitivo
- 🟡 **Medium** - Competencia moderada
- 🟢 **Low** - Baja competencia

## 📐 Cálculo de Métricas

### Volume Estimation
Se calcula según el tipo de keyword:

| Tipo | Volume | Ejemplo |
|------|--------|---------|
| Brand | 500 | `biblenow` |
| Generic 2 palabras | 300 | `bible chat` |
| Generic 3 palabras | 150 | `audio bible stories` |
| Long tail (4 palabras) | 50 | `kids calming audio bible` |
| Very long (5+ palabras) | 20 | `peaceful bible sleep stories for kids` |

**Boost adicional:** Keywords con términos populares (`bible`, `audio`, `chat`, `stories`, `sleep`, `kids`) obtienen volume de categoría "generic_3w" (150).

### Difficulty Calculation
Basado en una heurística de **rank actual + volume**:

| Rank | Volume | Difficulty |
|------|--------|-----------|
| <20 | >200 | 🔴 High |
| <50 | >100 | 🟡 Medium |
| >150 | any | 🔴 High (muy competido) |
| Otros | - | 🟢 Low |

## 💡 Uso Estratégico

### Keywords 🔥🟢 (Alto Volume + Baja Dificultad)
- **Oportunidad de oro** ⭐
- Priorizar optimización
- Potencial de crecimiento rápido

### Keywords 📊🟡 (Medio Volume + Media Dificultad)
- **Trabajo constante**
- Monitorización regular
- Optimización gradual

### Keywords 🔥🔴 (Alto Volume + Alta Dificultad)
- **Mantener posición**
- Vigilar competencia
- No descuidar

### Keywords 📉🟢 (Bajo Volume + Baja Dificultad)
- **Nicho específico**
- Evaluar relevancia
- Considerar eliminar si rank bajo

## 🔧 Implementación Técnica

Los cambios se han realizado en:
- **`src/report_formatter.py`**
  - Nuevo método `_estimate_volume()`
  - Nuevo método `_calculate_difficulty()`
  - Métodos de formateo `_format_volume()` y `_format_difficulty()`
  - Actualización de `_calculate_changes()` para incluir métricas
  - Modificación de `_build_top_keywords()` para mostrar emojis

## 📱 Ejemplo Completo

```
✅ Tracking completado

📊 Total: 83 keywords
👁️ Visibles: 65

_Leyenda: 🔥📊📉=vol · 🔴🟡🟢=diff_

🏆 TOP 10
#1 NEW 🔥🔴 · `biblenow`
#3 ↑5 🔥🔴 · `bedtime bible stories`
#7 = 📊🟡 · `bible sleep`
#9 ↓2 📊🟡 · `bible sleep stories`

🥈 TOP 11-30
#12 ↑3 📊🟡 · `audio bible stories`
#18 = 📉🟢 · `peaceful bible sleep`
#25 ↓4 📊🟡 · `bible chat app`

📈 TOP 31-100
#45 NEW 📉🟢 · `calming prayer audio`
#67 ↑12 📉🟢 · `relaxing bible kids`

🚀 Mayores subidas
#67 ↑12 · `relaxing bible kids`
#12 ↑3 · `audio bible stories`

🕒 14:30
```

## 🎉 Beneficios

1. **Priorización visual inmediata** - Identifica oportunidades de un vistazo
2. **Contexto estratégico** - Entiendes el "por qué" detrás de cada rank
3. **Decisiones informadas** - Sabes dónde invertir esfuerzo
4. **Tracking completo** - No solo posiciones, sino potencial real

---

_Actualizado: 15 enero 2026_
