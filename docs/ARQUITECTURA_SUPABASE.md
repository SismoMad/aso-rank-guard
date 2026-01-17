# 🏗️ Arquitectura con Supabase - ASO Rank Guard

## 📊 Arquitectura Actual vs Nueva

### ❌ Antes (CSV + Config.yaml)
```
┌─────────────────┐
│  rank_tracker   │ → CSV (data/ranks.csv)
└─────────────────┘
         ↓
┌─────────────────┐
│ telegram_alerts │ → Lee CSV + config.yaml
└─────────────────┘
         ↓
┌─────────────────┐
│   Telegram Bot  │ → Envía alertas
└─────────────────┘
```

**Problemas:**
- ❌ CSV no escala a múltiples usuarios
- ❌ Config.yaml con credenciales hardcodeadas
- ❌ No hay autenticación de usuarios
- ❌ Bot y web no comparten datos
- ❌ Cada usuario necesita su propio servidor

---

### ✅ Después (Supabase PostgreSQL)
```
┌──────────────────────────────────────────────────────┐
│                   SUPABASE                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ PostgreSQL │  │ Auth       │  │ Realtime   │    │
│  │ + RLS      │  │ (JWT)      │  │ (Websocket)│    │
│  └────────────┘  └────────────┘  └────────────┘    │
└──────────────────────────────────────────────────────┘
           ↑                ↑                ↑
           │                │                │
    ┌──────┴────────┬───────┴────────┬──────┴─────┐
    │               │                │            │
┌───────┐    ┌─────────────┐  ┌──────────┐  ┌──────────┐
│ Web   │    │ Telegram    │  │ Worker   │  │ Stripe   │
│(Next) │    │ Bot         │  │(BullMQ)  │  │Webhooks  │
└───────┘    └─────────────┘  └──────────┘  └──────────┘
  │                │                │            │
  └────────────────┴────────────────┴────────────┘
         TODOS USAN LA MISMA BASE DE DATOS
         (service_role key para bots/workers)
         (anon key + RLS para web/usuarios)
```

**Ventajas:**
- ✅ Multi-tenancy: Cada usuario ve solo sus datos
- ✅ Autenticación centralizada (Supabase Auth)
- ✅ Bot, web y workers comparten datos en tiempo real
- ✅ Escalable a miles de usuarios
- ✅ RLS protege datos incluso si frontend comprometido

---

## 🔐 Autenticación y Roles

### 1. Usuarios Normales (Free/Pro/Enterprise)

```typescript
// Signup (Frontend)
const { data, error } = await supabase.auth.signUp({
  email: 'usuario@example.com',
  password: 'contraseña_segura',
  options: {
    data: {
      full_name: 'Juan Pérez'
    }
  }
})

// Automáticamente:
// 1. Crea usuario en auth.users
// 2. Trigger crea profile en public.profiles
// 3. User puede login con JWT
```

**Permisos (RLS):**
- ✅ Ver solo sus apps, keywords, rankings
- ✅ Crear/editar sus propios recursos
- ❌ NO puede ver datos de otros usuarios
- ❌ NO puede modificar subscription tier

---

### 2. Rol de Admin (TÚ)

**Opción A: Flag en profiles (RECOMENDADO)**

```sql
-- Añadir columna is_admin a profiles
ALTER TABLE public.profiles ADD COLUMN is_admin BOOLEAN DEFAULT false;

-- Hacerte admin
UPDATE public.profiles 
SET is_admin = true 
WHERE email = 'tu_email@example.com';

-- Policy para admins
CREATE POLICY "Admins can view all apps"
  ON public.apps
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
        AND profiles.is_admin = true
    )
    OR user_id = auth.uid()
  );
```

**Opción B: Usar service_role key (Backend only)**

```python
# En backend/workers/admin tools
from supabase import create_client

# Service role bypasses ALL RLS
supabase_admin = create_client(
    supabase_url,
    supabase_service_role_key  # ⚠️ NUNCA en frontend
)

# Puedes ver TODOS los datos
all_apps = supabase_admin.table('apps').select('*').execute()
```

---

