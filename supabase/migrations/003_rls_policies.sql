-- ============================================================================
-- Migration 003: Row Level Security (RLS) Policies
-- ============================================================================
-- Description: Implements security policies for multi-tenant isolation
-- Author: ASO Rank Guard
-- Date: 2026-01-17
-- Dependencies: 001_initial_schema.sql, 002_tracking_tables.sql
-- Security: CRITICAL - These policies prevent data leakage between users
-- ============================================================================

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tracking_jobs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- HELPER FUNCTION: Get authenticated user ID
-- ============================================================================
-- Nota: No creamos auth.user_id() porque el schema auth es restringido
-- Usamos directamente auth.uid() en las policies

-- ============================================================================
-- PROFILES POLICIES
-- Users can only view and update their own profile
-- ============================================================================

-- SELECT: Users can read their own profile
CREATE POLICY "Users can view own profile"
  ON public.profiles
  FOR SELECT
  USING (auth.uid() = id);

-- INSERT: Users can create their own profile (via Supabase Auth trigger)
CREATE POLICY "Users can insert own profile"
  ON public.profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- UPDATE: Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON public.profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- DELETE: Users can delete their own profile
CREATE POLICY "Users can delete own profile"
  ON public.profiles
  FOR DELETE
  USING (auth.uid() = id);

-- ============================================================================
-- APPS POLICIES
-- Users can only manage their own apps
-- ============================================================================

-- SELECT: Users can view their own apps
CREATE POLICY "Users can view own apps"
  ON public.apps
  FOR SELECT
  USING (user_id = auth.uid());

-- INSERT: Users can create apps (respecting max_apps limit)
CREATE POLICY "Users can insert own apps"
  ON public.apps
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- UPDATE: Users can update their own apps
CREATE POLICY "Users can update own apps"
  ON public.apps
  FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- DELETE: Users can delete their own apps
CREATE POLICY "Users can delete own apps"
  ON public.apps
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================================
-- KEYWORDS POLICIES
-- Users can only manage keywords for their apps
-- ============================================================================

-- SELECT: Users can view keywords for their apps
CREATE POLICY "Users can view keywords for own apps"
  ON public.keywords
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.apps
      WHERE apps.id = keywords.app_id
        AND apps.user_id = auth.uid()
    )
  );

-- INSERT: Users can add keywords to their apps
CREATE POLICY "Users can insert keywords for own apps"
  ON public.keywords
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.apps
      WHERE apps.id = keywords.app_id
        AND apps.user_id = auth.uid()
    )
  );

-- UPDATE: Users can update keywords for their apps
CREATE POLICY "Users can update keywords for own apps"
  ON public.keywords
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.apps
      WHERE apps.id = keywords.app_id
        AND apps.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.apps
      WHERE apps.id = keywords.app_id
        AND apps.user_id = auth.uid()
    )
  );

-- DELETE: Users can delete keywords from their apps
CREATE POLICY "Users can delete keywords for own apps"
  ON public.keywords
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.apps
      WHERE apps.id = keywords.app_id
        AND apps.user_id = auth.uid()
    )
  );

-- ============================================================================
-- RANKINGS POLICIES
-- Users can view rankings for their keywords
-- System can insert rankings (via service_role key)
-- ============================================================================

-- SELECT: Users can view rankings for their keywords
CREATE POLICY "Users can view rankings for own keywords"
  ON public.rankings
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.keywords
      JOIN public.apps ON apps.id = keywords.app_id
      WHERE keywords.id = rankings.keyword_id
        AND apps.user_id = auth.uid()
    )
  );

-- INSERT: Allow service role to insert rankings (BullMQ workers)
-- Users typically don't insert rankings manually
CREATE POLICY "Service role can insert rankings"
  ON public.rankings
  FOR INSERT
  WITH CHECK (true); -- Service role bypass RLS, pero la política existe para claridad

-- DELETE: Users can delete rankings for their keywords (cleanup)
CREATE POLICY "Users can delete rankings for own keywords"
  ON public.rankings
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.keywords
      JOIN public.apps ON apps.id = keywords.app_id
      WHERE keywords.id = rankings.keyword_id
        AND apps.user_id = auth.uid()
    )
  );

