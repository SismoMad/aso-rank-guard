# 🗄️ ASO Rank Guard - Database Schema Design

## 📊 Modelo de Datos

### 🎯 Principios de Diseño

1. **Multi-tenant**: Un usuario puede tener múltiples apps
2. **Normalización**: Evitar redundancia de datos
3. **RLS (Row Level Security)**: Seguridad a nivel de fila
4. **Auditoría**: created_at, updated_at en todas las tablas
5. **Performance**: Índices en foreign keys y columnas de búsqueda

---

## 📋 Tablas Principales

### 1. **users** (autenticación Supabase)
```sql
-- Gestionada automáticamente por Supabase Auth
-- Usamos auth.users para autenticación
-- Extendemos con public.profiles
```

### 2. **profiles** (extensión de users)
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  company TEXT,
  subscription_tier TEXT DEFAULT 'free', -- free, pro, enterprise
  subscription_status TEXT DEFAULT 'active',
  trial_ends_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Datos actuales:** 1 usuario (tú)

---

### 3. **apps** (aplicaciones a monitorear)
```sql
CREATE TABLE apps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  bundle_id TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('ios', 'android')),
  country TEXT NOT NULL DEFAULT 'ES',
  category TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, bundle_id, platform, country)
);
```

**Datos actuales:** 
- 1 app: "Heylog" (com.heylog.app)
- Plataforma: iOS
- País: ES

---

### 4. **keywords** (palabras clave a trackear)
```sql
CREATE TABLE keywords (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,
  volume INT, -- búsquedas mensuales estimadas
  difficulty INT CHECK (difficulty BETWEEN 0 AND 100),
  is_active BOOLEAN DEFAULT true,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(app_id, keyword)
);
```

**Datos actuales:** 82 keywords del config.yaml

---

### 5. **rankings** (histórico de posiciones)
```sql
CREATE TABLE rankings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  keyword_id UUID REFERENCES keywords(id) ON DELETE CASCADE,
  rank INT NOT NULL,
  tracked_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Índice compuesto para queries rápidas
  CONSTRAINT unique_keyword_date UNIQUE(keyword_id, tracked_at)
);

CREATE INDEX idx_rankings_keyword_date ON rankings(keyword_id, tracked_at DESC);
CREATE INDEX idx_rankings_tracked_at ON rankings(tracked_at DESC);
```

**Datos actuales:** 249 registros del CSV (3 fechas × 82 keywords)

---

### 6. **alerts** (configuración de alertas)
```sql
CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL CHECK (alert_type IN ('rank_drop', 'rank_gain', 'new_top10', 'lost_top10', 'daily_summary')),
  is_active BOOLEAN DEFAULT true,
  telegram_enabled BOOLEAN DEFAULT true,
  email_enabled BOOLEAN DEFAULT false,
  threshold INT, -- e.g., alertar si cae +5 posiciones
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Configuración actual:** Alertas Telegram habilitadas

---

### 7. **alert_history** (histórico de alertas enviadas)
```sql
CREATE TABLE alert_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
  keyword_id UUID REFERENCES keywords(id) ON DELETE SET NULL,
  message TEXT NOT NULL,
  channel TEXT NOT NULL, -- telegram, email
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'sent' -- sent, failed, pending
);
```

---

### 8. **subscriptions** (facturación Stripe)
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  stripe_customer_id TEXT UNIQUE,
  stripe_subscription_id TEXT UNIQUE,
  tier TEXT NOT NULL, -- free, pro, enterprise
  status TEXT NOT NULL, -- active, canceled, past_due
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 9. **tracking_jobs** (cola de trabajos BullMQ)
```sql
CREATE TABLE tracking_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  error_message TEXT,
  results_count INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tracking_jobs_status ON tracking_jobs(status, created_at DESC);
```

---

## 🔗 Relaciones

```
profiles (1) ──┬─→ apps (N)
               ├─→ alerts (N)
               └─→ subscriptions (1)

apps (1) ──┬─→ keywords (N)
           ├─→ alerts (N)
           └─→ tracking_jobs (N)

keywords (1) ──→ rankings (N)

alerts (1) ──→ alert_history (N)
```

---

## 📈 Migración de Datos CSV Actuales

### Mapping CSV → PostgreSQL

**data/ranks.csv** (249 rows):
```csv
keyword,date,rank
diario de viaje,2026-01-13,149
```

**Transformación:**
1. Insertar user profile (tu cuenta)
2. Insertar app "Heylog"
3. Insertar 82 keywords desde config.yaml
4. Insertar rankings agrupando por (keyword, date)

**Script:** `supabase/scripts/migrate_csv_to_postgres.py`

---

## 🔒 Límites por Tier

| Feature | Free | Pro ($19) | Enterprise ($99) |
|---------|------|-----------|------------------|
| Apps | 1 | 5 | 50 |
| Keywords/app | 50 | 500 | Unlimited |
| Tracking frequency | Daily | 4x/day | Hourly |
| Alert channels | Telegram | +Email | +Slack, Webhook |
| History retention | 30 días | 1 año | Unlimited |

---

## 📊 Estimaciones de Storage

**Datos actuales:**
- 82 keywords × 365 días = ~30k rankings/año
- Storage: ~2MB/año

**Proyección (100 usuarios Pro):**
- 100 users × 5 apps × 500 keywords × 4 checks/day × 365 days = 365M rankings/año
- Storage: ~15GB/año (optimizado con particiones)

**Recomendación:** Particionar tabla `rankings` por mes después de 1M registros
