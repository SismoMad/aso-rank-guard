# 🤖 Automatización del Dashboard

## Opción 1: Cron (macOS/Linux) - RECOMENDADO

Añade esto a tu crontab para ejecutar diariamente a las 17:00:

```bash
# Editar crontab
crontab -e

# Añadir esta línea (cambia la hora si quieres)
0 17 * * * cd /Users/javi/aso-rank-guard && ./update_dashboard.sh >> logs/dashboard_update.log 2>&1
```

**Horarios útiles:**
```
0 17 * * *    # Todos los días a las 17:00
0 9,17 * * *  # Dos veces al día (9:00 y 17:00)
0 */6 * * *   # Cada 6 horas
```

## Opción 2: Launchd (macOS nativo)

Crea: `~/Library/LaunchAgents/com.biblenow.dashboard.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.biblenow.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/javi/aso-rank-guard/update_dashboard.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>17</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/javi/aso-rank-guard/logs/dashboard_update.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/javi/aso-rank-guard/logs/dashboard_update_error.log</string>
</dict>
</plist>
```

**Activar:**
```bash
launchctl load ~/Library/LaunchAgents/com.biblenow.dashboard.plist
launchctl start com.biblenow.dashboard
```

## Opción 3: Manual cuando quieras

```bash
./update_dashboard.sh
```

## Verificar logs

```bash
tail -f logs/dashboard_update.log
```

## Desactivar auto-despliegue

Si solo quieres generar local sin subir al servidor, edita `update_dashboard.sh` y comenta las líneas de scp/ssh:

```bash
# echo "📤 Desplegando en servidor..."
# scp ...
# ssh ...
```
