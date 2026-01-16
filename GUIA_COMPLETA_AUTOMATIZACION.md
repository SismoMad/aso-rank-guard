# 🚀 Guía Completa: Dashboard + Alertas Automatizadas

## 📋 Resumen

Tu sistema ASO ahora tiene:
1. ✅ **Dashboard interactivo** con análisis PRO
2. ✅ **Alertas Telegram** inteligentes (ya configuradas)
3. ✅ **Automatización diaria** con `update_dashboard.sh`
4. ✅ **Configuración de alertas desde el dashboard** (preparado para SaaS)

---

## 🔄 Automatización Diaria del Dashboard

### Paso 1: Configurar Cron (RECOMENDADO)

```bash
# Abrir crontab
crontab -e

# Añadir esta línea (ejecuta todos los días a las 17:00)
0 17 * * * cd /Users/javi/aso-rank-guard && ./update_dashboard.sh >> logs/dashboard_update.log 2>&1
```

**Horarios útiles:**
```bash
0 17 * * *     # Una vez al día a las 17:00
0 9,17 * * *   # Dos veces al día (9:00 y 17:00)
0 */6 * * *    # Cada 6 horas
30 16 * * *    # Todos los días a las 16:30
```

### Paso 2: Verificar que funciona

```bash
# Ejecutar manualmente para probar
./update_dashboard.sh

# Ver logs
tail -f logs/dashboard_update.log
```

### ¿Qué hace el script automáticamente?

