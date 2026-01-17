# 🚀 ASO Rank Guard - Sistema Completo con Supabase

## ✅ Sistema Integrado: Web + Bot Telegram + Supabase

### 📁 Estructura del Proyecto

```
aso-rank-guard/
├── web/
│   └── dashboard_supabase.html    # Dashboard web (acceso directo desde navegador)
├── api/
│   ├── main.py                    # API FastAPI (opcional, para servidor dedicado)
│   └── requirements.txt
├── bot_telegram_supabase.py       # Bot de Telegram con Supabase
├── track_and_save.py              # Script de tracking manual
└── .env                           # Credenciales (¡NO COMMITEAR!)
```

---

## 🎯 Opciones de Uso

### **Opción 1: Dashboard Web (MÁS SIMPLE)** ⭐ RECOMENDADO

El dashboard se conecta **directamente** a Supabase desde el navegador.

**Cómo usar:**

1. Abre el archivo en tu navegador:
```bash
open web/dashboard_supabase.html
# o doble clic en el archivo
```

2. **¡Listo!** Ya puedes ver:
   - ✅ Rankings actuales de todas las keywords
   - ✅ Gráfico de evolución (últimos 7 días)
   - ✅ Estadísticas (Top 10, Top 50, total)
   - ✅ Actualización en tiempo real

**Para subirlo a tu servidor:**
```bash
# Copiar al servidor
scp web/dashboard_supabase.html usuario@194.164.160.111:/ruta/web/

# Acceder desde: http://194.164.160.111/dashboard_supabase.html
```

**Ventajas:**
- ✅ No necesita backend (se conecta directo a Supabase)
- ✅ Funciona localmente y en servidor
- ✅ Actualización automática cada 5 minutos
- ✅ Login opcional con Supabase Auth

---

### **Opción 2: Bot de Telegram** ⭐ RECOMENDADO

El bot te permite ver rankings desde Telegram.

**Instalación:**

```bash
# 1. Instalar dependencias (solo una vez)
pip install python-telegram-bot supabase python-dotenv

# 2. Ejecutar bot
python3 bot_telegram_supabase.py
```

**Comandos disponibles:**

```
/start      - Iniciar bot
/rankings   - Ver todos los rankings
/stats      - Estadísticas generales
/top        - Top 10 keywords
/changes    - Cambios últimas 24h
/alerts     - Alertas recientes
/help       - Ayuda
```

**Ejecutar en segundo plano (servidor):**

```bash
# Opción 1: Con nohup
nohup python3 bot_telegram_supabase.py > bot.log 2>&1 &

# Opción 2: Con screen
screen -S aso-bot
python3 bot_telegram_supabase.py
# Ctrl+A, luego D para dejar corriendo
```

---

### **Opción 3: API FastAPI (Para múltiples clientes)**

Si quieres una API REST que sirva datos a múltiples dashboards.

**Instalación:**

```bash
cd api
pip install -r requirements.txt
```

**Ejecutar:**

```bash
# Desarrollo
python3 main.py

# Producción con uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# En servidor con systemd (permanente)
# Ver: scripts/aso-api.service
```

**Endpoints disponibles:**

```
GET /                           # Info de la API
GET /api/stats                  # Estadísticas generales
GET /api/rankings/current       # Rankings actuales
GET /api/rankings/history?days=7 # Histórico
GET /api/changes?hours=24       # Cambios recientes
GET /health                     # Health check
```

---

## 🔐 Configuración (.env)

Asegúrate de tener esto en tu archivo `.env`:

```bash
# Supabase
SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...  # Para web (público)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci... # Para backend (SECRETO)

# Telegram
TELEGRAM_BOT_TOKEN=8531462519:AAFv...
TELEGRAM_ALLOWED_CHATS=123456789  # Tu chat ID

# Admin
ADMIN_EMAIL=gutierrezjavier1989@gmail.com
```

---

## 📊 Tracking de Keywords

### Tracking Manual (cuando quieras)

```bash
python3 track_and_save.py
```

### Tracking Automático Diario

**Opción 1: Cron (macOS/Linux)**

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecuta todos los días a las 9am)
0 9 * * * cd /Users/javi/aso-rank-guard && /usr/bin/python3 track_and_save.py >> logs/tracking.log 2>&1
```

**Opción 2: GitHub Actions (gratis)**

Crea `.github/workflows/tracking.yml`:

```yaml
name: Track Rankings Daily

on:
  schedule:
    - cron: '0 9 * * *'  # 9am UTC diario
  workflow_dispatch:      # También manual

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install supabase python-dotenv
      - run: python track_and_save.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
