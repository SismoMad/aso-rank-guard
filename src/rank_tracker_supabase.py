#!/usr/bin/env python3
"""
ASO Rank Guard - Rastreador de Rankings con Supabase
Versión actualizada que guarda datos en Supabase PostgreSQL en lugar de CSV
"""

import requests
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

from supabase_client import get_supabase_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rank_guard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RankTrackerSupabase:
    """
    Rastreador de rankings que guarda en Supabase
    
    Diferencias con versión CSV:
    - ✅ Multi-usuario (RLS separa datos automáticamente)
    - ✅ Tiempo real (cambios visibles inmediatamente en web)
    - ✅ Escalable (no límites de CSV)
    - ✅ Histórico ilimitado (PostgreSQL maneja grandes volúmenes)
    - ✅ Análisis avanzados (usa funciones SQL)
    """
    
    def __init__(self, user_id: Optional[str] = None, app_id: Optional[str] = None):
        """
        Inicializar tracker
        
        Args:
            user_id: UUID del usuario en Supabase (None = usar admin)
            app_id: UUID de la app a trackear (None = trackear todas las apps del user)
        """
        # Inicializar Supabase (service role para backend scripts)
        self.supabase = get_supabase_client(use_service_role=True)
        
        self.user_id = user_id
        self.app_id = app_id
        
        # Configuración de API (desde env vars o defaults)
        self.itunes_api_url = "https://itunes.apple.com/search"
        self.api_limit = 250
        self.api_timeout = 10
        self.api_delay = float(os.getenv('ITUNES_API_DELAY', 1.5))
        self.max_retries = int(os.getenv('ITUNES_API_MAX_RETRIES', 3))
        
        logger.info("✅ RankTrackerSupabase inicializado")
        
        # Health check
        if not self.supabase.health_check():
            raise Exception("Supabase connection failed")
    
    def get_rank_for_keyword(self, keyword: str, country: str, 
                            app_store_id: int) -> Optional[int]:
        """
        Obtener ranking de la app para un keyword específico
        
        Args:
            keyword: Keyword a buscar
            country: Código del país (ES, US, etc.)
            app_store_id: App Store ID (trackId)
        
        Returns:
            Posición del ranking (1-250) o None si no aparece
        """
        try:
            params = {
                'term': keyword,
                'country': country,
                'entity': 'software',
                'limit': self.api_limit
            }
            
            # Rate limiting con variación aleatoria (evitar detección)
            random_delay = self.api_delay + random.uniform(-0.3 * self.api_delay, 
                                                           0.3 * self.api_delay)
            time.sleep(random_delay)
            
            # Request con retry logic
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        self.itunes_api_url, 
                        params=params, 
                        timeout=self.api_timeout
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            f"⚠️ Intento {attempt + 1} falló para '{keyword}', "
                            f"reintentando..."
                        )
                        time.sleep(2 * (attempt + 1))  # Backoff exponencial
                    else:
                        raise
            
            data = response.json()
            results = data.get('results', [])
            
            # Buscar nuestra app
            for idx, app in enumerate(results, start=1):
                if app.get('trackId') == app_store_id:
                    logger.debug(f"✅ '{keyword}' ({country}): Rank #{idx}")
                    return idx
            
            logger.debug(f"❌ '{keyword}' ({country}): No aparece en top {self.api_limit}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Error de red buscando '{keyword}' ({country}): {e}")
            return None
        except Exception as e:
            logger.error(f"💥 Error inesperado buscando '{keyword}' ({country}): {e}")
            return None
    
    def track_app(self, app_id: Optional[str] = None, 
                  send_alerts: bool = True) -> Dict:
        """
        Trackear todos los keywords de una app
        
        Args:
            app_id: UUID de la app (usa self.app_id si no se especifica)
            send_alerts: Si True, verifica y envía alertas después
        
        Returns:
            Dict con resultados del tracking
        """
        target_app_id = app_id or self.app_id
        
        if not target_app_id:
            raise ValueError("app_id is required")
        
        logger.info(f"🚀 Iniciando tracking para app {target_app_id}...")
        
        # Crear tracking job
        job_id = self.supabase.create_tracking_job(target_app_id, 'manual')
        
        try:
            # 1. Obtener app y keywords desde Supabase
            app_data = self.supabase.client.table('apps')\
                .select('*, keywords!inner(*)')\
                .eq('id', target_app_id)\
                .eq('keywords.is_active', True)\
                .single()\
                .execute()
            
            if not app_data.data:
                raise Exception(f"App {target_app_id} not found")
            
            app = app_data.data
            keywords = app['keywords']
            app_store_id = int(app['app_store_id'])
            
            logger.info(
                f"📊 Tracking '{app['name']}' - "
                f"{len(keywords)} keywords activos"
            )
            
            # 2. Trackear cada keyword
            rankings = []
            total = len(keywords)
            
            for idx, kw in enumerate(keywords, start=1):
                logger.info(
                    f"[{idx}/{total}] Buscando '{kw['keyword']}' en {kw['country']}..."
                )
                
                rank = self.get_rank_for_keyword(
                    kw['keyword'], 
                    kw['country'], 
                    app_store_id
                )
                
                rankings.append({
                    'keyword_id': kw['id'],
                    'rank': rank,
                    'tracked_at': datetime.utcnow().isoformat()
                })
            
            # 3. Guardar rankings en Supabase
            success = self.supabase.bulk_save_rankings(rankings)
            
            if success:
                logger.info(f"✅ {len(rankings)} rankings guardados en Supabase")
                
                # Actualizar tracking job
                self.supabase.update_tracking_job(
                    job_id, 
                    'completed', 
                    len(rankings)
                )
            else:
                raise Exception("Failed to save rankings")
            
            # 4. Enviar alertas si está habilitado
            if send_alerts:
                self._check_and_send_alerts(target_app_id, rankings)
            
            return {
                'success': True,
                'job_id': job_id,
                'rankings_tracked': len(rankings),
                'app_name': app['name'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error durante tracking: {e}")
            
            # Actualizar job como fallido
            if job_id:
                self.supabase.update_tracking_job(job_id, 'failed')
            
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def track_all_user_apps(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        Trackear todas las apps de un usuario
        
        Args:
            user_id: UUID del usuario (usa self.user_id si no se especifica)
        
        Returns:
            Lista de resultados por cada app
        """
        target_user_id = user_id or self.user_id
        
        if not target_user_id:
            raise ValueError("user_id is required")
        
        logger.info(f"🚀 Tracking todas las apps del usuario {target_user_id}...")
        
        # Obtener apps del usuario
        apps = self.supabase.get_user_apps(target_user_id, active_only=True)
        
        if not apps:
            logger.warning("⚠️ No se encontraron apps activas para el usuario")
            return []
        
        logger.info(f"📱 {len(apps)} apps encontradas")
        
        # Trackear cada app
        results = []
        for app in apps:
            logger.info(f"\n{'='*60}")
            logger.info(f"Tracking: {app['name']}")
            logger.info(f"{'='*60}\n")
            
            result = self.track_app(app['id'], send_alerts=True)
            results.append(result)
            
            # Pausa entre apps para evitar rate limiting
            if len(apps) > 1:
                time.sleep(5)
        
        # Resumen final
        successful = sum(1 for r in results if r['success'])
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ TRACKING COMPLETADO")
        logger.info(f"   Apps procesadas: {successful}/{len(apps)}")
        logger.info(f"{'='*60}\n")
        
        return results
    
    def _check_and_send_alerts(self, app_id: str, current_rankings: List[Dict]):
        """
        Verificar cambios significativos y enviar alertas
        
        Args:
            app_id: UUID de la app
            current_rankings: Rankings actuales que acabamos de obtener
        """
        try:
            logger.info("🔍 Verificando alertas automáticas...")
            
            # Importar módulo de alertas (si existe)
            try:
                from supabase_alerts import SupabaseAlertManager
                
                alert_manager = SupabaseAlertManager()
                alert_manager.check_and_send_alerts(app_id)
                
            except ImportError:
                logger.warning(
                    "⚠️ Módulo supabase_alerts no disponible. "
                    "Crea src/supabase_alerts.py para habilitar alertas."
                )
            
        except Exception as e:
            logger.error(f"⚠️ Error verificando alertas: {e}")


def main():
    """
    Script de ejemplo para usar RankTrackerSupabase
    
    Uso:
        # Trackear todas las apps de un usuario
        python src/rank_tracker_supabase.py
    """
    import sys
    
    # Verificar que existe .env
    if not os.path.exists('.env'):
        logger.error("❌ Archivo .env no encontrado. Copia .env.example a .env")
        sys.exit(1)
    
    # Obtener user_id del admin (desde env o DB)
    admin_email = os.getenv('ADMIN_EMAIL')
    
    if not admin_email:
        logger.error("❌ ADMIN_EMAIL no configurado en .env")
        sys.exit(1)
    
    # Inicializar cliente
    supabase = get_supabase_client(use_service_role=True)
    
    # Buscar usuario admin
    user = supabase.get_user_by_email(admin_email)
    
    if not user:
        logger.error(f"❌ Usuario no encontrado: {admin_email}")
        logger.info("💡 Primero crea el usuario en Supabase Dashboard")
        sys.exit(1)
    
    logger.info(f"👤 Usuario encontrado: {user['email']}")
    
    # Crear tracker
    tracker = RankTrackerSupabase(user_id=user['id'])
    
    # Trackear todas las apps
    results = tracker.track_all_user_apps()
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TRACKING")
    print("="*60)
    
    for result in results:
        if result['success']:
            print(f"✅ {result['app_name']}: {result['rankings_tracked']} rankings")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
