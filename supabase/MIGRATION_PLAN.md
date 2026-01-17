# 🚀 Supabase Migration Plan - ASO Rank Guard

## 📋 Plan de Ejecución Completo

Este documento describe el plan paso a paso para migrar ASO Rank Guard a Supabase PostgreSQL.

---

## ✅ Estado Actual

### Archivos Creados (Guardados Localmente)

- ✅ `supabase/README.md` - Documentación de migraciones
- ✅ `supabase/SCHEMA_DESIGN.md` - Diseño completo de base de datos
- ✅ `supabase/migrations/001_initial_schema.sql` - Tablas base (profiles, apps, keywords)
- ✅ `supabase/migrations/002_tracking_tables.sql` - Tablas de tracking (rankings, alerts, subscriptions)
- ✅ `supabase/migrations/003_rls_policies.sql` - Políticas de seguridad Row Level Security
- ✅ `supabase/migrations/004_functions_triggers.sql` - Funciones y triggers PostgreSQL
- ✅ `supabase/scripts/migrate_csv_to_postgres.py` - Script de migración de datos CSV
- ✅ `.github/copilot-instructions.md` - Mejores prácticas para el proyecto

---

## 📊 Resumen de Migraciones

### Migration 001: Initial Schema
**Tablas:**
- `profiles` - Perfiles de usuario (extiende auth.users)
- `apps` - Aplicaciones móviles a monitorear
- `keywords` - Palabras clave por app

**Features:**
- UUIDs como primary keys
- Triggers para `updated_at`
- Constraints para validación
- Índices optimizados

**Líneas de código:** ~160 líneas SQL

---

### Migration 002: Tracking Tables
**Tablas:**
- `rankings` - Histórico de posiciones (datos principales)
- `alerts` - Configuración de alertas por usuario
- `alert_history` - Log de alertas enviadas
- `subscriptions` - Integración con Stripe
- `tracking_jobs` - Queue de trabajos BullMQ

**Features:**
- Relaciones con ON DELETE CASCADE
- Índices compuestos para performance
- Check constraints para validación
- Unique constraints para prevenir duplicados

**Líneas de código:** ~180 líneas SQL

---

### Migration 003: RLS Policies
**Políticas de Seguridad:**
- 8 tablas con RLS habilitado
- ~32 policies para multi-tenancy
- Separación entre `authenticated` y `service_role`
- Grants específicos por tabla

**Security Features:**
- Users solo ven sus propios datos
- Service role bypass para workers
- Helper function `auth.user_id()`
- Documentación de security notes

**Líneas de código:** ~280 líneas SQL

---

### Migration 004: Functions & Triggers
**Funciones:**
- `handle_new_user()` - Auto-crear profile en signup
- `update_tier_limits()` - Sincronizar límites con subscription
- `get_keyword_trend()` - Calcular tendencia (improving/declining)
- `get_current_rank()`, `get_previous_rank()`, `get_best_rank()`
- `can_add_app()`, `can_add_keyword()` - Validar límites de tier
- `get_app_stats()` - Estadísticas en JSON
- `cleanup_old_rankings()` - Política de retención de datos

**Materialized View:**
- `daily_app_performance` - Resumen diario de rendimiento

**Líneas de código:** ~320 líneas SQL

---

## 🗂️ Datos a Migrar

### Desde config.yaml
- **App:** Audio Bible Stories & Chat (bundle_id: com.biblenow.app)
- **Keywords:** 82 palabras clave
- **País:** US
- **Alertas:** Configuración de Telegram

### Desde data/ranks.csv
- **Registros:** 333 rankings
- **Fechas:** Múltiples fechas de tracking
- **Formato:** `date,keyword,country,rank,app_id`

---

## 🔄 Orden de Ejecución (CRÍTICO)

### Paso 1: Conectar a Supabase
```bash
# Necesitarás:
# - SUPABASE_URL (tu proyecto)
# - SUPABASE_SERVICE_ROLE_KEY (para aplicar migraciones)
```

### Paso 2: Aplicar Migraciones (EN ORDEN)
```bash
# 1. Initial Schema
mcp_supabase_apply_migration(
  name="initial_schema",
  query=<contenido de 001_initial_schema.sql>
)

# 2. Tracking Tables
mcp_supabase_apply_migration(
  name="tracking_tables",
  query=<contenido de 002_tracking_tables.sql>
)

# 3. RLS Policies
mcp_supabase_apply_migration(
  name="rls_policies",
  query=<contenido de 003_rls_policies.sql>
)

# 4. Functions & Triggers
mcp_supabase_apply_migration(
  name="functions_triggers",
  query=<contenido de 004_functions_triggers.sql>
)
```

