# 🚀 ROADMAP: De Script Personal a SaaS Escalable

## 🎯 Objetivo
Convertir ASO Rank Guard en un producto SaaS que cualquiera pueda usar sin conocimientos técnicos.

---

## 📅 FASE 1: MVP SaaS (Semana 1-2)

### Backend: Migrar CSV → Supabase

**1.1 Setup Supabase (30 min)**
```bash
# Crear cuenta en supabase.com
# Crear proyecto: aso-rank-guard

# Instalar cliente
pip install supabase

# Crear .env con credenciales
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
```

**1.2 Crear esquema de base de datos (1 hora)**
```sql
-- users (Supabase Auth lo crea automáticamente)

-- apps
CREATE TABLE apps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    app_id BIGINT NOT NULL, -- iTunes App ID
    name TEXT NOT NULL,
    bundle_id TEXT,
    country TEXT DEFAULT 'US',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, app_id)
);

-- keywords
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    priority TEXT DEFAULT 'medium', -- low, medium, high
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(app_id, keyword)
);

-- rankings (histórico - reemplaza ranks.csv)
CREATE TABLE rankings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword_id UUID REFERENCES keywords(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    date TIMESTAMPTZ DEFAULT NOW(),
    country TEXT DEFAULT 'US',
    metadata JSONB -- para guardar datos extra
);

-- alert_configs
CREATE TABLE alert_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    telegram_chat_id TEXT,
    telegram_enabled BOOLEAN DEFAULT false,
    email TEXT,
    email_enabled BOOLEAN DEFAULT false,
    webhook_url TEXT,
    webhook_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- subscriptions (para planes Free/Pro)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT DEFAULT 'free', -- free, pro, enterprise
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active', -- active, cancelled, expired
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Índices para performance
CREATE INDEX idx_rankings_keyword_date ON rankings(keyword_id, date DESC);
CREATE INDEX idx_keywords_app ON keywords(app_id);
CREATE INDEX idx_apps_user ON apps(user_id);
```

**1.3 Row Level Security (RLS) - Seguridad multi-tenant (30 min)**
```sql
-- Usuarios solo ven sus propios datos
ALTER TABLE apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_configs ENABLE ROW LEVEL SECURITY;

-- Políticas
CREATE POLICY "Users can view own apps" ON apps
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own apps" ON apps
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Similar para otras tablas...
```

**1.4 Migrar datos CSV → Supabase (1 hora)**
```python
# scripts/migrate_csv_to_supabase.py
import pandas as pd
from supabase import create_client
import os

# Conectar a Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# 1. Crear usuario de prueba (tú mismo)
# Ya existe si hiciste signup en Supabase UI

# 2. Crear tu app
app_data = {
    'user_id': 'TU_USER_ID',  # Obtenlo de Supabase dashboard
    'app_id': 6749528117,
    'name': 'Audio Bible Stories & Chat',
    'country': 'US'
}
app = supabase.table('apps').insert(app_data).execute()
app_uuid = app.data[0]['id']

# 3. Migrar keywords desde config.yaml
import yaml
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

for kw in config['keywords']:
    supabase.table('keywords').insert({
        'app_id': app_uuid,
        'keyword': kw,
        'priority': 'medium'
    }).execute()

print(f"✅ {len(config['keywords'])} keywords migradas")

# 4. Migrar rankings desde CSV
df = pd.read_csv('data/ranks.csv')

# Agrupar por keyword para obtener keyword_id
for keyword in df['keyword'].unique():
    # Obtener keyword_id de Supabase
    kw_result = supabase.table('keywords')\
        .select('id')\
        .eq('app_id', app_uuid)\
        .eq('keyword', keyword)\
        .execute()
    
    if kw_result.data:
        keyword_id = kw_result.data[0]['id']
        
        # Insertar rankings históricos
        kw_rankings = df[df['keyword'] == keyword]
        for _, row in kw_rankings.iterrows():
            supabase.table('rankings').insert({
                'keyword_id': keyword_id,
                'rank': int(row['rank']),
                'date': row['date'],
                'country': row['country']
            }).execute()

print(f"✅ {len(df)} rankings migrados")
```

---

## 📅 FASE 2: Frontend con UI (Semana 3-4)

### 2.1 Landing Page + Auth (3 días)

**Stack:** Next.js 14 + Supabase Auth

```bash
# Crear proyecto Next.js
npx create-next-app@latest aso-rank-guard-web
cd aso-rank-guard-web
npm install @supabase/ssr @supabase/supabase-js
```

