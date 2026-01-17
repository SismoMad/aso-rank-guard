# ASO Rank Guard - Copilot Instructions

You are working on **ASO Rank Guard**, a SaaS platform for App Store Optimization (ASO) ranking tracking and analytics.

## 🎯 Project Context

**Tech Stack:**
- **Backend:** Python 3.8+, FastAPI, Supabase PostgreSQL
- **Frontend:** Next.js 14, React, TypeScript, TailwindCSS
- **Database:** Supabase PostgreSQL with Row Level Security (RLS)
- **Queue:** BullMQ with Redis for background jobs
- **Payments:** Stripe for subscriptions
- **Deployment:** Vercel (frontend), Railway/Render (backend workers)

**Current State:** Migrating from local CSV-based script to multi-tenant SaaS

---

## 🏗️ Architecture Principles

### 1. Multi-Tenancy
- **RLS is CRITICAL**: Every table must have Row Level Security policies
- Users can NEVER see other users' data
- Use `user_id` foreign keys consistently
- Test queries with different user contexts

### 2. Security Best Practices
- **NEVER** expose `SUPABASE_SERVICE_ROLE_KEY` in frontend
- Use `SUPABASE_ANON_KEY` for client-side code
- All sensitive operations use service role on backend only
- Validate input on both client and server
- Use parameterized queries (avoid SQL injection)

### 3. Database Conventions
- **Tables:** `snake_case` (e.g., `tracking_jobs`)
- **Columns:** `snake_case` (e.g., `created_at`)
- All tables have: `id`, `created_at`, `updated_at`
- Use `UUID` for primary keys (not integers)
- Foreign keys: `ON DELETE CASCADE` for owned relationships
- Indexes on all foreign keys and frequently queried columns

### 4. API Design
- RESTful endpoints: `/api/apps`, `/api/keywords/{id}`
- Use HTTP methods correctly: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- Return proper status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)
- Include error messages: `{ "error": "message" }`
- Paginate large results: `?page=1&limit=50`

### 5. Code Quality
- **Type safety:** Use TypeScript types from Supabase schema
- **Error handling:** Try/catch with meaningful messages
- **Logging:** Use structured logging (JSON format)
- **Testing:** Write tests for critical paths (auth, payments, RLS)
- **Comments:** Document WHY, not WHAT (code should be self-explanatory)

---

## 📁 File Organization

```
aso-rank-guard/
├── supabase/
│   ├── migrations/          # SQL migrations (versioned)
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_tracking_tables.sql
│   │   ├── 003_rls_policies.sql
│   │   └── 004_functions_triggers.sql
│   ├── scripts/             # Data migration scripts
│   └── SCHEMA_DESIGN.md     # Database documentation
├── src/                     # Python backend (legacy)
├── config/
│   └── config.yaml          # DO NOT COMMIT (use .example)
├── data/                    # CSV files (being deprecated)
└── web/                     # Next.js frontend (future)
```

---

## 🔒 Supabase Specific Guidelines

### RLS Policies Pattern
```sql
-- Always enable RLS
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own data"
  ON my_table
  FOR SELECT
  USING (user_id = auth.uid());

-- Service role can do anything (for workers)
-- No policy needed - service_role bypasses RLS
```

### Using Supabase Client (TypeScript)
```typescript
// ✅ CORRECT: Client-side (uses anon key + RLS)
import { createBrowserClient } from '@supabase/ssr'

const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// ✅ CORRECT: Server-side (service role for admin operations)
import { createClient } from '@supabase/supabase-js'

const supabaseAdmin = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!, // ⚠️ NEVER in frontend!
  { auth: { autoRefreshToken: false, persistSession: false } }
)
```

### Common Queries
```typescript
// Fetch user's apps
const { data: apps } = await supabase
  .from('apps')
  .select('*')
  .eq('user_id', user.id)

// Fetch keywords with rankings (JOIN)
const { data: keywords } = await supabase
  .from('keywords')
  .select(`
    *,
    rankings:rankings(rank, tracked_at)
  `)
  .eq('app_id', appId)
  .order('rankings.tracked_at', { ascending: false })
```

---

## 🚫 Common Pitfalls to Avoid

### ❌ DON'T: Forget RLS policies
```sql
-- Missing RLS = users can see ALL data!
CREATE TABLE apps (...);  -- ❌ No RLS enabled
```

### ✅ DO: Always enable RLS
```sql
CREATE TABLE apps (...);
ALTER TABLE apps ENABLE ROW LEVEL SECURITY;
CREATE POLICY "..." ON apps FOR SELECT USING (user_id = auth.uid());
```

---

### ❌ DON'T: Use integer IDs in multi-tenant systems
```sql
CREATE TABLE apps (
  id SERIAL PRIMARY KEY  -- ❌ Predictable, sequential
);
```

### ✅ DO: Use UUIDs for security
```sql
CREATE TABLE apps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4()  -- ✅ Unpredictable
);
```

---

### ❌ DON'T: Expose service role key
```typescript
// ❌ CRITICAL SECURITY VULNERABILITY
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY // ❌ In frontend = game over
)
```

### ✅ DO: Use anon key in frontend
```typescript
// ✅ Safe for public use
const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY! // ✅ Protected by RLS
)
```