## 🤖 Telegram Bot con Supabase

### Flujo Actual (CSV)
```python
# Lee CSV
df = pd.read_csv('data/ranks.csv')

# Filtra cambios
changes = df[df['date'] == today]

# Envía alerta a UN usuario (hardcoded)
bot.send_message(chat_id, message)
```

### ✅ Nuevo Flujo (Supabase)
```python
from supabase import create_client
from telegram import Bot

# Inicializar Supabase (service role)
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Obtener usuarios con alertas de Telegram activas
users_with_alerts = supabase.table('alerts')\
    .select('*, profiles!inner(id, email)')\
    .eq('telegram_enabled', True)\
    .eq('is_active', True)\
    .execute()

# Para cada usuario, obtener SUS rankings
for alert in users_with_alerts.data:
    user_id = alert['user_id']
    
    # Obtener rankings recientes del usuario
    rankings = supabase.rpc('get_app_stats', {
        'p_app_id': alert['app_id']
    }).execute()
    
    # Detectar cambios
    if has_significant_change(rankings):
        # Enviar alerta SOLO a ese usuario
        send_telegram_alert(user_id, rankings)
        
        # Guardar en histórico
        supabase.table('alert_history').insert({
            'user_id': user_id,
            'alert_id': alert['id'],
            'message': message,
            'channel': 'telegram',
            'status': 'sent'
        }).execute()
```

---

## 📱 Web Dashboard con Supabase

### Frontend (Next.js)

```typescript
// app/dashboard/page.tsx
import { createServerClient } from '@supabase/ssr'

export default async function DashboardPage() {
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  // RLS automáticamente filtra por user_id = auth.uid()
  const { data: apps } = await supabase
    .from('apps')
    .select(`
      *,
      keywords(count),
      tracking_jobs(count)
    `)
    .eq('is_active', true)
  
  return <AppsList apps={apps} />
}
```

### Realtime (Rankings en vivo)

```typescript
// Hook para suscribirse a cambios
'use client'
import { useEffect, useState } from 'react'
import { createBrowserClient } from '@supabase/ssr'

export function useRankings(appId: string) {
  const [rankings, setRankings] = useState([])
  const supabase = createBrowserClient(...)
  
  useEffect(() => {
    // Fetch inicial
    fetchRankings()
    
    // Suscribirse a cambios en tiempo real
    const channel = supabase
      .channel('rankings-changes')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'rankings',
        filter: `keyword_id=in.(${keywordIds.join(',')})`
      }, (payload) => {
        setRankings(prev => [...prev, payload.new])
      })
      .subscribe()
    
    return () => { channel.unsubscribe() }
  }, [appId])
  
  return rankings
}
```

---

## 🔄 Worker BullMQ (Tracking Automático)

```typescript
// workers/ranking-tracker.ts
import { Queue, Worker } from 'bullmq'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // Service role
)

// Queue de tracking
const trackingQueue = new Queue('ranking-tracking', {
  connection: { host: 'localhost', port: 6379 }
})

// Worker que procesa jobs
new Worker('ranking-tracking', async (job) => {
  const { app_id } = job.data
  
  // 1. Obtener app y keywords
  const { data: app } = await supabase
    .from('apps')
    .select('*, keywords(*)')
    .eq('id', app_id)
    .single()
  
  // 2. Trackear rankings (usando tu lógica actual)
  const results = await trackRankings(app.keywords, app.country)
  
  // 3. Guardar en Supabase
  const rankings = results.map(r => ({
    keyword_id: r.keyword_id,
    rank: r.rank,
    tracked_at: new Date().toISOString()
  }))
  
  await supabase.table('rankings').insert(rankings)
  
  // 4. Verificar alertas
  await checkAndSendAlerts(app_id)
  
  // 5. Actualizar tracking_job
  await supabase.table('tracking_jobs')
    .update({
      status: 'completed',
      results_count: rankings.length,
      completed_at: new Date().toISOString()
    })
    .eq('id', job.id)
}, {
  connection: { host: 'localhost', port: 6379 }
})

// Scheduler (cada X horas según tier del usuario)
async function scheduleTracking() {
  const apps = await supabase
    .from('apps')
    .select(`
      *,
      profiles!inner(subscription_tier)
    `)
    .eq('is_active', true)
  
  for (const app of apps.data) {
    const frequency = getFrequency(app.profiles.subscription_tier)
    
    await trackingQueue.add('track-app', {
      app_id: app.id
    }, {
      repeat: { cron: frequency }
    })
  }
}

function getFrequency(tier: string): string {
  switch(tier) {
    case 'free': return '0 9 * * *'        // Daily at 9am
    case 'pro': return '0 */6 * * *'       // Every 6 hours
    case 'enterprise': return '0 * * * *'  // Every hour
    default: return '0 9 * * *'
  }
}
```

