# 🚀 QUICK WINS - Mejoras Rápidas (< 30 min cada una)

## Implementación Inmediata

### 1. Fix Dashboard `setTimeRange` Bug ✅

**Problema:** Consola muestra `setTimeRange is not defined`  
**Tiempo:** 5 minutos

```bash
# Los botones llaman setTimeRange() pero la función se llama updateTimeRange()
# Ya lo arreglamos, solo regenerar dashboard:
python3 src/dashboard_generator.py
scp web/dashboard-interactive.html root@194.164.160.111:/var/www/aso-rank-guard/
```

---

### 2. Health Check + Monitoring 🏥

**Beneficio:** Saber si el server está caído  
**Tiempo:** 15 minutos

```bash
# 1. Endpoint ya creado con fix_critical.sh
curl http://194.164.160.111:8447/api/health

# 2. Configurar UptimeRobot (gratis)
# - Ir a: https://uptimerobot.com
# - Añadir monitor: http://194.164.160.111:8447/api/health
# - Intervalo: 5 minutos
# - Alertas: Email + Telegram
```

---

### 3. Favicon + Dark Mode 🎨

**Beneficio:** UI más profesional  
**Tiempo:** 10 minutos

Favicon ya creado con `fix_critical.sh`.

Para dark mode, añadir al dashboard:

```javascript
// En dashboard_generator.py, añadir botón en header
<button onclick="toggleDarkMode()" class="theme-toggle">
    <i data-lucide="moon" id="theme-icon"></i>
</button>

// Función JavaScript
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    document.getElementById('theme-icon').setAttribute('data-lucide', isDark ? 'sun' : 'moon');
    lucide.createIcons();
}

// Restaurar al cargar
window.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('theme-icon').setAttribute('data-lucide', 'sun');
    }
});
```

---

### 4. Log Rotation 📝

**Problema:** Logs crecen infinitamente  
**Tiempo:** 5 minutos

```bash
# Crear archivo de rotación
sudo tee /etc/logrotate.d/aso-rank-guard << EOF
/Users/javi/aso-rank-guard/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

# Test
sudo logrotate -f /etc/logrotate.d/aso-rank-guard
```

---

### 5. Cleanup Command 🧹

**Beneficio:** Mantenimiento fácil  
**Tiempo:** 10 minutos

Añadir a `run.sh`:

```bash
cleanup)
    echo "🧹 Limpiando proyecto..."
    
    # Eliminar duplicados en config
    python3 -c "
import yaml
with open('config/config.yaml') as f:
    cfg = yaml.safe_load(f)
before = len(cfg['keywords'])
cfg['keywords'] = sorted(list(set(cfg['keywords'])))
with open('config/config.yaml', 'w') as f:
    yaml.dump(cfg, f, sort_keys=False)
print(f'✅ Keywords: {before} → {len(cfg[\"keywords\"])}')
    "
    
    # Limpiar logs antiguos
    find logs/ -name "*.log" -mtime +30 -delete
    echo "✅ Logs antiguos eliminados"
    
    # Limpiar backups
    find data/backups/ -name "*.csv" -mtime +90 -delete
    echo "✅ Backups antiguos eliminados"
    
    echo "🎉 Limpieza completada"
    ;;
```

Uso: `./run.sh cleanup`

---

### 6. Comando de Estado Mejorado 📊

**Tiempo:** 15 minutos

Reemplazar `status` en `run.sh`:

```bash
status)
    echo "📊 ASO Rank Guard - Estado del Sistema"
    echo "========================================"
    echo ""
    
    # Keywords trackeadas
    KEYWORDS=$(python3 -c "import yaml; c=yaml.safe_load(open('config/config.yaml')); print(len(c['keywords']))")
    echo "📌 Keywords trackeadas: $KEYWORDS"
    
    # Último check
    LAST_CHECK=$(python3 -c "import pandas as pd; df=pd.read_csv('data/ranks.csv'); print(df['date'].max())")
    echo "⏰ Último check: $LAST_CHECK"
    
    # Total registros
    RECORDS=$(wc -l < data/ranks.csv)
    echo "📈 Total registros: $RECORDS"
    
    # Tamaño de datos
    SIZE=$(du -sh data/ | cut -f1)
    echo "💾 Tamaño datos: $SIZE"
    
    # Uptime del servidor (si está en server)
    if command -v uptime &> /dev/null; then
        echo "⏱️  Server uptime: $(uptime -p 2>/dev/null || uptime)"
    fi
    
    # Espacio en disco
    echo "💿 Espacio libre: $(df -h . | tail -1 | awk '{print $4}')"
    
    # Health check (si API está corriendo)
    if curl -s http://localhost:5000/health &>/dev/null; then
        echo "✅ API: Running"
    else
        echo "❌ API: Stopped"
    fi
    
    echo ""
    echo "📋 Últimas 5 keywords trackeadas:"
    tail -6 data/ranks.csv | head -5 | cut -d',' -f2,4 | sed 's/,/ → Rank #/'
    ;;
```

---

### 7. Validación en add_keywords.py 🔍

**Problema:** Permite keywords inválidas  
**Tiempo:** 10 minutos