---

### ❌ DON'T: Hardcode limits in queries
```typescript
// ❌ What if user upgrades to Pro?
const maxKeywords = 50; // Free tier limit
```

### ✅ DO: Check limits from database
```typescript
// ✅ Dynamic based on subscription tier
const { data: profile } = await supabase
  .from('profiles')
  .select('max_keywords_per_app')
  .eq('id', userId)
  .single();

const canAdd = keywordCount < profile.max_keywords_per_app;
```

---

### ❌ DON'T: Forget to handle errors
```typescript
// ❌ Silent failure
const { data } = await supabase.from('apps').insert(newApp);
```

### ✅ DO: Always check for errors
```typescript
// ✅ Proper error handling
const { data, error } = await supabase.from('apps').insert(newApp);

if (error) {
  console.error('Failed to create app:', error.message);
  throw new Error('Could not create app');
}
```

---

## 📊 Performance Guidelines

### Indexing Strategy
- Index all foreign keys: `CREATE INDEX idx_apps_user_id ON apps(user_id)`
- Index frequently filtered columns: `WHERE is_active = true`
- Composite indexes for common queries: `(user_id, created_at DESC)`
- Don't over-index (slows down writes)

### Query Optimization
- Use `select()` with specific columns (not `select('*')`)
- Limit results with `.limit(100)`
- Use pagination for large datasets
- Aggregate in database (not in application code)

### Caching
- Cache static data: country lists, tier limits
- Use Redis for session data
- Cache Supabase schema types (regenerate on migrations)

---

## 🎨 Frontend Best Practices

### Component Structure
```typescript
// ✅ Server Component (default in Next.js 14)
export default async function DashboardPage() {
  const supabase = createServerClient(...)
  const { data } = await supabase.from('apps').select('*')
  return <AppList apps={data} />
}

// ✅ Client Component (interactive)
'use client'
export function KeywordForm() {
  const [keyword, setKeyword] = useState('')
  // ... interactive logic
}
```

### Data Fetching
- **Server Components**: Fetch in component, no loading state needed
- **Client Components**: Use `useSWR` or `useQuery` for caching
- **Realtime**: Use Supabase subscriptions for live updates

---

## 🧪 Testing Guidelines

### What to Test
1. **RLS Policies**: Different users can't access each other's data
2. **Tier Limits**: Free users can't exceed keyword limits
3. **Edge Cases**: Empty states, max limits, deleted data
4. **Critical Paths**: Signup, subscription creation, ranking import

### Test Example (RLS)
```sql
-- Set user context
SET request.jwt.claims = '{"sub": "user-123"}';

-- This should return data
SELECT * FROM apps WHERE user_id = 'user-123';

-- This should return nothing (different user)
SELECT * FROM apps WHERE user_id = 'user-456';
```

---

## 🔄 Migration Workflow

1. **Write migration locally**: `supabase/migrations/NNN_description.sql`
2. **Review SQL carefully**: Check for breaking changes
3. **Test on dev branch**: Use Supabase branching
4. **Apply via MCP**: `mcp_supabase_apply_migration`
5. **Verify**: Check tables, policies, functions
6. **Generate types**: `mcp_supabase_generate_typescript_types`
7. **Update code**: Use new types in frontend/backend

---

## 📝 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(keywords): Add bulk import from CSV

- Upload CSV file via UI
- Parse and validate keywords
- Check tier limits before import
- Show progress during upload

Closes #42
```

---

## 🚀 Deployment Checklist

- [ ] Environment variables set in Vercel/Railway
- [ ] Database migrations applied to production
- [ ] RLS policies tested with real users
- [ ] Stripe webhooks configured
- [ ] Error tracking enabled (Sentry)
- [ ] Analytics configured (PostHog/Mixpanel)
- [ ] Backup strategy in place
- [ ] Health check endpoint responding
- [ ] SSL/HTTPS enabled
- [ ] Rate limiting configured

---

## 🆘 When You Need Help

1. **Database schema questions**: Check `supabase/SCHEMA_DESIGN.md`
2. **API questions**: Check Supabase docs `mcp_supabase_search_docs`
3. **Best practices**: Re-read this file
4. **Debugging RLS**: Set `log_statement = 'all'` in PostgreSQL
5. **Performance issues**: Use `EXPLAIN ANALYZE` on slow queries

---

## 🎯 Current Development Focus

**Phase 1** (Current): Database Migration
- ✅ Create SQL migrations
- ⏳ Apply migrations to Supabase
- ⏳ Migrate CSV data to PostgreSQL
- ⏳ Test RLS policies

**Phase 2** (Next): Frontend Development
- Build Next.js dashboard
- Keywords manager UI
- Settings page with Stripe integration
- Realtime ranking updates

**Phase 3** (Future): Production Launch
- BullMQ workers for automated tracking
- Landing page + marketing site
- Beta user onboarding
- Payment processing

---

## 💡 Remember

- **Security first**: RLS is your safety net
- **User experience**: Fast, intuitive, reliable
- **Scalability**: Design for 1000+ users from day one
- **Documentation**: Future you will thank present you
- **Test thoroughly**: Especially payments and data access

---

**Last Updated:** 2026-01-17
**Maintainer:** @javi
**Project Status:** Active Development
