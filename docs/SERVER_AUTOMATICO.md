# 🖥️ Automatización en Servidor (100% Autónoma)

## ✅ Ventajas de Correr en Servidor

- 🔋 **24/7** - No depende de tu Mac encendido
- 🚀 **Más rápido** - El servidor ya tiene los datos
- 💰 **Gratis** - Ya tienes el servidor pagado
- 🔧 **Centralizado** - Todo en un solo lugar

---

## 🚀 Setup Inicial (UNA SOLA VEZ)

Ejecuta este comando desde tu Mac:

```bash
./server_setup.sh
```

**Esto configurará automáticamente:**

1. ✅ Sube todo el código al servidor (`/root/aso-rank-guard/`)
2. ✅ Instala dependencias Python
3. ✅ Crea script `update_dashboard.sh` en servidor
4. ✅ Configura cron para ejecutar automáticamente:
   - **16:00** → Alertas Telegram (`scheduler.py`)
   - **17:00** → Dashboard (`update_dashboard.sh`)

---

## 📋 Verificar que Está Funcionando

### 1. Ver tareas programadas:

```bash
ssh root@194.164.160.111 'crontab -l'
```

Deberías ver:
```
0 17 * * * /root/aso-rank-guard/update_dashboard.sh >> /root/aso-rank-guard/logs/cron.log 2>&1
0 16 * * * cd /root/aso-rank-guard && python3 src/scheduler.py >> /root/aso-rank-guard/logs/alerts.log 2>&1
```

### 2. Ejecutar manualmente (probar):

```bash
ssh root@194.164.160.111 '/root/aso-rank-guard/update_dashboard.sh'
```

### 3. Ver logs en tiempo real:

```bash
# Logs del dashboard
ssh root@194.164.160.111 'tail -f /root/aso-rank-guard/logs/cron.log'

# Logs de alertas Telegram
ssh root@194.164.160.111 'tail -f /root/aso-rank-guard/logs/alerts.log'
```

---

## 🔄 Actualizar Código en Servidor

Cuando hagas cambios locales y quieras subirlos:

```bash
# Subir solo el código fuente
scp -r src/* root@194.164.160.111:/root/aso-rank-guard/src/

# O subir configuración
scp config/config.yaml root@194.164.160.111:/root/aso-rank-guard/config/

# O re-ejecutar setup completo
./server_setup.sh
```

---

## ⏰ Cambiar Horarios

```bash
# Conectar al servidor
ssh root@194.164.160.111

# Editar cron
crontab -e

# Ejemplos de horarios:
0 8 * * *      # 8:00 AM
0 */6 * * *    # Cada 6 horas
30 9,15,21 * * *   # 9:30, 15:30, 21:30
```

---

## 🛑 Desactivar Automatización

```bash
ssh root@194.164.160.111 'crontab -r'
```

Para reactivar, ejecuta `./server_setup.sh` de nuevo.

---

## 📊 Flujo Completo (Servidor)

```
                  SERVIDOR 194.164.160.111
                           |
        ┌──────────────────┴──────────────────┐
        |                                      |
     16:00                                  17:00
  scheduler.py                      update_dashboard.sh
        |                                      |
        v                                      v
  ┌──────────────┐                    ┌──────────────┐
  │ rank_tracker │                    │ rank_tracker │
  │ smart_alerts │                    │ aso_expert   │
  │     ↓        │                    │ dashboard    │
  │  Telegram    │                    │     ↓        │
  └──────────────┘                    │ /var/www/... │
                                      └──────────────┘
                                             |
                                             v
                                   http://194.164.160.111/
```

---

## 🐛 Troubleshooting

### Dashboard no se actualiza:

```bash
# Ver errores
ssh root@194.164.160.111 'tail -50 /root/aso-rank-guard/logs/cron.log'

# Ejecutar manualmente
ssh root@194.164.160.111 '/root/aso-rank-guard/update_dashboard.sh'
```

### Alertas no llegan:

```bash
# Ver logs de alertas
ssh root@194.164.160.111 'tail -50 /root/aso-rank-guard/logs/alerts.log'

# Verificar config
ssh root@194.164.160.111 'cat /root/aso-rank-guard/config/config.yaml | grep -A 5 telegram'
```

### Dependencias faltantes:

```bash
ssh root@194.164.160.111 'cd /root/aso-rank-guard && python3 -m pip install -r requirements.txt --user'
```

---

## ✅ Checklist de Setup

- [ ] Ejecutar `./server_setup.sh` desde tu Mac
- [ ] Verificar cron: `ssh root@194.164.160.111 'crontab -l'`
- [ ] Probar manualmente: `ssh root@194.164.160.111 '/root/aso-rank-guard/update_dashboard.sh'`
- [ ] Verificar dashboard: http://194.164.160.111/
- [ ] Esperar a las 16:00 y verificar que llega alerta de Telegram
- [ ] Esperar a las 17:00 y verificar que dashboard se actualiza

**Una vez completo:** No necesitas hacer nada más, todo corre solo en el servidor 🎯