```

---

## 🎨 Personalización del Dashboard

### Cambiar intervalo de actualización

En `dashboard_supabase.html` línea ~580:

```javascript
// De 5 minutos a 10 minutos
setInterval(() => loadAllData(), 10 * 60 * 1000);
```

### Cambiar colores del tema

Modificar las variables CSS en `<style>`:

```css
--color-primary: #667eea;      /* Morado */
--color-secondary: #764ba2;    /* Morado oscuro */
--color-success: #10b981;      /* Verde */
--color-warning: #f59e0b;      /* Naranja */
```

### Mostrar más keywords en gráfico

Línea ~480:

```javascript
// De top 5 a top 10
.slice(0, 10);
```

---

## 🚨 Sistema de Alertas

Las alertas se generan automáticamente cuando:

1. **Caída de ranking >5 posiciones** (configurado en BD)
2. Se guardan en tabla `alert_history`
3. Puedes verlas:
   - Dashboard web (próximamente)
   - Bot Telegram: `/alerts`
   - Supabase Dashboard

**Configurar alertas personalizadas:**

```sql
-- En Supabase SQL Editor
INSERT INTO alerts (user_id, app_id, alert_type, threshold, telegram_enabled)
VALUES (
  '5126950f-9eb9-4ea4-bf79-9ac2f65984fa',
  'd30da119-98d7-4c12-9e9f-13f3726c82fe',
  'rank_improvement',  -- Alerta de MEJORA
  10,                  -- Cuando mejore 10+ posiciones
  true
);
```

---

## 🧪 Testing

### Probar conexión a Supabase

```bash
python3 << 'EOF'
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

# Test query
result = supabase.table("keywords").select("keyword").limit(5).execute()
print("✅ Conexión exitosa!")
print(f"Keywords: {[k['keyword'] for k in result.data]}")
EOF
```

### Probar bot de Telegram

```bash
python3 bot_telegram_supabase.py

# En Telegram, envía:
# /start
# /stats
```

### Probar API

```bash
# Terminal 1: Ejecutar API
python3 api/main.py

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
```

---

## 📱 Acceso desde Móvil

### Dashboard Web

1. Sube el archivo a tu servidor
2. Accede desde: `http://194.164.160.111/dashboard_supabase.html`
3. Funciona perfecto en móvil (diseño responsive)

### Bot Telegram

¡Ya lo tienes! Telegram funciona en móvil de forma nativa.

---

## 🔧 Troubleshooting

### "Error: Failed to fetch"

**Causa:** CORS o URL incorrecta de Supabase

**Solución:**
1. Verifica que `SUPABASE_URL` en `.env` sea correcta
2. Verifica que `SUPABASE_ANON_KEY` sea la correcta (no service_role)
3. En Supabase Dashboard → Authentication → URL Configuration → Site URL agregar tu dominio

### "Bot no responde"

**Causa:** Token incorrecto o bot no ejecutándose

**Solución:**
```bash
# 1. Verificar token
echo $TELEGRAM_BOT_TOKEN

# 2. Verificar bot corriendo
ps aux | grep bot_telegram

# 3. Ver logs
tail -f bot.log
```

### "Rankings vacíos"

**Causa:** No hay datos en la BD

**Solución:**
```bash
# Ejecutar tracking manual
python3 track_and_save.py

# O insertar datos de ejemplo (ver RESUMEN_FINAL.txt)
```

---

## 🚀 Deployment Checklist

### Servidor de Producción

- [ ] Subir `dashboard_supabase.html` a servidor web
- [ ] Configurar HTTPS (Cloudflare/Let's Encrypt)
- [ ] Bot de Telegram ejecutándose con `screen` o `systemd`
- [ ] Cron job para tracking automático
- [ ] Backups de base de datos (Supabase lo hace automático)
- [ ] Monitoreo de uptime (UptimeRobot gratis)

### Variables de Entorno

- [ ] `.env` NUNCA en Git
- [ ] `.env.example` con valores de ejemplo
- [ ] Secrets configurados en GitHub Actions (si usas)
- [ ] Service role key SOLO en backend

---

## 📞 Soporte

**Dashboard Web no carga:**
1. Abre la consola del navegador (F12)
2. Busca errores en rojo
3. Verifica que SUPABASE_URL sea accesible

**Bot no recibe comandos:**
1. Verifica que esté ejecutándose: `ps aux | grep bot`
2. Revisa logs: `tail bot.log`
3. Prueba el token en: https://api.telegram.org/bot<TOKEN>/getMe

**API no arranca:**
1. Verifica dependencias: `pip list | grep fastapi`
2. Puerto ocupado: `lsof -i :8000`
3. Logs de uvicorn para más detalles

---

## 🎯 Próximos Pasos

1. **Ahora:** Abre `web/dashboard_supabase.html` y verifica que funciona
2. **Luego:** Ejecuta el bot: `python3 bot_telegram_supabase.py`
3. **Opcional:** Configura tracking automático con cron
4. **Opcional:** Sube el dashboard a tu servidor
5. **Opcional:** Configura alertas personalizadas

---

**¡Todo está listo para usar!** 🎉

Tu stack completo:
- ✅ Base de datos: Supabase (PostgreSQL + RLS)
- ✅ Dashboard: HTML/JS (se conecta directo a Supabase)
- ✅ Bot: Telegram con comandos
- ✅ API: FastAPI (opcional)
- ✅ Tracking: Script Python manual/automático

_Última actualización: 17 enero 2026_