1. 📊 **Rastrea rankings** (ejecuta `rank_tracker.py`)
2. 🔍 **Analiza competidores y descubrimientos** (ejecuta `aso_expert_pro.py`)
3. 🎨 **Genera dashboard HTML** con todos los datos frescos
4. 📤 **Lo sube al servidor** (http://194.164.160.111/)

**Resultado:** Dashboard siempre actualizado con datos del día 🎯

---

## 📱 Configuración de Alertas desde el Dashboard

### Nueva Pestaña "Alertas" en el Dashboard

Ahora tienes una pestaña **"Alertas"** donde puedes:

1. **Ingresar tus credenciales de Telegram:**
   - Bot Token (desde @BotFather)
   - Chat ID (desde @userinfobot)

2. **Copiar configuración automáticamente:**
   - Genera el YAML correcto
   - Lo copia al portapapeles
   - Solo pegas en `config/config.yaml`

3. **Ver tipos de alertas:**
   - CRITICAL (inmediato)
   - HIGH (importante)
   - MEDIUM (resumen diario)
   - CELEBRATION (siempre)

### Flujo para usuarios finales (futuro SaaS):

```
Usuario → Dashboard → Pestaña Alertas → Introduce datos → Guarda
                                                              ↓
                                                    Backend API (futuro)
                                                              ↓
                                                    Actualiza config.yaml
                                                              ↓
                                                    Reinicia scheduler
```

**Por ahora:** Usuario copia el YAML y lo pega manualmente (perfecto para uso personal).

**Futuro:** Botón "Guardar" que llama a una API y activa las alertas automáticamente.

---

## 🎯 Flujo Completo de Uso

### Configuración Inicial (una sola vez):

```bash
# 1. Configurar alertas Telegram (ya está hecho)
# config/config.yaml tiene bot_token y chat_id

# 2. Automatizar dashboard
crontab -e
# Añadir línea: 0 17 * * * cd /Users/javi/aso-rank-guard && ./update_dashboard.sh >> logs/dashboard_update.log 2>&1

# 3. Automatizar alertas (ya está con scheduler.py)
# Ya lo tienes corriendo, envía alertas cuando detecta cambios
```

### Operación Diaria (TODO AUTOMÁTICO):

**17:00 - Dashboard se actualiza:**
```
Cron ejecuta update_dashboard.sh
  → Rastrea rankings
  → Analiza competidores
  → Genera HTML
  → Sube al servidor
```

**16:00 - Alertas Telegram (según config):**
```
Scheduler ejecuta rank_tracker.py
  → Detecta cambios en rankings
  → Smart alerts evalúa prioridad
  → Envía alertas críticas inmediatamente
  → Acumula cambios menores para resumen
```

**18:00 - Resumen diario:**
```
Daily summary envía a Telegram:
  → Cambios MEDIUM/LOW del día
  → Métricas generales
  → Tendencias
```

### Resultado:

🎯 **Dashboard:** Siempre actualizado en http://194.164.160.111/  
📱 **Telegram:** Alertas en tiempo real cuando algo importante pasa  
🤖 **Tú:** Solo revisas cuando te avisan o cuando quieres ver análisis profundo

---

## 🛠️ Personalización

### Cambiar horarios:

```bash
# Editar crontab
crontab -e

# Opciones:
0 8 * * *      # Actualizar a las 8:00 AM
0 20 * * *     # Actualizar a las 8:00 PM
0 */4 * * *    # Cada 4 horas
```

### Desactivar auto-despliegue al servidor:

Edita `update_dashboard.sh` y comenta estas líneas:

```bash
# echo "📤 Desplegando en servidor..."
# scp -o StrictHostKeyChecking=no web/dashboard-interactive.html root@194.164.160.111:/var/www/aso-rank-guard/index.html
# ssh -o StrictHostKeyChecking=no root@194.164.160.111 'chmod 644 /var/www/aso-rank-guard/index.html && restorecon -v /var/www/aso-rank-guard/index.html'
```

Así solo genera el HTML local (`web/dashboard-interactive.html`) sin subirlo.

### Ajustar prioridades de alertas:

Edita `config/config.yaml`:

```yaml
alerts:
  smart_alerts:
    enabled: true
    pattern_detection: true  # Detectar patrones automáticamente
    contextual_insights: true  # Añadir recomendaciones
  
  daily_summary:
    enabled: true
    time: "18:00"  # Cambiar hora del resumen
    min_changes: 3  # Mínimo de cambios para enviar
```

---

## 📊 Acceso al Dashboard

- **URL:** http://194.164.160.111/
- **Usuario:** (configurado en nginx)
- **Actualización:** Automática cada día a las 17:00
- **Offline:** Abre `web/dashboard-interactive.html` localmente

---

## 🔍 Troubleshooting

### Dashboard no se actualiza:

```bash
# Ver logs del cron
tail -f logs/dashboard_update.log

# Ejecutar manualmente
./update_dashboard.sh

# Verificar que cron está activo
crontab -l
```

### Alertas no llegan a Telegram:

```bash
# Verificar config
cat config/config.yaml | grep -A 5 telegram

# Probar envío manual
python3 send_test_alert.py

# Ver logs del scheduler
tail -f logs/rank_guard.log
```

### Dashboard muestra datos viejos:

```bash
# Generar dashboard manualmente
python3 -c "
from src.dashboard_generator import InteractiveDashboard
import yaml
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)
dash = InteractiveDashboard(config)
html = dash.generate_html()
with open('web/dashboard-interactive.html', 'w', encoding='utf-8') as f:
    f.write(html)
"

# Subir al servidor
scp web/dashboard-interactive.html root@194.164.160.111:/var/www/aso-rank-guard/index.html
```

---

## 🚀 Próximos Pasos (Escalabilidad SaaS)

Si decides ofrecer esto como producto:

### Backend necesario:

```python
# API para guardar configuración desde dashboard
@app.post('/api/alerts/config')
def save_alerts_config(token: str, chat_id: str, user_id: str):
    # Validar token de Telegram
    # Guardar en base de datos
    # Actualizar config.yaml del usuario
    # Reiniciar scheduler si está activo
    return {"status": "ok"}
```

### Multi-tenant:

```
users/
├─ user_1/
│  ├─ config/config.yaml
│  ├─ data/ranks.csv
│  └─ web/dashboard.html
├─ user_2/
│  ├─ config/config.yaml
│  ├─ data/ranks.csv
│  └─ web/dashboard.html
```

### Autenticación:

- Login con email/password
- Cada usuario ve solo su dashboard
- Alertas van a su Telegram

**El dashboard ya está preparado para esto:** solo necesitas backend que procese el formulario de alertas.

---

## ✅ Checklist de Configuración Completa

- [x] `config/config.yaml` con bot_token y chat_id
- [x] `scheduler.py` corriendo (alertas automáticas)
- [ ] Cron configurado para `update_dashboard.sh`
- [ ] Verificar logs: `tail -f logs/dashboard_update.log`
- [x] Dashboard accesible en http://194.164.160.111/
- [x] Pestaña "Alertas" visible en dashboard

**Cuando completes todo:** 100% automatizado, solo revisas cuando Telegram te avisa 🎯
