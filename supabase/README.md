# Supabase Database Migrations

Este directorio contiene todas las migraciones de base de datos para ASO Rank Guard.

## 📁 Estructura

```
supabase/
├── migrations/           # Migraciones SQL (guardadas localmente)
│   ├── 001_initial_schema.sql
│   ├── 002_tracking_tables.sql
│   ├── 003_rls_policies.sql
│   └── 004_functions_triggers.sql
├── seed/                 # Datos de prueba
└── scripts/             # Scripts de migración de datos
```

## 🔄 Orden de Ejecución

Las migraciones deben aplicarse en este orden:

1. **001_initial_schema.sql** - Tablas base (users, apps, keywords)
2. **002_tracking_tables.sql** - Tablas de tracking (rankings, alerts, subscriptions)
3. **003_rls_policies.sql** - Row Level Security policies
4. **004_functions_triggers.sql** - Funciones PostgreSQL y triggers

## 📝 Convenciones

- Todas las migraciones están en SQL puro
- Se guardan localmente ANTES de aplicarse
- Nomenclatura: `NNN_descripcion.sql` (3 dígitos + snake_case)
- Cada migración debe ser idempotente cuando sea posible
- Incluir rollback cuando sea relevante

## 🚀 Aplicar Migraciones

Las migraciones se aplican usando Supabase MCP tools:

```bash
# Ejemplo (via MCP)
mcp_supabase_apply_migration --name="initial_schema" --query="$(cat 001_initial_schema.sql)"
```

## 🔐 Seguridad

- **NUNCA** incluir credenciales en migraciones
- Usar variables de entorno para secrets
- RLS activado en TODAS las tablas de usuarios
- Policies restrictivas por defecto
