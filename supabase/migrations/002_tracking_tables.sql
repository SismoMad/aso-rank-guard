-- ============================================================================
-- Migration 002: Tracking Tables
-- ============================================================================
-- Description: Creates rankings, alerts, alert_history, and subscriptions
-- Author: ASO Rank Guard
-- Date: 2026-01-17
-- Dependencies: 001_initial_schema.sql (profiles, apps, keywords)
-- ============================================================================

-- ============================================================================
-- TABLE: rankings
-- Purpose: Historical ranking data for keywords
-- RLS: Enabled (users can only see rankings for their keywords)
-- Performance: Partitioned by month after reaching 1M rows (future optimization)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.rankings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  keyword_id UUID NOT NULL REFERENCES public.keywords(id) ON DELETE CASCADE,
  rank INT NOT NULL CHECK (rank > 0),
  tracked_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Prevenir duplicados: un ranking por keyword por timestamp
  CONSTRAINT unique_keyword_tracking UNIQUE(keyword_id, tracked_at)
);

-- Índices críticos para performance
CREATE INDEX IF NOT EXISTS idx_rankings_keyword_id ON public.rankings(keyword_id);
CREATE INDEX IF NOT EXISTS idx_rankings_tracked_at ON public.rankings(tracked_at DESC);
CREATE INDEX IF NOT EXISTS idx_rankings_keyword_date ON public.rankings(keyword_id, tracked_at DESC);

-- Comentarios
COMMENT ON TABLE public.rankings IS 'Historical ASO ranking positions for keywords';
COMMENT ON COLUMN public.rankings.rank IS 'App Store ranking position (1-200+)';
COMMENT ON COLUMN public.rankings.tracked_at IS 'When this ranking was captured';

-- ============================================================================
-- TABLE: alerts
-- Purpose: Alert configuration for users
-- RLS: Enabled (users manage their own alerts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  app_id UUID REFERENCES public.apps(id) ON DELETE CASCADE, -- NULL = alertas globales para el user
  keyword_id UUID REFERENCES public.keywords(id) ON DELETE CASCADE, -- NULL = aplica a todas las keywords del app
  
  alert_type TEXT NOT NULL CHECK (alert_type IN (
    'rank_drop',       -- Caída de posición
    'rank_gain',       -- Mejora de posición
    'new_top10',       -- Entró al Top 10
    'lost_top10',      -- Salió del Top 10
    'new_top50',       -- Entró al Top 50
    'lost_top50',      -- Salió del Top 50
    'daily_summary',   -- Resumen diario
    'weekly_report'    -- Reporte semanal
  )),
  
  is_active BOOLEAN NOT NULL DEFAULT true,
  telegram_enabled BOOLEAN NOT NULL DEFAULT true,
  email_enabled BOOLEAN NOT NULL DEFAULT false,
  webhook_enabled BOOLEAN NOT NULL DEFAULT false,
  webhook_url TEXT,
  
  -- Configuración de threshold
  threshold INT CHECK (threshold >= 0), -- e.g., alertar si cae +5 posiciones
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON public.alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_app_id ON public.alerts(app_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON public.alerts(is_active) WHERE is_active = true;

-- Comentarios
COMMENT ON TABLE public.alerts IS 'User-configured alert rules for ranking changes';
COMMENT ON COLUMN public.alerts.threshold IS 'Minimum position change to trigger alert (e.g., 5 = alert if drops/gains 5+ positions)';

-- ============================================================================
-- TABLE: alert_history
-- Purpose: Log of sent alerts
-- RLS: Enabled (users see their own alert history)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.alert_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  alert_id UUID REFERENCES public.alerts(id) ON DELETE SET NULL, -- Mantener histórico si se borra la alerta
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  keyword_id UUID REFERENCES public.keywords(id) ON DELETE SET NULL,
  
  message TEXT NOT NULL,
  channel TEXT NOT NULL CHECK (channel IN ('telegram', 'email', 'webhook')),
  status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending')),
  error_message TEXT,
  
  sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para búsqueda de histórico
CREATE INDEX IF NOT EXISTS idx_alert_history_user_id ON public.alert_history(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_sent_at ON public.alert_history(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_history_status ON public.alert_history(status) WHERE status != 'sent';

-- Comentarios
COMMENT ON TABLE public.alert_history IS 'Historical log of all sent alerts';

-- ============================================================================
-- TABLE: subscriptions
-- Purpose: Stripe subscription management
-- RLS: Enabled (users see only their subscription)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  
  -- Stripe IDs
  stripe_customer_id TEXT UNIQUE,
  stripe_subscription_id TEXT UNIQUE,
  stripe_price_id TEXT, -- e.g., price_1234567890
  
  -- Subscription details
  tier TEXT NOT NULL CHECK (tier IN ('free', 'pro', 'enterprise')),
  status TEXT NOT NULL CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'incomplete')),
  
  -- Billing periods
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at TIMESTAMPTZ,
  canceled_at TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Un usuario solo puede tener una suscripción activa
  CONSTRAINT unique_user_subscription UNIQUE(user_id)
);

-- Índices para Stripe webhooks
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON public.subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription ON public.subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);

-- Comentarios
COMMENT ON TABLE public.subscriptions IS 'Stripe subscription data synced via webhooks';

-- ============================================================================
-- TABLE: tracking_jobs
-- Purpose: Queue tracking for BullMQ job monitoring
-- RLS: Enabled (users see jobs for their apps)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.tracking_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_id UUID NOT NULL REFERENCES public.apps(id) ON DELETE CASCADE,
  
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INT, -- Duración en milisegundos
  
  results_count INT DEFAULT 0, -- Cuántos rankings se capturaron
  error_message TEXT,
  retry_count INT DEFAULT 0,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para monitoreo de jobs
CREATE INDEX IF NOT EXISTS idx_tracking_jobs_app_id ON public.tracking_jobs(app_id);
CREATE INDEX IF NOT EXISTS idx_tracking_jobs_status ON public.tracking_jobs(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tracking_jobs_created_at ON public.tracking_jobs(created_at DESC);

-- Comentarios
COMMENT ON TABLE public.tracking_jobs IS 'BullMQ job queue tracking for ASO rankings';
COMMENT ON COLUMN public.tracking_jobs.duration_ms IS 'Job execution time in milliseconds';

-- ============================================================================
-- TRIGGERS: updated_at auto-update
-- ============================================================================

CREATE TRIGGER set_alerts_updated_at
  BEFORE UPDATE ON public.alerts
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_subscriptions_updated_at
  BEFORE UPDATE ON public.subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- ============================================================================
-- END OF MIGRATION 002
-- ============================================================================
