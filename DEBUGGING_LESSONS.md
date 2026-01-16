# 🔥 Lecciones Críticas de Debugging

## 1. Z-INDEX Y POSITION ABSOLUTE - NO ASUMIR NUNCA

**Fecha:** 16 Enero 2026  
**Tiempo perdido:** ~2 horas  
**Problema:** Botones con `position: absolute` invisibles a pesar de estar en el HTML

### ❌ ERROR FATAL:
```css
.theme-toggle {
    position: absolute;  /* SIN z-index */
    top: 20px;
    right: 20px;
}
```

### ✅ SOLUCIÓN OBLIGATORIA:
```css
/* CONTENEDOR PADRE */
<div style="z-index: 10000;">

/* ELEMENTO */
.theme-toggle {
    z-index: 9999 !important;
    background: #007AFF !important;  /* inline con !important */
}
```

### 🎯 REGLAS INQUEBRANTABLES:

1. **SIEMPRE** z-index alto en elementos `position: absolute`
2. **SIEMPRE** z-index en el contenedor padre también
3. **SIEMPRE** usar `!important` en propiedades críticas de visibilidad
4. **SIEMPRE** inline styles con `!important` para máxima especificidad
5. **NO ASUMIR** que "si está en el HTML, se va a ver"

### 🔍 Debugging checklist para elementos invisibles:

```javascript
// En DevTools Console:
console.log(document.getElementById('elemento'))  // ¿Existe?
console.log(window.getComputedStyle(elemento).zIndex)  // ¿z-index?
console.log(window.getComputedStyle(elemento).display)  // ¿display?
console.log(window.getComputedStyle(elemento).visibility)  // ¿visibility?
```

### ⏱️ Tiempo que debió tomar: 5 minutos
### ⏱️ Tiempo que tomó: 2+ horas

**NUNCA MÁS.**

---

## 2. CACHE DE NAVEGADOR - SIEMPRE VERIFICAR PRIMERO

**Problema:** Cambios no aparecían tras deploy

### Checklist inmediato:
1. ✅ Ctrl+Shift+R (hard refresh)
2. ✅ DevTools → Network → Disable cache
3. ✅ Modo incógnito
4. ✅ View Source (Ctrl+U) para ver HTML real
5. ✅ Verificar en servidor: `grep -n "texto" archivo.html`

### No gastar tiempo en:
- ❌ Múltiples redeploys sin verificar cache primero
- ❌ Cambiar código antes de confirmar que el nuevo código llegó al navegador
- ❌ Asumir que no-cache headers funcionan siempre

---

## 3. CSS STACKING CONTEXT

**Concepto clave:** `z-index` solo funciona dentro del mismo stacking context

### Crear nuevo stacking context:
- `position: relative/absolute/fixed` + `z-index`
- `opacity` < 1
- `transform`
- `filter`

**Si hijo tiene z-index 999 pero padre z-index 1 → hijo NUNCA estará por encima de elementos con z-index 2**

---

## 🚨 PROTOCOLO DE EMERGENCIA

Cuando algo "no aparece" en el HTML:

1. **Verificar PRIMERO en servidor** (`grep`, `cat`)
2. **Verificar cache** (View Source)
3. **DevTools Console** → buscar el elemento
4. **Computed styles** → ver qué CSS se está aplicando realmente
5. **NO cambiar código** hasta confirmar pasos 1-4

**Tiempo máximo para diagnóstico:** 10 minutos  
**Si pasa de 10 minutos:** Hacer debugging sistemático, no "probar cosas"

---

_Este documento debe actualizarse con cada bug que tome >30 minutos resolver._