```python
# Reemplazar en add_keywords.py
def add_keywords(new_keywords):
    """Añadir keywords al config.yaml con validación"""
    # ... código existente ...
    
    # AÑADIR VALIDACIÓN
    for kw in new_keywords_clean:
        # Validar longitud
        if not kw or len(kw) < 3:
            print(f"⚠️ Keyword muy corta: '{kw}' (mínimo 3 caracteres)")
            continue
        if len(kw) > 100:
            print(f"⚠️ Keyword muy larga: '{kw}' (máximo 100 caracteres)")
            continue
            
        # Validar caracteres especiales
        if any(c in kw for c in ['<', '>', '|', '&', ';']):
            print(f"⚠️ Keyword con caracteres inválidos: '{kw}'")
            continue
        
        # Todo OK
        if kw not in current_keywords:
            current_keywords.add(kw)
            added.append(kw)
    
    # ... resto del código ...
```

---

### 8. Exportar Rankings a Excel 📑

**Beneficio:** Análisis en Excel  
**Tiempo:** 20 minutos

Crear `export_excel.py`:

```python
#!/usr/bin/env python3
"""Exportar rankings a Excel con formato"""

import pandas as pd
from datetime import datetime

# Leer datos
df = pd.read_csv('data/ranks.csv')
df['date'] = pd.to_datetime(df['date'])

# Crear pivot table
pivot = df.pivot_table(
    index='keyword',
    columns='date',
    values='rank',
    aggfunc='first'
)

# Guardar a Excel con formato
filename = f"rankings_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    # Sheet 1: Rankings
    pivot.to_excel(writer, sheet_name='Rankings')
    
    # Sheet 2: Datos crudos
    df.to_excel(writer, sheet_name='Raw Data', index=False)
    
    # Sheet 3: Estadísticas
    stats = df.groupby('keyword').agg({
        'rank': ['min', 'max', 'mean', 'last']
    }).round(1)
    stats.to_excel(writer, sheet_name='Stats')

print(f"✅ Exportado: {filename}")
```

Uso:
```bash
python3 export_excel.py
# Genera: rankings_export_20260116.xlsx
```

Añadir a `run.sh`:
```bash
export)
    python3 export_excel.py
    ;;
```

---

### 9. Webhook para Slack (Opcional) 💬

**Si trabajas en equipo**  
**Tiempo:** 15 minutos

```python
# Crear src/slack_alerts.py
import requests
import json

def send_slack_alert(message: str, webhook_url: str):
    """Enviar alerta a Slack"""
    payload = {
        "text": message,
        "username": "ASO Rank Guard",
        "icon_emoji": ":chart_with_upwards_trend:"
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.ok

# Uso en telegram_alerts.py
if config.get('alerts', {}).get('slack', {}).get('enabled'):
    webhook = config['alerts']['slack']['webhook_url']
    send_slack_alert(alert_text, webhook)
```

Config:
```yaml
alerts:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

### 10. Test Suite Básico 🧪

**Fundamental para calidad**  
**Tiempo:** 30 minutos

```bash
# Instalar pytest
pip install pytest pytest-cov

# Crear tests/test_rank_tracker.py
mkdir -p tests
cat > tests/test_rank_tracker.py << 'EOF'
import pytest
from src.rank_tracker import RankTracker

def test_tracker_init():
    """Test inicialización del tracker"""
    tracker = RankTracker()
    assert tracker.app_id == 6749528117
    assert len(tracker.keywords) > 0
    assert len(tracker.countries) > 0

def test_get_rank_for_keyword():
    """Test búsqueda de ranking"""
    tracker = RankTracker()
    rank = tracker.get_rank_for_keyword('biblenow', 'US')
    assert rank is None or (1 <= rank <= 250)

def test_load_history():
    """Test carga de histórico"""
    tracker = RankTracker()
    assert tracker.history_df is not None
    assert 'date' in tracker.history_df.columns
EOF

# Ejecutar tests
pytest tests/ -v --cov=src
```

---

## 📋 Checklist de Implementación

Ejecuta en orden:

```bash
# 1. Fixes críticos (ya hecho)
./fix_critical.sh

# 2. Quick wins
# ✅ Health check → Ya incluido en fix_critical.sh
# ✅ Favicon → Ya incluido
# ✅ Log rotation → Ejecutar comandos de arriba
# ✅ Cleanup command → Añadir a run.sh
# ✅ Status mejorado → Reemplazar en run.sh
# ✅ Validación keywords → Actualizar add_keywords.py
# ✅ Export Excel → Crear export_excel.py
# ⏸️ Dark mode → Opcional, implementar si quieres
# ⏸️ Slack → Solo si trabajas en equipo
# ✅ Tests → Ejecutar setup de pytest

# 3. Verificar
./run.sh status
python3 -m pytest tests/ -v

# 4. Commit
git add .
git commit -m "Quick wins: health check, cleanup, validation, tests"
```

---

## 🎯 Impacto de Quick Wins

| Feature | Tiempo | Impacto | Prioridad |
|---------|--------|---------|-----------|
| Health check | 15 min | 🔥🔥🔥 | ALTA |
| Log rotation | 5 min | 🔥🔥🔥 | ALTA |
| Cleanup command | 10 min | 🔥🔥 | MEDIA |
| Status mejorado | 15 min | 🔥🔥 | MEDIA |
| Validación keywords | 10 min | 🔥 | BAJA |
| Export Excel | 20 min | 🔥🔥 | MEDIA |
| Dark mode | 10 min | 🔥 | BAJA |
| Tests básicos | 30 min | 🔥🔥🔥 | ALTA |
| **TOTAL** | **115 min** | - | - |

**En ~2 horas tienes 8 mejoras implementadas** ✅

---

## ✅ Próximo Paso

```bash
# Ejecutar esto AHORA
./fix_critical.sh

# Luego implementa quick wins uno por uno
# Empieza por los de prioridad ALTA
```

¡Éxito! 🚀
