-- ============================================================================
-- Migration 004: Database Functions & Triggers
-- ============================================================================
-- Description: Helper functions, stats calculations, and automated triggers
-- Author: ASO Rank Guard
-- Date: 2026-01-17
-- Dependencies: All previous migrations
-- ============================================================================

-- ============================================================================
-- FUNCTION: Auto-create profile on user signup
-- Trigger: After INSERT on auth.users
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger en auth.users (sistema Supabase)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- FUNCTION: Update tier limits when subscription changes
-- ============================================================================

CREATE OR REPLACE FUNCTION public.update_tier_limits()
RETURNS TRIGGER AS $$
BEGIN
  -- Actualizar límites según tier
  UPDATE public.profiles
  SET
    subscription_tier = NEW.tier,
    subscription_status = NEW.status,
    max_apps = CASE NEW.tier
      WHEN 'free' THEN 1
      WHEN 'pro' THEN 5
      WHEN 'enterprise' THEN 50
      ELSE 1
    END,
    max_keywords_per_app = CASE NEW.tier
      WHEN 'free' THEN 50
      WHEN 'pro' THEN 500
      WHEN 'enterprise' THEN 10000
      ELSE 50
    END,
    trial_ends_at = NEW.trial_end
  WHERE id = NEW.user_id;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger en subscriptions
DROP TRIGGER IF EXISTS on_subscription_change ON public.subscriptions;
CREATE TRIGGER on_subscription_change
  AFTER INSERT OR UPDATE ON public.subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_tier_limits();

-- ============================================================================
-- FUNCTION: Calculate ranking trend (last 7 days)
-- Returns: 'improving', 'declining', 'stable', 'new'
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_keyword_trend(p_keyword_id UUID)
RETURNS TEXT AS $$
DECLARE
  recent_avg NUMERIC;
  previous_avg NUMERIC;
  diff NUMERIC;
BEGIN
  -- Promedio de rankings últimos 3 días
  SELECT AVG(rank) INTO recent_avg
  FROM public.rankings
  WHERE keyword_id = p_keyword_id
    AND tracked_at > NOW() - INTERVAL '3 days';
  
  -- Promedio de rankings días 4-7
  SELECT AVG(rank) INTO previous_avg
  FROM public.rankings
  WHERE keyword_id = p_keyword_id
    AND tracked_at BETWEEN NOW() - INTERVAL '7 days' AND NOW() - INTERVAL '3 days';
  
  -- Si no hay datos previos, es nueva
  IF previous_avg IS NULL THEN
    RETURN 'new';
  END IF;
  
  -- Calcular diferencia
  diff := recent_avg - previous_avg;
  
  -- Tendencia (menor rank = mejor posición)
  IF diff <= -3 THEN
    RETURN 'improving';
  ELSIF diff >= 3 THEN
    RETURN 'declining';
  ELSE
    RETURN 'stable';
  END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FUNCTION: Get current rank for keyword
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_current_rank(p_keyword_id UUID)
RETURNS INT AS $$
  SELECT rank
  FROM public.rankings
  WHERE keyword_id = p_keyword_id
  ORDER BY tracked_at DESC
  LIMIT 1;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- FUNCTION: Get previous rank (yesterday)
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_previous_rank(p_keyword_id UUID)
RETURNS INT AS $$
  SELECT rank
  FROM public.rankings
  WHERE keyword_id = p_keyword_id
    AND tracked_at < NOW() - INTERVAL '1 day'
  ORDER BY tracked_at DESC
  LIMIT 1;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- FUNCTION: Get best rank ever for keyword
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_best_rank(p_keyword_id UUID)
RETURNS INT AS $$
  SELECT MIN(rank)
  FROM public.rankings
  WHERE keyword_id = p_keyword_id;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- FUNCTION: Get worst rank in last 30 days
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_worst_rank_30d(p_keyword_id UUID)
RETURNS INT AS $$
  SELECT MAX(rank)
  FROM public.rankings
  WHERE keyword_id = p_keyword_id
    AND tracked_at > NOW() - INTERVAL '30 days';
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- FUNCTION: Check if user can add more apps (tier limit)
-- ============================================================================

