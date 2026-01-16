# 🔔 Smart Alerting - Guía Completa

## ¿Qué es Smart Alerting?

Sistema inteligente de alertas que **reduce el ruido** y te muestra **solo lo que importa**. En vez de recibir 15 alertas al día (la mayoría irrelevantes), recibirás 2-3 alertas críticas que realmente requieren tu atención.

---

## 🆕 Cambios vs Sistema Anterior

### **ANTES (Sistema Legacy)**
```
✅ Todas las caídas >5 posiciones → ALERTA
❌ No distingue entre keyword TOP y malo
❌ No detecta patrones
❌ Sin contexto ni acciones recomendadas
📧 15 alertas/día (spam)
```

### **AHORA (Smart Alerting)**
```
🎯 Solo alertas relevantes según contexto
✅ Prioriza keywords TOP automáticamente
✅ Detecta patrones (ej: múltiples drops)
✅ Añade insights y acciones recomendadas
📧 2-3 alertas críticas + 1 resumen diario
```

---

## 🎛️ Niveles de Prioridad

### **🚨 CRITICAL** (Envío inmediato)
- Keywords TOP (≤20) que caen ≥3 posiciones
- Keywords buenos (≤50) que caen ≥10 posiciones
- **Acción:** Requiere atención URGENTE

**Ejemplo:**
```
🚨 CRÍTICO

🚨 biblenow (US)
   #3 → #8 (-5)
   📊 Impacto: ~500 impresiones/día
   💡 Keyword TOP perdiendo visibilidad crítica
   ✅ 1. Revisa reviews últimas 24-48h
   ✅ 2. Verifica metadata sigue optimizada
   ✅ 3. Chequea competidores en esta keyword
```

---

### **⚠️ HIGH** (Envío inmediato)
- Keywords decentes (≤100) con caída ≥15 posiciones
- Subidas importantes (≥10 posiciones en top 100)
- **Acción:** Revisar pronto

---

### **📊 MEDIUM** (Resumen diario)
- Keywords mediocres (≤150) con cambios ≥15 posiciones
- **Acción:** Solo para monitorizar
- **No se envía inmediatamente**, va al resumen de las 20:00

---

### **🔇 LOW / IGNORE** (Ignorar)
- Keywords malos (>150) con fluctuaciones normales (<20)
- **Acción:** Ninguna, se ignora completamente

---

### **🎉 CELEBRATION** (Envío inmediato)
- Subidas excepcionales (≥20 posiciones y rank ≤50)
- Entrada al TOP 10
- **Acción:** ¡Capitalizar el momento!

**Ejemplo:**
```
🎉 CELEBREMOS

🎯 bible meditation (US)
   #25 → #8 (+17)
   📊 Impacto: ~700 impresiones/día
   💡 🎯 ENTRADA AL TOP 10
   ✅ 1. Asegúrate que keyword está en TITLE
   ✅ 2. Pide reviews mencionando este término
   ✅ 3. Considera aumentar presupuesto ASA si aplica
```

---

## 🧠 Detección de Patrones

El sistema detecta automáticamente:

### **1. Múltiples Drops (Crítico)**
Si ≥3 keywords TOP caen al mismo tiempo:
```
⚡️ PATRÓN CRÍTICO: 4 keywords TOP cayeron simultáneamente
🔍 Causas posibles:
  - Update de competidor principal
  - Cambio en algoritmo de App Store  
  - Reviews negativas afectando ASO
  
✅ Acciones:
  - Análisis urgente de competidores
  - Revisar reviews últimas 48h
  - Considerar update de emergencia
```

### **2. Momentum Positivo**
Si ≥5 keywords suben fuerte:
```
🚀 MOMENTO POSITIVO: 7 keywords subiendo fuerte
✅ Capitalizar: aumentar esfuerzos ASO
✅ Pedir reviews agresivamente
✅ Considerar aumentar budget ASA
```

---

## 📊 Resumen Diario

**Hora:** 20:00 (configurable en `config.yaml`)
**Contenido:** Cambios MEDIUM y LOW que no son urgentes

```
📊 RESUMEN DIARIO
📅 15/01/2026

📉 Cambios Medios (3)
⬇️ scripture notes: #105→#120
⬇️ kids bible study: #158→#165
⬆️ faith ai bible: #180→#170

ℹ️ Cambios menores: 2

_Enviado automáticamente por ASO Rank Guard_
```