---

## 🔔 Sistema de Alertas Unificado

```python
# src/supabase_alerts.py
from supabase import create_client
from typing import List, Dict
import os

class SupabaseAlertManager:
    """Gestor de alertas con Supabase"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
    
    def check_and_send_alerts(self, app_id: str):
        """Verificar cambios y enviar alertas"""
        
        # 1. Obtener alertas activas para esta app
        alerts = self.supabase.table('alerts')\
            .select('*, profiles(*)')\
            .eq('app_id', app_id)\
            .eq('is_active', True)\
            .execute()
        
        # 2. Obtener rankings recientes
        recent_rankings = self.get_recent_changes(app_id)
        
        # 3. Procesar cada alerta
        for alert in alerts.data:
            for change in recent_rankings:
                if self.should_trigger_alert(alert, change):
                    message = self.format_alert_message(alert, change)
                    
                    # Enviar según canales habilitados
                    sent = False
                    if alert['telegram_enabled']:
                        sent = self.send_telegram(alert['profiles'], message)
                    
                    if alert['email_enabled']:
                        sent = self.send_email(alert['profiles']['email'], message)
                    
                    # Guardar en histórico
                    self.save_alert_history(alert, change, sent)
    
    def should_trigger_alert(self, alert: Dict, change: Dict) -> bool:
        """Verificar si debe enviar alerta"""
        threshold = alert.get('threshold', 5)
        
        if alert['alert_type'] == 'rank_drop':
            return change['rank_diff'] >= threshold
        elif alert['alert_type'] == 'rank_gain':
            return change['rank_diff'] <= -threshold
        elif alert['alert_type'] == 'new_top10':
            return change['current_rank'] <= 10 and change['prev_rank'] > 10
        
        return False
    
    def save_alert_history(self, alert: Dict, change: Dict, sent: bool):
        """Guardar histórico de alerta"""
        self.supabase.table('alert_history').insert({
            'user_id': alert['user_id'],
            'alert_id': alert['id'],
            'keyword_id': change['keyword_id'],
            'message': self.format_alert_message(alert, change),
            'channel': 'telegram' if alert['telegram_enabled'] else 'email',
            'status': 'sent' if sent else 'failed'
        }).execute()
```

---

## 🎯 Migrar Código Actual a Supabase

### 1. Reemplazar CSV por Supabase

**Antes:**
```python
# rank_tracker.py
df = pd.read_csv('data/ranks.csv')
new_data = pd.DataFrame([...])
df = pd.concat([df, new_data])
df.to_csv('data/ranks.csv', index=False)
```

**Después:**
```python
# rank_tracker.py
from supabase import create_client

supabase = create_client(url, service_key)

# Insertar rankings
supabase.table('rankings').insert([
    {
        'keyword_id': keyword_id,
        'rank': rank,
        'tracked_at': datetime.now().isoformat()
    }
    for keyword_id, rank in rankings
]).execute()

# Leer rankings
rankings = supabase.table('rankings')\
    .select('*, keywords(*)')\
    .gte('tracked_at', yesterday)\
    .execute()
```

---

### 2. Autenticación en Bot de Telegram

**Opción A: Vincular Telegram User ID a Profile**

```sql
-- Añadir columna telegram_user_id
ALTER TABLE public.profiles 
ADD COLUMN telegram_user_id TEXT UNIQUE;
```

