# 🏗️ Arquitectura del Sistema - ASO Rank Guard

## 📊 Diagrama Completo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   VPS (194.164.160.111)  │
                    │   Alma Linux 9 + Plesk   │
                    │   2 vCPU, 2GB RAM, 80GB  │
                    └────────────┬─────────────┘
                                 │
            ┌────────────────────┴────────────────────┐
            │                                         │
    ┌───────▼────────┐                       ┌───────▼────────┐
    │ Nginx (Port 80)│                       │ Firewall       │
    │ Reverse Proxy  │                       │ (Firewalld)    │
    │ SSL/HTTPS      │                       │ Ports: 80,443  │
    └───────┬────────┘                       │ 3000, 8000     │
            │                                 └────────────────┘
            │
    ┌───────┴───────────────────────────┐
    │                                   │
    │  Location Routing:                │
    │  /           → Next.js (3000)     │
    │  /api/*      → FastAPI (8000)     │
    │  /health     → FastAPI (8000)     │
    │  /docs       → FastAPI (8000)     │
    │                                   │
    └───────┬───────────────────────────┘
            │
    ┌───────┴────────────────────────────┐
    │                                    │
┌───▼─────────────┐          ┌───────────▼──────────┐
│   PM2 Process   │          │   PM2 Process        │
│   aso-web       │          │   aso-api            │
│                 │          │                      │
│ ┌─────────────┐ │          │ ┌──────────────────┐ │
│ │  Next.js    │ │          │ │  FastAPI         │ │
│ │  Port: 3000 │ │          │ │  Port: 8000      │ │
│ │             │ │          │ │                  │ │
│ │  Frontend:  │ │          │ │  Backend API:    │ │
│ │  - SSR      │ │          │ │  - /api/stats    │ │
│ │  - Dashboard│ │          │ │  - /api/rankings │ │
│ │  - Login    │ │          │ │  - /health       │ │
│ │  - Settings │ │          │ │  - /docs         │ │
│ └─────────────┘ │          │ └──────────────────┘ │
│                 │          │                      │
│  Auto-restart:  │          │  Auto-restart: ✅    │
│  ✅              │          │  Max Memory: 500M    │
│  Max Memory:    │          │                      │
│  500M           │          │  Python venv:        │
│                 │          │  /var/www/.../venv/  │
└─────────┬───────┘          └──────────┬───────────┘
          │                             │
          │                             │
          └──────────┬──────────────────┘
                     │
          ┌──────────▼──────────────────────────────┐
          │     Supabase Client Library            │
          │     (connects to cloud)                │
          └──────────┬──────────────────────────────┘
                     │
                     │ HTTPS
                     │
          ┌──────────▼──────────────────────────────┐
          │   Supabase Cloud                       │
          │   (bidqxydrybpuwyskrarh.supabase.co)  │
          │                                         │
          │   ┌───────────────────────────────┐    │
          │   │  PostgreSQL Database          │    │
          │   │  - Tables: apps, keywords,    │    │
          │   │    rankings, users, profiles  │    │
          │   │  - Row Level Security (RLS)   │    │
          │   │  - Auth: JWT tokens           │    │
          │   └───────────────────────────────┘    │
          │                                         │
          │   ┌───────────────────────────────┐    │
          │   │  Supabase Auth                │    │
          │   │  - User management            │    │
          │   │  - JWT token generation       │    │
          │   │  - Password reset             │    │
          │   └───────────────────────────────┘    │
          │                                         │
          │   ┌───────────────────────────────┐    │
          │   │  Supabase Storage (future)    │    │
          │   │  - File uploads               │    │
          │   │  - CSV imports                │    │
          │   └───────────────────────────────┘    │
          └─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED PROCESSES (CRON)                          │
└─────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────────┐
    │  Cron Job 1: Tracking                                 │
    │  Schedule: Daily at 9:00 AM (0 9 * * *)              │
    │                                                        │
    │  /var/www/aso-rank-guard/run-tracking.sh             │
    │  └─> Activates venv                                   │
    │  └─> Runs: python src/rank_tracker_supabase.py       │
    │  └─> Fetches rankings from iTunes API                │
    │  └─> Saves to Supabase                               │
    │  └─> Sends Telegram alerts if changes detected       │
    │  └─> Logs to: logs/cron-tracking.log                 │
    └───────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────────┐
    │  Cron Job 2: Backups                                  │
    │  Schedule: Daily at 2:00 AM (0 2 * * *)              │
    │                                                        │
    │  /var/www/aso-rank-guard/backup.sh                   │
    │  └─> Backs up data/ folder                           │
    │  └─> Backs up logs/ folder                           │
    │  └─> Backs up config files (.env, etc)               │
    │  └─> Saves to: /var/backups/aso-rank-guard/         │
    │  └─> Deletes backups older than 7 days               │
    │  └─> Logs to: logs/backup.log                        │
    └───────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                              │
└─────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────┐         ┌────────────────────┐
    │   iTunes Search    │         │   Telegram Bot     │
    │   API              │         │   API              │
    │                    │         │                    │
    │   Used by:         │         │   Used by:         │
    │   rank_tracker_    │         │   telegram_        │
    │   supabase.py      │         │   alerts.py        │
    │                    │         │                    │
    │   Fetches:         │         │   Sends:           │
    │   - App rankings   │         │   - Ranking alerts │
    │   - Search results │         │   - Daily summaries│
    │   - By keyword     │         │   - Error alerts   │
    └────────────────────┘         └────────────────────┘
```

---

## 🔄 Flujo de Datos

### 1. Usuario accede a la web
```
Usuario → Navegador
   ↓
http://194.164.160.111
   ↓
Nginx (Puerto 80/443)
   ↓
PM2: aso-web (Next.js:3000)
   ↓
Renderiza página (SSR)
   ↓
Envía HTML al navegador
```

### 2. Usuario hace login
```
Usuario → Form login
   ↓
Next.js llama a Supabase Client
   ↓
POST a Supabase Auth API
   ↓
Supabase valida credenciales
   ↓
Devuelve JWT token
   ↓
Next.js guarda token en cookie
   ↓
Redirige a /dashboard
```

### 3. Dashboard carga datos
```
Dashboard página (Next.js)
   ↓
Llama a: /api/stats
   ↓
Nginx → PM2: aso-api (FastAPI:8000)
   ↓
FastAPI usa Supabase Client
   ↓
Query a Supabase PostgreSQL
   ↓
SELECT * FROM keywords WHERE user_id = ...
   ↓
Supabase valida RLS policies
   ↓
Devuelve datos filtrados
   ↓
FastAPI formatea JSON
   ↓
Next.js renderiza gráficos
```

### 4. Tracking automático (Cron)
```
Cron ejecuta a las 9:00 AM
   ↓
/var/www/aso-rank-guard/run-tracking.sh
   ↓
Activa venv de Python
   ↓
python src/rank_tracker_supabase.py
   ↓
Para cada keyword activa:
   ├─> Llama a iTunes Search API
   ├─> Extrae ranking de la app
   ├─> Compara con ranking anterior
   └─> Guarda en Supabase (tabla: rankings)
   ↓
Si hay cambios significativos:
   └─> Envía alerta a Telegram Bot API
   ↓
Guarda resumen en logs/last_run_summary.txt
```

---

## 📁 Estructura de Archivos en el Servidor

```
/var/www/aso-rank-guard/
│
├── .env                           # ⚙️ Variables backend
│   ├── SUPABASE_URL
│   ├── SUPABASE_SERVICE_ROLE_KEY
│   └── TELEGRAM_BOT_TOKEN
│
├── venv/                          # 🐍 Entorno Python
│   ├── bin/
│   │   ├── python3
│   │   ├── pip
│   │   └── uvicorn
│   └── lib/python3.11/site-packages/
│
├── api/                           # 🔌 Backend API
│   ├── main.py                    # FastAPI app
│   └── requirements.txt
│
├── src/                           # 📦 Backend logic
│   ├── rank_tracker_supabase.py   # Tracking script
│   ├── telegram_alerts.py
│   ├── supabase_client.py
│   └── ...
│
├── web-app/                       # ⚛️ Frontend Next.js
│   ├── app/                       # Next.js 14 App Router
│   │   ├── page.tsx               # Homepage
│   │   ├── login/
│   │   ├── dashboard/
│   │   └── api/                   # API routes (unused)
│   │
│   ├── components/                # React components
│   ├── lib/                       # Utilities
│   │
│   ├── .next/                     # 🏗️ Build output
│   │   ├── server/
│   │   ├── static/
│   │   └── standalone/            # Standalone server
│   │
│   ├── .env.production            # ⚙️ Variables frontend
│   │   ├── NEXT_PUBLIC_SUPABASE_URL
│   │   ├── NEXT_PUBLIC_SUPABASE_ANON_KEY
│   │   └── NEXT_PUBLIC_API_URL
│   │
│   ├── package.json
│   └── node_modules/
│
├── logs/                          # 📝 Logs
│   ├── rank_guard.log             # Tracking logs
│   ├── api-out.log                # FastAPI stdout
│   ├── api-error.log              # FastAPI stderr
│   ├── web-out.log                # Next.js stdout
│   ├── web-error.log              # Next.js stderr
│   ├── cron-tracking.log          # Cron tracking logs
│   ├── backup.log                 # Backup logs
│   └── last_run_summary.txt       # Último tracking resumen
│
├── data/                          # 💾 Data (legacy CSV)
│   ├── ranks.csv                  # Histórico rankings (deprecated)
│   ├── competitors.csv
│   └── backups/
│
├── ecosystem.config.js            # ⚙️ PM2 config
│   ├── aso-api config
│   └── aso-web config
│
├── run-tracking.sh                # 🔄 Cron wrapper
├── backup.sh                      # 💾 Backup script
│
└── requirements.txt               # 📦 Python dependencies
```

---

## 🔐 Puertos y Servicios

| Puerto | Servicio | Acceso | Propósito |
|--------|----------|--------|-----------|
| **80** | Nginx | Público | HTTP (redirige a 443) |
| **443** | Nginx | Público | HTTPS (SSL/TLS) |
| **3000** | Next.js | Interno | Frontend (via Nginx) |
| **8000** | FastAPI | Interno | Backend API (via Nginx) |
| **8443** | Plesk | Público | Panel de control (opcional) |
| **22** | SSH | Restringido | Administración |

---

## 🔒 Seguridad en Capas

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Firewall (firewalld)                     │
│  - Solo puertos 80, 443, 22, 8443 abiertos        │
│  - Resto bloqueados                                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Nginx Reverse Proxy                      │
│  - No expone puertos 3000, 8000 directamente       │
│  - Headers de seguridad                            │
│  - Rate limiting (configurable)                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: Application Level                        │
│  - Next.js: CSRF protection, XSS prevention        │
│  - FastAPI: CORS config, input validation          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 4: Database (Supabase)                      │
│  - Row Level Security (RLS)                        │
│  - JWT token validation                            │
│  - user_id filtering automático                    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 5: Environment Variables                    │
│  - .env con chmod 600 (solo root puede leer)       │
│  - SERVICE_ROLE_KEY nunca expuesta a frontend      │
│  - ANON_KEY segura con RLS                         │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Optimizaciones

### PM2 Auto-Restart
```javascript
// ecosystem.config.js
{
  autorestart: true,         // Reinicia si crashea
  max_memory_restart: '500M', // Reinicia si supera RAM
  instances: 1,              // 1 instancia (2GB RAM total)
}
```

### Nginx Caching
```nginx
location /_next/static {
    proxy_cache_valid 200 60m;  # Cachea assets 60 min
    add_header Cache-Control "public, immutable";
}
```

### Next.js Production Build
```bash
npm run build  # Optimiza JS, CSS, imágenes
# Resultado: ~10MB build vs ~200MB dev
```

---

## 📈 Escalabilidad Futura

### Cuando crezcas, puedes:

1. **Aumentar recursos del VPS:**
   - Upgrade a 4 vCPU, 4GB RAM
   - PM2 con múltiples instancias (cluster mode)

2. **Separar servicios:**
   - VPS 1: Solo Next.js (frontend)
   - VPS 2: Solo FastAPI (backend)
   - VPS 3: Redis para caché

3. **Usar CDN:**
   - Cloudflare para assets estáticos
   - Edge caching para Next.js

4. **Base de datos local:**
   - Migrar de Supabase a PostgreSQL local
   - Mejor rendimiento, sin latencia cloud

5. **Load Balancer:**
   - Nginx como balanceador
   - Múltiples instancias de Next.js/FastAPI

---

## 🎯 Monitoreo de Salud

### Health Check Endpoints

```bash
# API Health
curl http://194.164.160.111/health
# Response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2026-01-17T20:00:00"
# }

# PM2 Status
pm2 status
# Response:
# ┌─────┬───────────┬─────────┬─────────┬──────────┐
# │ id  │ name      │ mode    │ status  │ memory   │
# ├─────┼───────────┼─────────┼─────────┼──────────┤
# │ 0   │ aso-api   │ fork    │ online  │ 150 MB   │
# │ 1   │ aso-web   │ fork    │ online  │ 200 MB   │
# └─────┴───────────┴─────────┴─────────┴──────────┘
```

---

## 🔧 Troubleshooting Diagram

```
        ❓ ¿App no carga?
                │
        ┌───────┴────────┐
        │                │
    ¿Error 502?     ¿Error 404?
        │                │
        ▼                ▼
   pm2 status      Nginx config
   pm2 restart     nginx -t
        │
        ▼
   ¿API funciona?
        │
    ┌───┴───┐
    │       │
  Sí       No
    │       │
    │       └─> Ver logs:
    │           pm2 logs aso-api
    │           
    ▼
¿Next.js funciona?
    │
  ┌─┴─┐
  │   │
 Sí  No
  │   │
  │   └─> Ver logs:
  │       pm2 logs aso-web
  │       
  ▼
¿Supabase conecta?
  │
  └─> curl API endpoint
      Ver credentials en .env
```

---

**Este diagrama te ayudará a entender cómo funciona todo el sistema juntos! 🚀**
