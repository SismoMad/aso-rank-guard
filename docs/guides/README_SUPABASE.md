# 🚀 Migración a Supabase - Guía Rápida

## 📊 Estado Actual

✅ **Completado:**
- Base de datos creada en Supabase (8 tablas, 38 RLS policies)
- Migraciones aplicadas (001-004)
- TypeScript types generados
- Código Python adaptado para Supabase

⏳ **Pendiente:**
- Configurar credenciales en `.env`
- Crear primer usuario en Supabase
- Migrar datos CSV existentes
- Probar nuevo sistema

---

## ⚡ Instalación Rápida

```bash
# 1. Ejecutar setup automático
./setup_supabase.sh

# 2. Editar credenciales
nano .env
# Añade: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, TELEGRAM_BOT_TOKEN

# 3. Activar entorno
source venv/bin/activate
```

---

## 🔑 Obtener Credenciales Supabase

### 1. SUPABASE_URL y Keys

1. Ve a: https://app.supabase.com/project/YOUR_PROJECT/settings/api
2. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_ANON_KEY` (para frontend)
   - **service_role** → `SUPABASE_SERVICE_ROLE_KEY` (para backend)

⚠️ **IMPORTANTE**: El `service_role` key es secreto. **NUNCA** lo uses en frontend.

### 2. Crear Usuario Admin

1. Ve a: https://app.supabase.com/project/YOUR_PROJECT/auth/users
2. Click en **"Add user"** → **"Create new user"**
3. Email: `tu@email.com`
4. Password: (genera una segura)
5. Click **"Create user"**

Esto automáticamente:
- ✅ Crea registro en `auth.users`
- ✅ Trigger crea perfil en `public.profiles`
- ✅ Usuario puede hacer login

### 3. Hacerte Admin (Opcional)

```sql
-- En SQL Editor de Supabase Dashboard
UPDATE public.profiles 
SET is_admin = true 
WHERE email = 'tu@email.com';
```

---

## 📦 Migrar Datos CSV a Supabase

```bash
# Migrar tus rankings existentes
python3 supabase/scripts/migrate_csv_to_postgres.py --email tu@email.com

# Esto hará:
# 1. Crear app "Audio Bible Stories & Chat"
# 2. Importar keywords desde CSV
# 3. Migrar histórico de rankings
```

---

## 🧪 Probar Nuevos Scripts

### 1. Tracker con Supabase

```bash
# Trackear todas las apps del usuario admin
python3 src/rank_tracker_supabase.py

# Output esperado:
# ✅ RankTrackerSupabase inicializado
# 👤 Usuario encontrado: tu@email.com
# 📱 1 apps encontradas
# 🚀 Tracking: Audio Bible Stories & Chat
# [1/50] Buscando 'bible stories' en US...
# ✅ 50 rankings guardados en Supabase
```

### 2. Sistema de Alertas

```bash
# Probar detección de cambios (modo test)
TEST_MODE=true python3 src/supabase_alerts.py

# Output esperado:
# 🧪 MODO TEST activado
# 🔍 Verificando alertas para app...
# 📊 5 cambios detectados
# 🧪 [TEST] Telegram a tu@email.com:
# 🔔 Alerta de Ranking...
```

### 3. Health Check

```python
# Script de prueba rápido
from src.supabase_client import get_supabase_client

client = get_supabase_client(use_service_role=True)

if client.health_check():
    print("✅ Supabase conectado")
    
    # Ver tus apps
    user = client.get_user_by_email('tu@email.com')
    apps = client.get_user_apps(user['id'])
    print(f"📱 Tienes {len(apps)} apps")
else:
    print("❌ Error de conexión")
```

---

## 🔄 Diferencias Clave: CSV vs Supabase

| Característica | CSV (Antiguo) | Supabase (Nuevo) |
|----------------|---------------|------------------|
| **Storage** | `data/ranks.csv` | PostgreSQL table `rankings` |
| **Multi-user** | ❌ Un usuario | ✅ Ilimitados (RLS) |
| **Tiempo real** | ❌ No | ✅ Sí (websockets) |
| **Límite datos** | ~1GB (CSV) | ~8GB gratis (Postgres) |
| **Queries** | pandas (lento) | SQL (rápido) |
| **Alertas** | config.yaml | Tabla `alerts` |
| **Histórico** | ❌ No | Tabla `alert_history` |

---

## 📁 Nuevos Archivos Creados

```
aso-rank-guard/
├── .env.example                      # ⭐ Variables de entorno
├── setup_supabase.sh                 # ⭐ Script de instalación
├── requirements-supabase.txt         # ⭐ Dependencias Python
│
├── src/
│   ├── supabase_client.py           # ⭐ Cliente Supabase reutilizable
│   ├── rank_tracker_supabase.py     # ⭐ Tracker con Supabase
│   └── supabase_alerts.py           # ⭐ Alertas con Supabase
│
├── docs/
│   └── ARQUITECTURA_SUPABASE.md     # ⭐ Arquitectura completa
│
└── supabase/
    ├── migrations/                   # ✅ Migraciones SQL (ya aplicadas)
    ├── scripts/
    │   └── migrate_csv_to_postgres.py  # ✅ Script de migración
    ├── SCHEMA_DESIGN.md              # ✅ Diseño de BD
    └── database.types.ts             # ✅ TypeScript types