### Paso 3: Verificar Schema
```bash
# Listar tablas creadas
mcp_supabase_list_tables(schemas=["public"])

# Verificar extensiones
mcp_supabase_list_extensions()

# Revisar advisors (security checks)
mcp_supabase_get_advisors(type="security")
```

### Paso 4: Crear Usuario (ANTES de migrar datos)
```bash
# En Supabase Dashboard:
# 1. Authentication > Users > Add User
# 2. Email: tu_email@example.com
# 3. Password: (temporal)
# 4. Confirmar email

# O via Supabase CLI:
supabase auth signup --email tu_email@example.com
```

### Paso 5: Migrar Datos CSV
```bash
# Instalar dependencias
pip install supabase pandas python-dotenv

# Configurar .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
USER_EMAIL=tu_email@example.com

# Ejecutar migración
python3 supabase/scripts/migrate_csv_to_postgres.py \
  --email tu_email@example.com
```

### Paso 6: Generar TypeScript Types
```bash
mcp_supabase_generate_typescript_types()
```

### Paso 7: Verificar Datos
```sql
-- Verificar que los datos se insertaron correctamente
SELECT COUNT(*) FROM profiles;  -- Debería ser 1
SELECT COUNT(*) FROM apps;      -- Debería ser 1
SELECT COUNT(*) FROM keywords;  -- Debería ser 82
SELECT COUNT(*) FROM rankings;  -- Debería ser ~333
SELECT COUNT(*) FROM alerts;    -- Debería ser 2-3
```

---

## 🧪 Testing de RLS (CRÍTICO)

### Test 1: Usuarios solo ven sus datos
```sql
-- Simular usuario 1
SET request.jwt.claims = '{"sub": "user-1-uuid"}';
SELECT * FROM apps; -- Debería mostrar solo apps de user-1

-- Simular usuario 2
SET request.jwt.claims = '{"sub": "user-2-uuid"}';
SELECT * FROM apps; -- Debería mostrar solo apps de user-2 (o vacío)
```

### Test 2: Service Role bypasses RLS
```sql
-- Service role puede ver TODO
RESET request.jwt.claims;
SELECT * FROM apps; -- Muestra todas las apps
```

---

## 📦 Próximos Pasos (Después de Migración)

### Fase 1: Backend API (FastAPI)
- [ ] Crear endpoints REST con Supabase client
- [ ] Implementar autenticación JWT
- [ ] Rate limiting por tier
- [ ] Error handling y logging

### Fase 2: Frontend (Next.js)
- [ ] Setup Next.js 14 con App Router
- [ ] Integrar Supabase Auth
- [ ] Dashboard con Chart.js
- [ ] Keywords manager (CRUD)
- [ ] Settings page

### Fase 3: Workers (BullMQ)
- [ ] Queue de tracking automático
- [ ] Worker para scraping de rankings
- [ ] Alert sender (Telegram/Email)
- [ ] Cleanup job (retention policy)

### Fase 4: Payments (Stripe)
- [ ] Checkout session
- [ ] Webhook handler (subscription updates)
- [ ] Customer portal
- [ ] Usage-based limits

---

## 🚨 Troubleshooting

### Error: "permission denied for table profiles"
**Solución:** Verifica que usaste `SUPABASE_SERVICE_ROLE_KEY` (NO anon key)

### Error: "relation does not exist"
**Solución:** Aplica las migraciones en orden (001 → 002 → 003 → 004)

### Error: "duplicate key value violates unique constraint"
**Solución:** Ya existen datos, usa `UPSERT` o limpia la tabla primero

### Error: "function auth.uid() does not exist"
**Solución:** RLS policy mal escrita, usa `auth.uid()` correctamente

---

## 📊 Métricas de Éxito

Al completar la migración, deberías tener:

- ✅ 8 tablas creadas
- ✅ 32 RLS policies activas
- ✅ 10+ funciones PostgreSQL
- ✅ 1 materialized view
- ✅ 82 keywords migradas
- ✅ ~333 rankings históricos
- ✅ 0 errores de seguridad (advisors)
- ✅ TypeScript types generados

---

## 🔗 Referencias

- **Supabase Docs:** https://supabase.com/docs
- **RLS Guide:** https://supabase.com/docs/guides/auth/row-level-security
- **PostgreSQL Functions:** https://www.postgresql.org/docs/current/sql-createfunction.html
- **Schema Design:** Ver `supabase/SCHEMA_DESIGN.md`
- **Copilot Instructions:** Ver `.github/copilot-instructions.md`

---

## 📞 Contacto

Si tienes problemas durante la migración:
1. Revisa los logs de Supabase Dashboard
2. Consulta `mcp_supabase_get_logs(service="postgres")`
3. Verifica advisors: `mcp_supabase_get_advisors(type="security")`

---

**¿Listo para comenzar?** 🚀

Ejecuta: `mcp_supabase_apply_migration` con la primera migración (001_initial_schema.sql)