**Páginas necesarias:**
```
/                    → Landing (features, pricing, demo)
/login               → Login con email/Google
/signup              → Registro
/dashboard           → Tu dashboard actual (migrado)
/keywords            → Gestión de keywords (UI)
/settings            → Configuración de alertas
/billing             → Planes y pagos
```

**Componente de Auth:**
```typescript
// app/login/page.tsx
'use client'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

export default function LoginPage() {
  const supabase = createClientComponentClient()
  
  const handleLogin = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    
    if (!error) {
      router.push('/dashboard')
    }
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleLogin}>
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button>Login</button>
        
        {/* Login con Google */}
        <button onClick={() => supabase.auth.signInWithOAuth({
          provider: 'google'
        })}>
          Continuar con Google
        </button>
      </form>
    </div>
  )
}
```

### 2.2 Keywords Manager UI (2 días)

**Reemplazar:** Terminal + YAML → UI web

```typescript
// app/keywords/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

export default function KeywordsPage() {
  const supabase = createClientComponentClient()
  const [keywords, setKeywords] = useState([])
  const [newKeyword, setNewKeyword] = useState('')
  
  // Cargar keywords
  useEffect(() => {
    loadKeywords()
  }, [])
  
  async function loadKeywords() {
    const { data } = await supabase
      .from('keywords')
      .select('*, app:apps(name)')
      .order('created_at', { ascending: false })
    
    setKeywords(data)
  }
  
  // Añadir keyword
  async function addKeyword() {
    const { error } = await supabase
      .from('keywords')
      .insert({
        app_id: selectedAppId,
        keyword: newKeyword.toLowerCase(),
        priority: 'medium'
      })
    
    if (!error) {
      setNewKeyword('')
      loadKeywords()
      toast.success('✅ Keyword añadida')
    }
  }
  
  // Eliminar keyword
  async function deleteKeyword(id) {
    await supabase.from('keywords').delete().eq('id', id)
    loadKeywords()
  }
  
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Keywords</h1>
      
      {/* Añadir nueva */}
      <div className="mb-8 flex gap-2">
        <input
          value={newKeyword}
          onChange={(e) => setNewKeyword(e.target.value)}
          placeholder="Ej: bible stories for sleep"
          className="flex-1 px-4 py-2 border rounded"
        />
        <button onClick={addKeyword} className="px-6 py-2 bg-blue-500 text-white rounded">
          ➕ Añadir
        </button>
      </div>
      
      {/* Lista */}
      <div className="space-y-2">
        {keywords.map(kw => (
          <div key={kw.id} className="flex items-center justify-between p-4 bg-white rounded shadow">
            <div>
              <span className="font-medium">{kw.keyword}</span>
              <span className="ml-2 text-gray-500 text-sm">{kw.app.name}</span>
            </div>
            <button onClick={() => deleteKeyword(kw.id)} className="text-red-500">
              🗑️ Eliminar
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Beneficio:** ¡Ya no necesitas editar YAML ni ejecutar scripts! 🎉

### 2.3 Settings para Telegram/Email (1 día)

```typescript
// app/settings/page.tsx
export default function SettingsPage() {
  const [config, setConfig] = useState({
    telegram_enabled: false,
    telegram_chat_id: '',
    email_enabled: false,
    email: ''
  })
  
  async function saveSettings() {
    await supabase
      .from('alert_configs')
      .upsert({
        user_id: session.user.id,
        ...config
      })
    
    toast.success('✅ Configuración guardada')
  }
  
  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Configuración de Alertas</h1>
      
      {/* Telegram */}
      <div className="mb-6">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={config.telegram_enabled}
            onChange={(e) => setConfig({...config, telegram_enabled: e.target.checked})}
          />
          Alertas por Telegram
        </label>
        
        {config.telegram_enabled && (
          <div className="mt-2">
            <p className="text-sm text-gray-600 mb-2">
              1. Abre Telegram y busca <strong>@{process.env.NEXT_PUBLIC_BOT_USERNAME}</strong><br/>
              2. Envía /start<br/>
              3. El bot te dirá tu Chat ID
            </p>
            <input
              placeholder="Tu Chat ID"
              value={config.telegram_chat_id}
              onChange={(e) => setConfig({...config, telegram_chat_id: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>
        )}
      </div>
      
      {/* Email */}
      <div className="mb-6">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={config.email_enabled}
            onChange={(e) => setConfig({...config, email_enabled: e.target.checked})}
          />
          Alertas por Email
        </label>
        
        {config.email_enabled && (
          <input
            type="email"
            value={config.email}
            onChange={(e) => setConfig({...config, email: e.target.value})}
            className="mt-2 w-full px-4 py-2 border rounded"
          />
        )}
      </div>
      
      <button onClick={saveSettings} className="px-6 py-2 bg-blue-500 text-white rounded">
        💾 Guardar
      </button>
    </div>
  )
}
```

---

## 📅 FASE 3: Automatización con Workers (Semana 5)

### 3.1 BullMQ Queue System

```typescript
// workers/tracking-queue.ts
import Queue from 'bull'
import { trackKeywordRank } from '../src/rank_tracker'

const rankingQueue = new Queue('ranking-jobs', {
  redis: process.env.REDIS_URL
})

// Añadir job cuando usuario añade keyword
export async function scheduleTracking(keywordId: string) {
  await rankingQueue.add('track', {
    keywordId
  }, {
    repeat: {
      cron: '0 9 * * *' // Diario a las 9 AM
    }
  })
}

// Worker procesa jobs
rankingQueue.process('track', async (job) => {
  const { keywordId } = job.data
  
  // 1. Obtener keyword info de Supabase
  const kw = await supabase
    .from('keywords')
    .select('*, app:apps(*)')
    .eq('id', keywordId)
    .single()
  
  // 2. Trackear ranking (tu código existente)
  const rank = await trackKeywordRank(kw.keyword, kw.app.country)
  
  // 3. Guardar en DB
  await supabase.table('rankings').insert({
    keyword_id: keywordId,
    rank,
    date: new Date()
  })
  
  // 4. Comparar con anterior
  const previous = await supabase
    .from('rankings')
    .select('rank')
    .eq('keyword_id', keywordId)
    .order('date', { ascending: false })
    .limit(2)
  
  if (previous.length === 2) {
    const delta = previous[0].rank - previous[1].rank
    
    // 5. Enviar alerta si cambio significativo
    if (Math.abs(delta) >= 5) {
      await sendAlert(kw.app.user_id, {
        keyword: kw.keyword,
        rank_now: previous[0].rank,
        rank_prev: previous[1].rank,
        delta
      })
    }
  }
})
```

### 3.2 Cron Job Centralizado

```typescript
// cron/daily-tracking.ts
import { createClient } from '@supabase/supabase-js'

// Ejecutar cada día a las 9 AM (Railway Cron o Vercel Cron)
export async function runDailyTracking() {
  const supabase = createClient(...)
  
  // Obtener TODAS las keywords activas de TODOS los usuarios
  const { data: keywords } = await supabase
    .from('keywords')
    .select('id, keyword, app:apps(user_id, app_id, country)')
    .eq('enabled', true)
  
  console.log(`📊 Tracking ${keywords.length} keywords...`)
  
  // Añadir a queue (procesa en paralelo)
  for (const kw of keywords) {
    await scheduleTracking(kw.id)
  }
}
```

---

## 📅 FASE 4: Pagos con Stripe (Semana 6)

### 4.1 Planes

```typescript
const PLANS = {
  free: {
    name: 'Free',
    price: 0,
    limits: {
      apps: 1,
      keywords: 10,
      checks_per_day: 1
    }
  },
  pro: {
    name: 'Pro',
    price: 19, // $19/mes
    limits: {
      apps: 3,
      keywords: 100,
      checks_per_day: 4,
      competitor_tracking: true,
      api_access: true
    }
  },
  enterprise: {
    name: 'Enterprise',
    price: 99,
    limits: {
      apps: 'unlimited',
      keywords: 'unlimited',
      checks_per_day: 24,
      white_label: true,
      priority_support: true
    }
  }
}
```

### 4.2 Stripe Integration

```typescript
// app/api/create-checkout/route.ts
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY)

export async function POST(req: Request) {
  const { plan } = await req.json()
  
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [{
      price: PLANS[plan].stripe_price_id,
      quantity: 1,
    }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/dashboard?success=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/billing`,
  })
  
  return Response.json({ url: session.url })
}
```

---

## 🎯 RESULTADO FINAL

### UI Completa (Sin código/terminal):

```
┌─────────────────────────────────────────┐
│  ASO Rank Guard - Dashboard             │
├─────────────────────────────────────────┤
│  👤 Javi (Pro Plan)              🔔 🚪  │
├─────────────────────────────────────────┤
│  📱 Apps:                                │
│  ┌─────────────────────────────────┐    │
│  │ 📖 Audio Bible Stories & Chat   │    │
│  │ 82 keywords · US                │    │
│  │ [📊 Ver Dashboard]              │    │
│  └─────────────────────────────────┘    │
│  [➕ Add New App]                        │
├─────────────────────────────────────────┤
│  🔑 Keywords:                            │
│  [+ Add Keyword]  🔍 Search              │
│                                          │
│  ✅ biblenow              Rank #2  📈    │
│  ✅ bible sleep           Rank #5  📈    │
│  ✅ bedtime bible stories Rank #10 ➡️    │
│  ✅ bible chat app        Rank #72 📉    │
│  ... (78 more)                           │
├─────────────────────────────────────────┤
│  ⚙️  Settings:                           │
│  ☑️  Telegram alerts → @biblenow_bot     │
│  ☑️  Email alerts → javi@example.com     │
│  ☐  Webhook → https://...                │
│  [💾 Save]                               │
└─────────────────────────────────────────┘
```

**¡Zero configuración técnica!** ✅

---

## 📊 COMPARATIVA

| Aspecto | Ahora (Script) | Después (SaaS) |
|---------|---------------|----------------|
| Setup | 1-2 horas | 2 minutos |
| Usuarios | Solo tú | Ilimitados |
| Keywords | YAML manual | UI web |
| Alertas | Terminal config | Toggle en UI |
| Base de datos | CSV | PostgreSQL |
| Escalabilidad | 1 usuario | Miles |
| Ingresos | $0 | $19-99/usuario/mes |
| Backup | Manual | Automático |
| Multi-tenant | ❌ | ✅ |
| API pública | Básica | Completa con docs |

---

## 💰 MODELO DE NEGOCIO

### Pricing:

- **Free**: 1 app, 10 keywords, 1 check/día → Adquirir usuarios
- **Pro ($19/mes)**: 3 apps, 100 keywords, 4 checks/día → Target principal
- **Enterprise ($99/mes)**: Unlimited, API, white-label → Agencias

### Proyección:

- **Mes 1-3**: 10 usuarios free (validación)
- **Mes 4-6**: 5 usuarios Pro = $95/mes 💰
- **Mes 7-12**: 50 usuarios Pro = $950/mes 💰💰
- **Año 2**: 200 usuarios Pro + 10 Enterprise = $4,790/mes 💎

**MRR objetivo año 1: $500-1000/mes**

---

## 🛠️ STACK FINAL RECOMENDADO

```yaml
Frontend:
  framework: Next.js 14 (App Router)
  styling: Tailwind CSS
  charts: Chart.js / Recharts
  deployment: Vercel ($0 hobby tier)

Backend:
  api: FastAPI (Python)
  auth: Supabase Auth
  deployment: Railway ($5-20/mes)

Database:
  primary: Supabase PostgreSQL
  cache: Upstash Redis
  
Queue:
  system: BullMQ + Redis
  cron: Railway Cron Jobs

Payments:
  processor: Stripe
  billing: Stripe Customer Portal

Monitoring:
  errors: Sentry
  analytics: Posthog
  uptime: UptimeRobot

Email:
  service: Resend
  templates: React Email
```

**Costo total mensual: $50-100** para empezar
**Puede escalar a 1000 usuarios sin cambiar stack**

---

## ✅ CHECKLIST DE MIGRACIÓN

### Semana 1-2:
- [ ] Crear cuenta Supabase
- [ ] Diseñar schema SQL
- [ ] Migrar datos CSV → PostgreSQL
- [ ] Adaptar rank_tracker.py para usar Supabase
- [ ] Crear API endpoints (FastAPI)

### Semana 3-4:
- [ ] Setup Next.js project
- [ ] Implementar Auth (login/signup)
- [ ] Crear Keywords Manager UI
- [ ] Migrar Dashboard actual
- [ ] Settings page (alertas)

### Semana 5:
- [ ] Setup BullMQ + Redis
- [ ] Crear worker de tracking
- [ ] Cron job diario
- [ ] Sistema de alertas (Telegram/Email)

### Semana 6:
- [ ] Integrar Stripe
- [ ] Crear pricing page
- [ ] Checkout flow
- [ ] Limitar features por plan

### Semana 7-8:
- [ ] Landing page + copywriting
- [ ] SEO básico
- [ ] Onboarding tutorial
- [ ] Documentación API
- [ ] Beta testing con 5-10 usuarios

---

## 🚀 PRÓXIMO PASO

**¿Qué hacemos primero?**

Opción A: **Crear Supabase schema + migración** (más seguro, validar arquitectura)
Opción B: **Frontend MVP rápido** (Next.js + UI, mock data primero)
Opción C: **Hybrid: Dashboard con Supabase** (unir tu dashboard actual con DB real)

**Mi recomendación: Opción C** 
1. Migrar tu dashboard actual a Next.js (2 días)
2. Conectar a Supabase (1 día)
3. Añadir Keywords Manager UI (1 día)
4. Ya tienes MVP funcional → Validar con usuarios beta

¿Empezamos con Supabase setup? Te puedo generar el schema SQL completo ahora mismo.