```

---

## 🎯 Workflow Recomendado

### Fase 1: Setup Inicial (HOY)
```bash
1. ./setup_supabase.sh
2. Editar .env con credenciales
3. Crear usuario en Supabase Dashboard
4. Migrar CSV: python3 supabase/scripts/migrate_csv_to_postgres.py
```

### Fase 2: Probar Sistema (MAÑANA)
```bash
1. Test tracker: python3 src/rank_tracker_supabase.py
2. Test alertas: TEST_MODE=true python3 src/supabase_alerts.py
3. Verificar datos en Supabase Dashboard
```

### Fase 3: Producción (PRÓXIMA SEMANA)
```bash
1. Configurar cron job con tracker
2. Vincular Telegram bot a DB
3. Desarrollar frontend Next.js
4. Activar alertas reales (TEST_MODE=false)
```

---

## 🤖 Bot de Telegram con Supabase

### Vincular Telegram User ID

```python
# En tu bot (src/telegram_bot.py)
from telegram.ext import CommandHandler, Application
from src.supabase_client import get_supabase_client

async def link_account(update, context):
    telegram_user_id = update.effective_user.id
    
    # Generar código de verificación
    code = generate_code()  # e.g., "ABC123"
    
    # Guardar en Redis temporal (5 minutos)
    redis.setex(f'telegram_link:{code}', 300, telegram_user_id)
    
    await update.message.reply_text(
        f"🔗 Código de verificación: `{code}`\n\n"
        f"Ingresa este código en:\n"
        f"https://asorankguard.com/settings/telegram"
    )

# Registrar comando
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("link", link_account))
```

### Frontend: Verificar Código

```typescript
// app/settings/telegram/page.tsx
async function linkTelegram(code: string) {
  // 1. Obtener telegram_user_id desde Redis
  const telegramUserId = await redis.get(`telegram_link:${code}`)
  
  // 2. Actualizar profile con telegram_user_id
  const { error } = await supabase
    .from('profiles')
    .update({ telegram_user_id: telegramUserId })
    .eq('id', user.id)
  
  if (!error) {
    toast.success('✅ Telegram vinculado correctamente')
  }
}
```

---

## 🚨 Troubleshooting

### Error: "supabase-py not installed"
```bash
source venv/bin/activate
pip install -r requirements-supabase.txt
```

### Error: "Missing Supabase credentials"
```bash
# Verifica que .env existe y tiene valores correctos
cat .env | grep SUPABASE_URL

# Debe mostrar:
# SUPABASE_URL=https://tu-proyecto.supabase.co
# (NO debe ser https://xxxxxxxxxxxxx.supabase.co)
```

### Error: "User not found"
```bash
# Primero crea el usuario en Supabase Dashboard:
# https://app.supabase.com/project/_/auth/users
# Luego ejecuta el script con ese email
```

### Error: "row-level security policy violation"
```bash
# Verifica que estás usando service_role key en backend:
echo $SUPABASE_SERVICE_ROLE_KEY

# El service_role key BYPASSES RLS (es correcto para scripts backend)
```

---

## 📚 Documentación Adicional

- **Arquitectura completa**: [docs/ARQUITECTURA_SUPABASE.md](docs/ARQUITECTURA_SUPABASE.md)
- **Schema BD**: [supabase/SCHEMA_DESIGN.md](supabase/SCHEMA_DESIGN.md)
- **Plan de migración**: [supabase/MIGRATION_PLAN.md](supabase/MIGRATION_PLAN.md)
- **Reporte de completitud**: [supabase/MIGRATION_COMPLETION_REPORT.md](supabase/MIGRATION_COMPLETION_REPORT.md)
- **Copilot Instructions**: [.github/copilot-instructions.md](.github/copilot-instructions.md)

---

## ✅ Checklist de Migración

- [ ] Setup ejecutado (`./setup_supabase.sh`)
- [ ] `.env` configurado con credenciales
- [ ] Usuario creado en Supabase Dashboard
- [ ] Usuario marcado como admin (opcional)
- [ ] CSV migrado a Supabase
- [ ] Tracker probado (`rank_tracker_supabase.py`)
- [ ] Alertas probadas (`supabase_alerts.py`)
- [ ] Telegram bot vinculado
- [ ] Cron job configurado
- [ ] Frontend Next.js iniciado

---

**¿Dudas?** Revisa [docs/ARQUITECTURA_SUPABASE.md](docs/ARQUITECTURA_SUPABASE.md) o pregunta a GitHub Copilot 🤖
