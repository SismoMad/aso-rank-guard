-- ============================================================================
-- Migration 001: Initial Schema - Base Tables
-- ============================================================================
-- Description: Creates core tables (profiles, apps, keywords)
-- Author: ASO Rank Guard
-- Date: 2026-01-17
-- Dependencies: Supabase Auth (auth.users must exist)
-- ============================================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: profiles
-- Purpose: Extends Supabase auth.users with additional profile data
-- RLS: Enabled (users can only see/edit their own profile)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  company TEXT,
  subscription_tier TEXT NOT NULL DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
  subscription_status TEXT NOT NULL DEFAULT 'active' CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled')),
  trial_ends_at TIMESTAMPTZ,
  max_apps INT NOT NULL DEFAULT 1, -- Límite según tier
  max_keywords_per_app INT NOT NULL DEFAULT 50, -- Límite según tier
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_subscription_tier ON public.profiles(subscription_tier);

-- Comentarios para documentación
COMMENT ON TABLE public.profiles IS 'User profiles extending Supabase auth.users';
COMMENT ON COLUMN public.profiles.subscription_tier IS 'Subscription level: free, pro, enterprise';
COMMENT ON COLUMN public.profiles.max_apps IS 'Maximum number of apps allowed for this user';

-- ============================================================================
-- TABLE: apps
-- Purpose: Applications being monitored for ASO
-- RLS: Enabled (users can only see their own apps)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.apps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  bundle_id TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('ios', 'android')),
  country TEXT NOT NULL DEFAULT 'ES' CHECK (length(country) = 2), -- ISO 3166-1 alpha-2
  category TEXT,
  icon_url TEXT,
  app_store_url TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Prevenir duplicados: mismo bundle_id + platform + country por usuario
  CONSTRAINT unique_user_app UNIQUE(user_id, bundle_id, platform, country)
);

-- Índices para búsquedas y JOIN frecuentes
CREATE INDEX IF NOT EXISTS idx_apps_user_id ON public.apps(user_id);
CREATE INDEX IF NOT EXISTS idx_apps_bundle_id ON public.apps(bundle_id);
CREATE INDEX IF NOT EXISTS idx_apps_is_active ON public.apps(is_active) WHERE is_active = true;

-- Comentarios
COMMENT ON TABLE public.apps IS 'Mobile applications being tracked for ASO rankings';
COMMENT ON COLUMN public.apps.bundle_id IS 'iOS: com.company.app, Android: com.company.app';
COMMENT ON COLUMN public.apps.country IS 'ISO 3166-1 alpha-2 country code (e.g., ES, US, GB)';

-- ============================================================================
-- TABLE: keywords
-- Purpose: Keywords to track for each app
-- RLS: Enabled (users can only see keywords for their apps)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.keywords (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_id UUID NOT NULL REFERENCES public.apps(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,
  volume INT CHECK (volume >= 0), -- Búsquedas mensuales estimadas
  difficulty INT CHECK (difficulty BETWEEN 0 AND 100), -- Dificultad SEO (0-100)
  is_active BOOLEAN NOT NULL DEFAULT true,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Prevenir duplicados: misma keyword por app
  CONSTRAINT unique_app_keyword UNIQUE(app_id, keyword)
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_keywords_app_id ON public.keywords(app_id);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON public.keywords(keyword); -- Para búsqueda de texto
CREATE INDEX IF NOT EXISTS idx_keywords_is_active ON public.keywords(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_keywords_volume ON public.keywords(volume DESC NULLS LAST); -- Keywords más populares

-- Índice de texto completo para búsqueda fuzzy (opcional, útil para UI)
CREATE INDEX IF NOT EXISTS idx_keywords_search ON public.keywords USING gin(to_tsvector('spanish', keyword));

-- Comentarios
COMMENT ON TABLE public.keywords IS 'Keywords tracked for ASO ranking monitoring';
COMMENT ON COLUMN public.keywords.volume IS 'Estimated monthly search volume';
COMMENT ON COLUMN public.keywords.difficulty IS 'SEO difficulty score (0-100, higher = harder)';

-- ============================================================================
-- TRIGGERS: updated_at auto-update
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_apps_updated_at
  BEFORE UPDATE ON public.apps
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_keywords_updated_at
  BEFORE UPDATE ON public.keywords
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- ============================================================================
-- SEED DATA: Tier limits (opcional, para referencia)
-- ============================================================================

-- Free tier: 1 app, 50 keywords
-- Pro tier: 5 apps, 500 keywords
-- Enterprise tier: 50 apps, unlimited keywords

-- ============================================================================
-- END OF MIGRATION 001
-- ============================================================================