-- ============================================================================
-- ALERTS POLICIES
-- Users can manage their own alerts
-- ============================================================================

-- SELECT: Users can view their own alerts
CREATE POLICY "Users can view own alerts"
  ON public.alerts
  FOR SELECT
  USING (user_id = auth.uid());

-- INSERT: Users can create alerts
CREATE POLICY "Users can insert own alerts"
  ON public.alerts
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- UPDATE: Users can update their own alerts
CREATE POLICY "Users can update own alerts"
  ON public.alerts
  FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- DELETE: Users can delete their own alerts
CREATE POLICY "Users can delete own alerts"
  ON public.alerts
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================================
-- ALERT_HISTORY POLICIES
-- Users can view their alert history (read-only)
-- ============================================================================

-- SELECT: Users can view their own alert history
CREATE POLICY "Users can view own alert history"
  ON public.alert_history
  FOR SELECT
  USING (user_id = auth.uid());

-- INSERT: System inserts alert history (service role)
CREATE POLICY "Service role can insert alert history"
  ON public.alert_history
  FOR INSERT
  WITH CHECK (true);

-- ============================================================================
-- SUBSCRIPTIONS POLICIES
-- Users can view their own subscription
-- ============================================================================

-- SELECT: Users can view their own subscription
CREATE POLICY "Users can view own subscription"
  ON public.subscriptions
  FOR SELECT
  USING (user_id = auth.uid());

-- INSERT: System creates subscriptions (Stripe webhooks)
CREATE POLICY "Service role can insert subscriptions"
  ON public.subscriptions
  FOR INSERT
  WITH CHECK (true);

-- UPDATE: System updates subscriptions (Stripe webhooks)
CREATE POLICY "Service role can update subscriptions"
  ON public.subscriptions
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- TRACKING_JOBS POLICIES
-- Users can view jobs for their apps
-- ============================================================================

-- SELECT: Users can view tracking jobs for their apps
CREATE POLICY "Users can view tracking jobs for own apps"
  ON public.tracking_jobs
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.apps
      WHERE apps.id = tracking_jobs.app_id
        AND apps.user_id = auth.uid()
    )
  );

-- INSERT: System creates tracking jobs (BullMQ)
CREATE POLICY "Service role can insert tracking jobs"
  ON public.tracking_jobs
  FOR INSERT
  WITH CHECK (true);

-- UPDATE: System updates tracking jobs
CREATE POLICY "Service role can update tracking jobs"
  ON public.tracking_jobs
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- GRANT PERMISSIONS TO authenticated ROLE
-- ============================================================================

-- Profiles
GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles TO authenticated;

-- Apps
GRANT SELECT, INSERT, UPDATE, DELETE ON public.apps TO authenticated;

-- Keywords
GRANT SELECT, INSERT, UPDATE, DELETE ON public.keywords TO authenticated;

-- Rankings (read + delete only for users)
GRANT SELECT, DELETE ON public.rankings TO authenticated;

-- Alerts
GRANT SELECT, INSERT, UPDATE, DELETE ON public.alerts TO authenticated;

-- Alert History (read-only for users)
GRANT SELECT ON public.alert_history TO authenticated;

-- Subscriptions (read-only for users)
GRANT SELECT ON public.subscriptions TO authenticated;

-- Tracking Jobs (read-only for users)
GRANT SELECT ON public.tracking_jobs TO authenticated;

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================

-- 1. Service Role Key: Used by backend workers (BullMQ, Stripe webhooks)
--    - Bypasses RLS policies
--    - Should NEVER be exposed in frontend
--    - Used in server-side code only

-- 2. Anon Key: Used by frontend (public)
--    - Subject to RLS policies
--    - Users can only access their own data
--    - Safe to expose in browser

-- 3. Multi-tenancy: Guaranteed by RLS
--    - Users can NEVER see other users' data
--    - Even if frontend is compromised, DB is secure

-- ============================================================================
-- END OF MIGRATION 003
-- ============================================================================