CREATE OR REPLACE FUNCTION public.can_add_app(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  current_count INT;
  max_allowed INT;
BEGIN
  -- Contar apps actuales
  SELECT COUNT(*) INTO current_count
  FROM public.apps
  WHERE user_id = p_user_id AND is_active = true;
  
  -- Obtener límite del tier
  SELECT max_apps INTO max_allowed
  FROM public.profiles
  WHERE id = p_user_id;
  
  RETURN current_count < max_allowed;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FUNCTION: Check if user can add more keywords to app
-- ============================================================================

CREATE OR REPLACE FUNCTION public.can_add_keyword(p_app_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  current_count INT;
  max_allowed INT;
  v_user_id UUID;
BEGIN
  -- Obtener user_id del app
  SELECT user_id INTO v_user_id
  FROM public.apps
  WHERE id = p_app_id;
  
  -- Contar keywords actuales para esta app
  SELECT COUNT(*) INTO current_count
  FROM public.keywords
  WHERE app_id = p_app_id AND is_active = true;
  
  -- Obtener límite del tier
  SELECT max_keywords_per_app INTO max_allowed
  FROM public.profiles
  WHERE id = v_user_id;
  
  RETURN current_count < max_allowed;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FUNCTION: Get app statistics
-- Returns JSON with rankings stats for an app
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_app_stats(p_app_id UUID)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_keywords', COUNT(DISTINCT k.id),
    'active_keywords', COUNT(DISTINCT k.id) FILTER (WHERE k.is_active = true),
    'top10_count', COUNT(DISTINCT k.id) FILTER (WHERE r.rank <= 10),
    'top50_count', COUNT(DISTINCT k.id) FILTER (WHERE r.rank <= 50),
    'avg_rank', ROUND(AVG(r.rank)::numeric, 1),
    'best_rank', MIN(r.rank),
    'last_tracked', MAX(r.tracked_at)
  ) INTO result
  FROM public.keywords k
  LEFT JOIN LATERAL (
    SELECT rank, tracked_at
    FROM public.rankings
    WHERE keyword_id = k.id
    ORDER BY tracked_at DESC
    LIMIT 1
  ) r ON true
  WHERE k.app_id = p_app_id;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FUNCTION: Delete old rankings (data retention policy)
-- For free tier: keep last 30 days
-- For pro tier: keep last 365 days
-- For enterprise: keep all
-- ============================================================================

CREATE OR REPLACE FUNCTION public.cleanup_old_rankings()
RETURNS INT AS $$
DECLARE
  deleted_count INT := 0;
BEGIN
  -- Eliminar rankings antiguos según tier del usuario
  WITH apps_with_retention AS (
    SELECT 
      a.id as app_id,
      CASE p.subscription_tier
        WHEN 'free' THEN NOW() - INTERVAL '30 days'
        WHEN 'pro' THEN NOW() - INTERVAL '365 days'
        WHEN 'enterprise' THEN '1970-01-01'::timestamptz -- Mantener todo
      END as retention_date
    FROM public.apps a
    JOIN public.profiles p ON p.id = a.user_id
  )
  DELETE FROM public.rankings r
  USING public.keywords k, apps_with_retention awr
  WHERE r.keyword_id = k.id
    AND k.app_id = awr.app_id
    AND r.tracked_at < awr.retention_date;
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: Calculate job duration and update results
-- ============================================================================

CREATE OR REPLACE FUNCTION public.complete_tracking_job()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
    NEW.completed_at := NOW();
    NEW.duration_ms := EXTRACT(EPOCH FROM (NOW() - NEW.started_at)) * 1000;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger en tracking_jobs
DROP TRIGGER IF EXISTS on_tracking_job_complete ON public.tracking_jobs;
CREATE TRIGGER on_tracking_job_complete
  BEFORE UPDATE ON public.tracking_jobs
  FOR EACH ROW
  EXECUTE FUNCTION public.complete_tracking_job();

-- ============================================================================
-- MATERIALIZED VIEW: Daily app performance summary (opcional, para performance)
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS public.daily_app_performance AS
SELECT 
  k.app_id,
  DATE(r.tracked_at) as tracking_date,
  COUNT(DISTINCT k.id) as total_keywords,
  AVG(r.rank) as avg_rank,
  MIN(r.rank) as best_rank,
  MAX(r.rank) as worst_rank,
  COUNT(*) FILTER (WHERE r.rank <= 10) as top10_count,
  COUNT(*) FILTER (WHERE r.rank <= 50) as top50_count,
  COUNT(*) FILTER (WHERE r.rank <= 100) as top100_count
FROM public.rankings r
JOIN public.keywords k ON k.id = r.keyword_id
GROUP BY k.app_id, DATE(r.tracked_at)
ORDER BY k.app_id, tracking_date DESC;

-- Índice para queries rápidas
CREATE INDEX IF NOT EXISTS idx_daily_performance_app_date 
  ON public.daily_app_performance(app_id, tracking_date DESC);

-- Función para refrescar la vista (ejecutar en cron job)
CREATE OR REPLACE FUNCTION public.refresh_daily_performance()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.daily_app_performance;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS: Permitir ejecutar funciones a usuarios autenticados
-- ============================================================================

GRANT EXECUTE ON FUNCTION public.get_keyword_trend(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_current_rank(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_previous_rank(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_best_rank(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_worst_rank_30d(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.can_add_app(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.can_add_keyword(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_app_stats(UUID) TO authenticated;

-- Solo service role puede ejecutar cleanup
GRANT EXECUTE ON FUNCTION public.cleanup_old_rankings() TO service_role;
GRANT EXECUTE ON FUNCTION public.refresh_daily_performance() TO service_role;

-- ============================================================================
-- END OF MIGRATION 004
-- ============================================================================
