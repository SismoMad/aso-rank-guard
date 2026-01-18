#!/usr/bin/env python3
"""
Supabase Client Wrapper for ASO Rank Guard
Provides a reusable client for all Python scripts to interact with Supabase
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
    from postgrest.exceptions import APIError
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.error("❌ supabase-py not installed. Run: pip install supabase")

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    logger.warning("⚠️ python-dotenv not installed. Using system env vars only.")


class SupabaseClient:
    """
    Wrapper for Supabase client with helper methods for ASO Rank Guard
    
    Usage:
        # For backend scripts (use service role)
        client = SupabaseClient(use_service_role=True)
        
        # For user operations (use anon key + RLS)
        client = SupabaseClient(use_service_role=False)
    """
    
    def __init__(self, use_service_role: bool = True):
        """
        Initialize Supabase client
        
        Args:
            use_service_role: If True, uses SERVICE_ROLE_KEY (bypasses RLS).
                            If False, uses ANON_KEY (subject to RLS).
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py library not installed")
        
        # Get credentials from environment
        self.url = os.getenv('SUPABASE_URL')
        
        if use_service_role:
            self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            self.role = 'service_role'
        else:
            self.key = os.getenv('SUPABASE_ANON_KEY')
            self.role = 'anon'
        
        # Validate credentials
        if not self.url or not self.key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY/SUPABASE_ANON_KEY "
                "in .env file or environment variables."
            )
        
        # Create client
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info(f"✅ Supabase client initialized (role: {self.role})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    # -------------------------------------------------------------------------
    # User Operations
    # -------------------------------------------------------------------------
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user profile by email"""
        try:
            response = self.client.table('profiles')\
                .select('*')\
                .eq('email', email)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None
    
    def get_user_by_telegram_id(self, telegram_user_id: str) -> Optional[Dict]:
        """Get user profile by Telegram user ID"""
        try:
            response = self.client.table('profiles')\
                .select('*')\
                .eq('telegram_user_id', telegram_user_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            logger.debug(f"User not found for telegram_id {telegram_user_id}")
            return None
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user has admin privileges"""
        try:
            response = self.client.table('profiles')\
                .select('is_admin')\
                .eq('id', user_id)\
                .single()\
                .execute()
            return response.data.get('is_admin', False)
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
    
    # -------------------------------------------------------------------------
    # App Operations
    # -------------------------------------------------------------------------
    
    def get_user_apps(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """Get all apps for a user"""
        try:
            query = self.client.table('apps')\
                .select('*')\
                .eq('user_id', user_id)
            
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching user apps: {e}")
            return []
    
    def create_app(self, user_id: str, app_data: Dict) -> Optional[Dict]:
        """Create a new app"""
        try:
            data = {
                'user_id': user_id,
                'app_store_id': app_data['app_store_id'],
                'name': app_data['name'],
                'bundle_id': app_data.get('bundle_id'),
                'platform': app_data.get('platform', 'ios'),
                'is_active': True
            }
            
            response = self.client.table('apps').insert(data).execute()
            logger.info(f"✅ App created: {data['name']}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating app: {e}")
            return None
    
    # -------------------------------------------------------------------------
    # Keyword Operations
    # -------------------------------------------------------------------------
    
    def get_app_keywords(self, app_id: str, active_only: bool = True) -> List[Dict]:
        """Get all keywords for an app"""
        try:
            query = self.client.table('keywords')\
                .select('*')\
                .eq('app_id', app_id)
            
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching keywords: {e}")
            return []
    
    def create_keyword(self, app_id: str, keyword_data: Dict) -> Optional[Dict]:
        """Create a new keyword"""
        try:
            data = {
                'app_id': app_id,
                'keyword': keyword_data['keyword'],
                'country': keyword_data['country'],
                'is_active': True
            }
            
            response = self.client.table('keywords').insert(data).execute()
            logger.info(f"✅ Keyword created: {data['keyword']} ({data['country']})")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating keyword: {e}")
            return None
    
    def bulk_create_keywords(self, app_id: str, keywords: List[Dict]) -> bool:
        """Create multiple keywords at once"""
        try:
            data = [
                {
                    'app_id': app_id,
                    'keyword': kw['keyword'],
                    'country': kw['country'],
                    'is_active': True
                }
                for kw in keywords
            ]
            
            response = self.client.table('keywords').insert(data).execute()
            logger.info(f"✅ {len(data)} keywords created")
            return True
        except Exception as e:
            logger.error(f"Error bulk creating keywords: {e}")
            return False
    
    # -------------------------------------------------------------------------
    # Ranking Operations
    # -------------------------------------------------------------------------
    
    def save_ranking(self, keyword_id: str, rank: Optional[int]) -> bool:
        """Save a single ranking result"""
        try:
            data = {
                'keyword_id': keyword_id,
                'rank': rank if rank and rank < 999 else None,
                'tracked_at': datetime.utcnow().isoformat()
            }
            
            self.client.table('rankings').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving ranking: {e}")
            return False
    
    def bulk_save_rankings(self, rankings: List[Dict]) -> bool:
        """Save multiple rankings at once"""
        try:
            data = [
                {
                    'keyword_id': r['keyword_id'],
                    'rank': (
                        int(r['rank'])
                        if r.get('rank') and int(r['rank']) > 0 and int(r['rank']) < 999
                        else 999
                    ),
                    'tracked_at': r.get('tracked_at', datetime.utcnow().isoformat())
                }
                for r in rankings
            ]
            
            response = self.client.table('rankings').insert(data).execute()
            logger.info(f"✅ {len(data)} rankings saved to database")
            return True
        except Exception as e:
            logger.error(f"Error bulk saving rankings: {e}")
            return False
    
    def get_recent_rankings(self, keyword_id: str, limit: int = 30) -> List[Dict]:
        """Get recent rankings for a keyword"""
        try:
            response = self.client.table('rankings')\
                .select('*')\
                .eq('keyword_id', keyword_id)\
                .order('tracked_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching rankings: {e}")
            return []
    
    def get_keyword_trend(self, keyword_id: str, days: int = 7) -> Optional[Dict]:
        """Get keyword trend using database function"""
        try:
            response = self.client.rpc('get_keyword_trend', {
                'p_keyword_id': keyword_id,
                'p_days': days
            }).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting keyword trend: {e}")
            return None
    
    # -------------------------------------------------------------------------
    # Alert Operations
    # -------------------------------------------------------------------------
    
    def get_active_alerts(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get active alerts (optionally filtered by user)"""
        try:
            query = self.client.table('alerts')\
                .select('*, profiles!inner(id, email, telegram_user_id)')\
                .eq('is_active', True)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []
    
    def save_alert_history(self, alert_id: str, user_id: str, 
                          message: str, channel: str, status: str = 'sent') -> bool:
        """Save alert to history"""
        try:
            data = {
                'user_id': user_id,
                'alert_id': alert_id,
                'message': message,
                'channel': channel,
                'status': status
            }
            
            self.client.table('alert_history').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")
            return False
    
    # -------------------------------------------------------------------------
    # Tracking Jobs
    # -------------------------------------------------------------------------
    
    def create_tracking_job(self, app_id: str, job_type: str = 'manual') -> Optional[str]:
        """Create a tracking job record"""
        try:
            data = {
                'app_id': app_id,
                'job_type': job_type,
                'status': 'pending'
            }
            
            response = self.client.table('tracking_jobs').insert(data).execute()
            job_id = response.data[0]['id']
            logger.info(f"✅ Tracking job created: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Error creating tracking job: {e}")
            return None
    
    def update_tracking_job(self, job_id: str, status: str, 
                           results_count: Optional[int] = None) -> bool:
        """Update tracking job status"""
        try:
            data = {'status': status}
            
            if results_count is not None:
                data['results_count'] = results_count
            
            if status == 'completed':
                data['completed_at'] = datetime.utcnow().isoformat()
            
            self.client.table('tracking_jobs')\
                .update(data)\
                .eq('id', job_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error updating tracking job: {e}")
            return False
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def health_check(self) -> bool:
        """Check if Supabase connection is healthy"""
        try:
            # Try a simple query
            self.client.table('profiles').select('id').limit(1).execute()
            logger.info("✅ Supabase connection healthy")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase health check failed: {e}")
            return False


# Singleton instance for convenience
_client_instance: Optional[SupabaseClient] = None

def get_supabase_client(use_service_role: bool = True) -> SupabaseClient:
    """
    Get or create Supabase client instance
    
    Args:
        use_service_role: If True, uses service role key (backend scripts)
    
    Returns:
        SupabaseClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = SupabaseClient(use_service_role=use_service_role)
    
    return _client_instance