```python
# Bot command: /start
@bot.command('start')
async def start(update, context):
    telegram_user_id = update.effective_user.id
    
    # Buscar usuario en Supabase
    user = supabase.table('profiles')\
        .select('*')\
        .eq('telegram_user_id', telegram_user_id)\
        .single()\
        .execute()
    
    if not user.data:
        await update.message.reply_text(
            "👋 Hola! Para usar el bot, primero regístrate en:\n"
            "https://asorankguard.com/signup\n\n"
            "Luego usa /link para vincular tu cuenta"
        )
    else:
        await update.message.reply_text(
            f"✅ Conectado como {user.data['email']}"
        )

@bot.command('link')
async def link(update, context):
    # Generar código único de verificación
    code = generate_code()
    
    # Guardar en Redis temporal (5 minutos)
    redis.setex(f'telegram_link:{code}', 300, telegram_user_id)
    
    await update.message.reply_text(
        f"🔗 Código de verificación: {code}\n\n"
        f"Ingresa este código en:\n"
        f"https://asorankguard.com/settings/telegram"
    )
```

---

### 3. Admin Dashboard

```typescript
// app/admin/page.tsx (Solo para is_admin = true)
import { createServerClient } from '@supabase/ssr'

export default async function AdminPage() {
  const supabase = createServerClient(...)
  
  // Verificar si es admin
  const { data: profile } = await supabase
    .from('profiles')
    .select('is_admin')
    .eq('id', (await supabase.auth.getUser()).data.user?.id)
    .single()
  
  if (!profile?.is_admin) {
    return <div>Access denied</div>
  }
  
  // Como admin, usar service_role para ver todo
  const supabaseAdmin = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY! // Server-side only
  )
  
  const { data: allUsers } = await supabaseAdmin
    .table('profiles')
    .select(`
      *,
      apps(count),
      subscriptions(tier, status)
    `)
  
  return <AdminDashboard users={allUsers} />
}
```

---

## 📝 Próximos Pasos Prácticos

### 1. Crear Usuario y Migrar Datos
```bash
# 1. Signup en Supabase Dashboard
# 2. Ejecutar migración CSV
python3 supabase/scripts/migrate_csv_to_postgres.py --email tu@email.com
```

### 2. Adaptar RankTracker
```bash
# Crear nuevo archivo con Supabase
touch src/rank_tracker_supabase.py
# Copiar lógica de scraping pero INSERT a Supabase
```

### 3. Adaptar TelegramAlerts
```bash
# Modificar telegram_alerts.py
# Leer de Supabase en lugar de CSV
# Guardar alerts en alert_history
```

### 4. Crear Worker BullMQ
```bash
# Setup BullMQ + Redis
npm install bullmq redis
# Crear worker que ejecuta tracking cada X horas
```

### 5. Desarrollar Frontend
```bash
npx create-next-app@latest web --typescript
cd web && npm install @supabase/supabase-js @supabase/ssr
# Crear dashboard con stats en tiempo real
```

---

## 🔑 Variables de Entorno (.env)

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...  # Para frontend (safe)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # Para backend/workers (secret)

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC...
# Ya no necesitas chat_id hardcoded!

# Redis (para BullMQ)
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe (futuro)
STRIPE_SECRET_KEY=sk_test...
STRIPE_WEBHOOK_SECRET=whsec...
```

---

## 🎉 Resultado Final

Con esta arquitectura:
- ✅ **Multi-usuario:** Cada uno ve solo sus datos
- ✅ **Tiempo real:** Cambios visibles inmediatamente en web
- ✅ **Bot personalizado:** Cada usuario recibe alertas de SUS keywords
- ✅ **Escalable:** De 1 a 10,000 usuarios sin cambios
- ✅ **Seguro:** RLS protege datos automáticamente
- ✅ **Admin:** Tú puedes ver todo desde panel de admin

**¿Quieres que empiece a adaptar el código actual?** Puedo crear:
1. `src/rank_tracker_supabase.py` - Versión nueva del tracker
2. `src/supabase_alerts.py` - Gestor de alertas con Supabase
3. `workers/ranking-worker.ts` - Worker BullMQ para automatización