---

## ⚙️ Configuración

En `config/config.yaml`:

```yaml
alerts:
  # SMART ALERTING
  smart_alerts:
    enabled: true  # Si false, usa sistema legacy
    pattern_detection: true  # Detectar patrones
    contextual_insights: true  # Añadir insights
  
  # Resumen diario
  daily_summary:
    enabled: true
    time: "20:00"  # Hora para enviar resumen
    min_changes: 3  # Mínimo de cambios para enviar
    include_priorities: ["MEDIUM", "LOW"]
```

---

## 🚀 Cómo Usar

### **1. Checks Manuales**
```bash
cd /Users/javi/aso-rank-guard
source venv/bin/activate
python src/rank_tracker.py
```
→ Envía alertas CRITICAL/HIGH inmediatamente vía Telegram

### **2. Scheduler Automático**
```bash
python src/scheduler.py
```
→ Ejecuta checks a las 18:00 + resumen a las 20:00

### **3. Ver Solo Resumen Diario**
```bash
python src/daily_summary.py
```

### **4. Test del Sistema**
```bash
python test_smart_alerts.py
```

---

## 📱 Ejemplos de Alertas Reales

### Alerta CRITICAL con Patrón
```
🔔 SMART ALERTS
📅 15/01/2026 18:05

⚡️ PATRONES DETECTADOS
⚠️ PATRÓN CRÍTICO: 3 keywords TOP cayeron simultáneamente
🔍 Causas: Update de competidor principal

🚨 CRÍTICO (acción inmediata)
🚨 biblenow (US)
   #3 → #8 (-5)
   📊 Impacto: ~500 impresiones/día
   💡 Keyword TOP perdiendo visibilidad crítica
   ✅ 1. Revisa reviews últimas 24-48h

🚨 bible sleep (US)
   #5 → #12 (-7)
   📊 Impacto: ~350 impresiones/día
   💡 ⚠️ SALIÓ DEL TOP 10
   ✅ 1. Revisa reviews últimas 24-48h

🚨 bible meditation (US)
   #8 → #15 (-7)
   📊 Impacto: ~350 impresiones/día
   💡 Keyword TOP perdiendo visibilidad crítica
   ✅ 1. Revisa reviews últimas 24-48h

_Total: 3 alertas_
```

---

## 🎯 Ventajas

### **Menos Ruido**
- ❌ Antes: 15 alertas/día (ignorabas todo)
- ✅ Ahora: 2-3 alertas críticas (actúas sobre ellas)

### **Más Contexto**
- Impact estimado en impresiones/día
- Insights sobre qué está pasando
- Acciones concretas a tomar

### **Detección Inteligente**
- Patrones de competidores
- Problemas sistémicos
- Oportunidades para capitalizar

### **Personalizable**
- Ajusta umbrales en `src/smart_alerts.py`
- Añade tus propias reglas
- Configura horarios

---

## 🔧 Personalización Avanzada

### Ajustar Umbrales en `src/smart_alerts.py`

```python
# Ejemplo: Hacer CRITICAL más restrictivo
{
    'name': 'top_keyword_critical_drop',
    'condition': lambda r, c, d: c <= 10 and d <= -5,  # Solo top 10
    'priority': AlertPriority.CRITICAL,
}
```

### Añadir Regla Custom

```python
# Nueva regla: Alerta si sales del top 50
{
    'name': 'exit_top_50',
    'condition': lambda r, c, d: r <= 50 and c > 50,
    'priority': AlertPriority.HIGH,
    'emoji': '📉',
    'telegram': True
}
```

---

## 📞 Soporte

- **Documentación:** Este archivo
- **Tests:** `python test_smart_alerts.py`
- **Logs:** `logs/rank_guard.log`

---

## ✅ Checklist de Implementación

- [x] Crear `src/smart_alerts.py`
- [x] Actualizar `config/config.yaml`
- [x] Modificar `src/auto_notifier.py`
- [x] Crear `src/daily_summary.py`
- [x] Actualizar `src/scheduler.py`
- [x] Tests completos pasados
- [ ] Ejecutar primer check con datos reales
- [ ] Verificar alertas en Telegram
- [ ] Ajustar si es necesario

---

**🎉 ¡Smart Alerting listo! Ahora solo verás las alertas que realmente importan.**
