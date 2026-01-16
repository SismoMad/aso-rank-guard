# 🤖 Guía de Automatización - Tracking Diario

Tienes **3 opciones** para automatizar el tracking diario con las nuevas métricas de volume/difficulty.

---

## 🎯 Opción 1: Scheduler Integrado (RECOMENDADO)

El sistema ya incluye un scheduler que ejecuta el tracking automáticamente.

### ✅ Ventajas
- Ya está configurado y listo
- Fácil de iniciar/detener
- Logs automáticos
- Se mantiene corriendo en background

### 📝 Uso

#### Configurar la hora (ya está en 09:00)
Edita `config/config.yaml`:
```yaml
schedule:
  daily_check_time: "09:00"  # Cambiar a la hora deseada (formato 24h)
```

#### Iniciar el scheduler
```bash
cd /Users/javi/aso-rank-guard
./run.sh schedule
```

Verás:
```
🛡️  ASO Rank Guard - Scheduler iniciado
📅 Check diario programado a las 09:00
⏳ Esperando próxima ejecución...
   (Presiona Ctrl+C para detener)
```

#### Mantener corriendo en background
```bash
nohup ./run.sh schedule > logs/scheduler_output.log 2>&1 &
```

Para ver si está corriendo:
```bash
ps aux | grep scheduler.py
```

Para detenerlo:
```bash
pkill -f scheduler.py
```

#### Ver logs
```bash
tail -f logs/scheduler.log
```

---

## 🍎 Opción 2: Launchd (macOS) - Automático al Iniciar

Para que se ejecute automáticamente incluso después de reiniciar el Mac.

### Crear el archivo plist

```bash
cat > ~/Library/LaunchAgents/com.biblenow.rankguard.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.biblenow.rankguard</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/javi/aso-rank-guard/venv/bin/python3</string>
        <string>/Users/javi/aso-rank-guard/src/rank_tracker.py</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/Users/javi/aso-rank-guard/logs/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/javi/aso-rank-guard/logs/launchd_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/javi/aso-rank-guard</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF
```

### Activar
```bash
launchctl load ~/Library/LaunchAgents/com.biblenow.rankguard.plist
```

### Ver estado
```bash
launchctl list | grep rankguard
```

### Desactivar
```bash
launchctl unload ~/Library/LaunchAgents/com.biblenow.rankguard.plist
```

---

## ⏰ Opción 3: Cron (Tradicional)

Para usar cron en macOS/Linux.

### Editar crontab
```bash
crontab -e
```

### Añadir esta línea
```cron
# ASO Rank Guard - Tracking diario a las 9:00 AM
0 9 * * * cd /Users/javi/aso-rank-guard && source venv/bin/activate && python3 src/rank_tracker.py >> logs/cron.log 2>&1
```

Formato: `minuto hora dia mes dia_semana comando`

Ejemplos:
- `0 9 * * *` - Todos los días a las 9:00 AM
- `0 14 * * *` - Todos los días a las 2:00 PM
- `0 9,14,18 * * *` - 3 veces al día (9 AM, 2 PM, 6 PM)
- `0 9 * * 1-5` - Solo lunes a viernes a las 9 AM

### Ver crontab actual
```bash
crontab -l
```

### Eliminar crontab
```bash
crontab -r
```

---

## 🚀 Mi Recomendación

### Para desarrollo/testing:
**Opción 1 (Scheduler)** - Fácil de iniciar/detener

```bash
# Iniciar en background
nohup ./run.sh schedule > logs/scheduler_output.log 2>&1 &

# Ver si está corriendo
ps aux | grep scheduler
```

### Para producción permanente:
**Opción 2 (Launchd)** - Se mantiene corriendo siempre, incluso tras reiniciar el Mac

---

## 📊 Verificar que Funciona

### Ver últimos resultados
```bash
./run.sh status
```

### Ver logs
```bash
# Scheduler
tail -f logs/scheduler.log

# Launchd
tail -f logs/launchd.log

# Cron
tail -f logs/cron.log

# Tracking general
tail -f logs/rank_guard.log
```

### Probar manualmente
```bash
./run.sh track
```

---

## 🔔 Notificaciones Automáticas

Con cualquier opción, las alertas se envían automáticamente a Telegram cuando:
- Una keyword sale del Top 250
- Una keyword entra/sale del Top 10
- Una keyword sube/baja >10 posiciones

No necesitas hacer nada extra, ya está configurado en `src/rank_tracker.py`.

---

## ⚡ Quick Start

**La forma más rápida:**

```bash
cd /Users/javi/aso-rank-guard

# Iniciar scheduler en background
nohup ./run.sh schedule > logs/scheduler_output.log 2>&1 &

# Verificar que está corriendo
ps aux | grep scheduler.py

# Ver próxima ejecución
tail logs/scheduler.log
```

**Para detener:**
```bash
pkill -f scheduler.py
```

---

## 🎉 Resultado Esperado

Una vez configurado, cada día a las 9:00 AM recibirás automáticamente en Telegram:

```
📊 Tracking completado

📊 Total: 83 keywords
👁️ Visibles: 77

_Leyenda: 🔥📊📉=vol · 🔴🟡🟢=diff_

🏆 TOP 10
#2 ↑1 🔥🔴 · `biblenow`

🥈 TOP 11-30
#16 = 📊🟡 · `bible sleep stories`
#19 ↑3 📊🟡 · `bible sleep`

🔔 ALERTAS (si las hay):
❌ FUERA DE RANKING
• keyword X ya no está en el ranking

🚀 Mayores subidas
...
```

Sin hacer absolutamente nada. ✨

---

_Última actualización: 15 enero 2026_
