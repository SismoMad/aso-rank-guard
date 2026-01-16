#!/usr/bin/env python3
"""
ASO Rank Guard - Rastreador de Rankings del App Store
Herramienta personal para monitorizar keywords de Audio Bible Stories & Chat
"""

import requests
import pandas as pd
import time
import random
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
import sys

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


class RankTracker:
    """Rastreador principal de rankings del App Store"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Inicializar tracker con configuración"""
        self.config = self._load_config(config_path)
        self.app_id = self.config['app']['id']
        self.keywords = self.config['keywords']
        self.countries = self.config['countries']
        self.ranks_file = Path(self.config['storage']['ranks_file'])
        
        # Crear directorio de datos si no existe
        self.ranks_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar histórico
        self.history_df = self._load_history()
        
        logger.info(f"✅ RankTracker inicializado para app {self.app_id}")
        logger.info(f"📊 Monitorizando {len(self.keywords)} keywords en {len(self.countries)} países")
    
    def _load_config(self, config_path: str) -> dict:
        """Cargar configuración desde YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            sys.exit(1)
    
    def _load_history(self) -> pd.DataFrame:
        """Cargar histórico de rankings desde CSV"""
        if self.ranks_file.exists():
            try:
                df = pd.read_csv(self.ranks_file)
                df['date'] = pd.to_datetime(df['date'])
                logger.info(f"📂 Histórico cargado: {len(df)} registros")
                return df
            except Exception as e:
                logger.warning(f"⚠️  Error cargando histórico: {e}. Creando nuevo.")
                return self._create_empty_history()
        else:
            logger.info("📝 Creando nuevo archivo de histórico")
            return self._create_empty_history()
    
    def _create_empty_history(self) -> pd.DataFrame:
        """Crear DataFrame vacío para histórico"""
        return pd.DataFrame(columns=['date', 'keyword', 'country', 'rank', 'app_id'])
    
    def get_rank_for_keyword(self, keyword: str, country: str) -> Optional[int]:
        """
        Obtener ranking de la app para un keyword específico usando iTunes Search API
        
        Args:
            keyword: Keyword a buscar
            country: Código del país (ES, US, etc.)
        
        Returns:
            Posición del ranking (1-250) o None si no aparece
        """
        try:
            # Configurar request
            base_url = self.config['api']['itunes']['base_url']
            limit = self.config['api']['itunes']['limit']
            timeout = self.config['api']['itunes']['timeout']
            
            params = {
                'term': keyword,
                'country': country,
                'entity': 'software',
                'limit': limit
            }
            
            # Rate limiting con delay aleatorio (evitar detección de bot)
            base_delay = self.config['api']['rate_limit']['delay_between_requests']
            # Añadir variación aleatoria ±30% para parecer más humano
            random_delay = base_delay + random.uniform(-0.3 * base_delay, 0.3 * base_delay)
            time.sleep(random_delay)
            
            # Hacer request con retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(base_url, params=params, timeout=timeout)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Intento {attempt + 1} falló para '{keyword}', reintentando...")
                        time.sleep(2 * (attempt + 1))  # Backoff exponencial
                    else:
                        raise
            
            data = response.json()
            results = data.get('results', [])
            
            # Buscar nuestra app por trackId
            for idx, app in enumerate(results, start=1):
                if app.get('trackId') == self.app_id:
                    logger.debug(f"✅ '{keyword}' ({country}): Rank #{idx}")
                    return idx
            
            # No encontrada en top 250
            logger.debug(f"❌ '{keyword}' ({country}): No aparece en top {limit}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Error de red buscando '{keyword}' ({country}): {e}")
            return None
        except Exception as e:
            logger.error(f"💥 Error inesperado buscando '{keyword}' ({country}): {e}")
            return None
    
    def track_all_keywords(self, send_auto_alerts: bool = True) -> pd.DataFrame:
        """
        Rastrear todos los keywords en todos los países
        
        Args:
            send_auto_alerts: Si True, envía alertas automáticas después del tracking
        
        Returns:
            DataFrame con resultados actuales
        """
        logger.info("🚀 Iniciando rastreo de keywords...")
        
        results = []
        total = len(self.keywords) * len(self.countries)
        current = 0
        
        for keyword in self.keywords:
            for country in self.countries:
                current += 1
                logger.info(f"[{current}/{total}] Buscando '{keyword}' en {country}...")
                
                rank = self.get_rank_for_keyword(keyword, country)
                
                results.append({
                    'date': datetime.now(),
                    'keyword': keyword,
                    'country': country,
                    'rank': rank if rank else 999,  # 999 = no aparece
                    'app_id': self.app_id
                })
        
        results_df = pd.DataFrame(results)
        logger.info(f"✅ Rastreo completado: {len(results)} checks realizados")
        
        # Enviar alertas automáticas si está habilitado
        if send_auto_alerts and 'alerts' in self.config and 'telegram' in self.config['alerts']:
            try:
                from auto_notifier import AutoNotifier
                from telegram_alerts import AlertManager
                
                logger.info("🔍 Verificando alertas automáticas...")
                notifier = AutoNotifier(self.config)
                alerts = notifier.check_for_alerts()
                
                if alerts:
                    message = notifier.format_alert_message(alerts)
                    if message:
                        telegram = AlertManager(self.config)
                        telegram.send_telegram_message(message)
                        logger.info(f"🔔 {len(alerts)} alertas enviadas por Telegram")
                else:
                    logger.info("✅ No hay alertas que enviar")
            
            except Exception as e:
                logger.error(f"⚠️ Error al enviar alertas automáticas: {e}")
        
        return results_df
    
    def save_results(self, results_df: pd.DataFrame):
        """Guardar resultados en histórico CSV eliminando duplicados del mismo día"""
        try:
            # Crear backup ANTES de modificar
            self._create_backup()
            
            # Obtener fecha de hoy (solo día, sin hora)
            today = datetime.now().date()
            
            # Eliminar entradas del mismo día del histórico existente
            if len(self.history_df) > 0:
                self.history_df['date'] = pd.to_datetime(self.history_df['date'])
                self.history_df['date_only'] = self.history_df['date'].dt.date
                
                # Filtrar: mantener solo datos de días anteriores
                before_count = len(self.history_df)
                self.history_df = self.history_df[self.history_df['date_only'] != today]
                removed = before_count - len(self.history_df)
                
                if removed > 0:
                    logger.info(f"🧹 Eliminados {removed} registros duplicados del mismo día")
                
                # Eliminar columna temporal
                self.history_df = self.history_df.drop(columns=['date_only'], errors='ignore')
            
            # Concatenar con nuevos resultados
            self.history_df = pd.concat([self.history_df, results_df], ignore_index=True)
            
            # Guardar a CSV
            self.history_df.to_csv(self.ranks_file, index=False)
            logger.info(f"💾 Resultados guardados en {self.ranks_file} ({len(results_df)} nuevos registros)")
            
            # Limpiar datos antiguos si es necesario
            self._cleanup_old_data()
            
            # Limpiar backups antiguos
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"❌ Error guardando resultados: {e}")
    
    def _create_backup(self):
        """Crear backup del CSV actual antes de modificarlo"""
        try:
            if not self.ranks_file.exists():
                return
            
            # Crear directorio de backups
            backup_dir = self.ranks_file.parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Nombre del backup con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f'ranks_backup_{timestamp}.csv'
            
            # Copiar archivo
            shutil.copy2(self.ranks_file, backup_file)
            logger.info(f"💾 Backup creado: {backup_file.name}")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear backup: {e}")
    
    def _cleanup_old_backups(self, max_backups: int = 7):
        """Mantener solo los últimos N backups"""
        try:
            backup_dir = self.ranks_file.parent / 'backups'
            if not backup_dir.exists():
                return
            
            # Listar todos los backups ordenados por fecha (más reciente primero)
            backups = sorted(backup_dir.glob('ranks_backup_*.csv'), reverse=True)
            
            # Eliminar backups antiguos
            if len(backups) > max_backups:
                for backup in backups[max_backups:]:
                    backup.unlink()
                    logger.info(f"🧹 Backup antiguo eliminado: {backup.name}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error limpiando backups: {e}")
    
    def _cleanup_old_data(self):
        """Eliminar datos más antiguos que retention_days"""
        retention_days = self.config['storage']['retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        before_count = len(self.history_df)
        self.history_df = self.history_df[self.history_df['date'] >= cutoff_date]
        after_count = len(self.history_df)
        
        if before_count > after_count:
            logger.info(f"🧹 Limpieza: {before_count - after_count} registros antiguos eliminados")
            self.history_df.to_csv(self.ranks_file, index=False)
    
    def detect_changes(self, current_df: pd.DataFrame) -> List[Dict]:
        """
        Detectar cambios significativos comparando con el día anterior
        
        Returns:
            Lista de cambios detectados con metadata
        """
        changes = []
        
        if len(self.history_df) == 0:
            logger.info("📊 Primera ejecución, no hay histórico para comparar")
            return changes
        
        # Obtener rankings del día anterior
        yesterday = datetime.now() - timedelta(days=1)
        recent_history = self.history_df[self.history_df['date'] >= yesterday]
        
        if len(recent_history) == 0:
            logger.info("⚠️  No hay datos recientes para comparar")
            return changes
        
        # Asegurar que rank sea numérico
        recent_history = recent_history.copy()
        recent_history['rank'] = pd.to_numeric(recent_history['rank'], errors='coerce')
        
        # Comparar cada keyword/country
        for _, current_row in current_df.iterrows():
            keyword = current_row['keyword']
            country = current_row['country']
            current_rank = current_row['rank']
            
            # Buscar última entrada para este keyword/country
            prev_data = recent_history[
                (recent_history['keyword'] == keyword) &
                (recent_history['country'] == country)
            ].sort_values('date', ascending=False)
            
            if len(prev_data) > 0:
                prev_rank = prev_data.iloc[0]['rank']
                diff = prev_rank - current_rank  # Positivo = subió, negativo = bajó
                
                # Detectar cambios significativos
                drop_threshold = self.config['alerts']['drop_threshold']
                rise_threshold = self.config['alerts'].get('rise_threshold', 10)
                
                if diff < -drop_threshold:  # Bajó
                    changes.append({
                        'type': 'drop',
                        'keyword': keyword,
                        'country': country,
                        'prev_rank': int(prev_rank),
                        'current_rank': int(current_rank),
                        'diff': int(diff),
                        'severity': 'high' if abs(diff) > 10 else 'medium'
                    })
                    logger.warning(f"⬇️  CAÍDA: '{keyword}' ({country}) bajó {abs(diff)} posiciones")
                
                elif diff > rise_threshold:  # Subió
                    changes.append({
                        'type': 'rise',
                        'keyword': keyword,
                        'country': country,
                        'prev_rank': int(prev_rank),
                        'current_rank': int(current_rank),
                        'diff': int(diff),
                        'severity': 'positive'
                    })
                    logger.info(f"⬆️  SUBIDA: '{keyword}' ({country}) subió {diff} posiciones")
        
        return changes
    
    def get_summary_stats(self) -> Dict:
        """Obtener estadísticas resumidas del tracking actual"""
        if len(self.history_df) == 0:
            return {}
        
        # Últimos datos
        latest = self.history_df.sort_values('date', ascending=False).iloc[0]['date']
        latest_data = self.history_df[self.history_df['date'] == latest].copy()
        
        # Asegurar que rank sea numérico
        latest_data['rank'] = pd.to_numeric(latest_data['rank'], errors='coerce')
        
        # Calcular stats
        visible_count = len(latest_data[latest_data['rank'] < 250])
        total_count = len(latest_data)
        avg_rank = latest_data[latest_data['rank'] < 250]['rank'].mean()
        
        # Top keywords
        top_keywords = latest_data[latest_data['rank'] < 250].nsmallest(5, 'rank')[
            ['keyword', 'country', 'rank']
        ].to_dict('records')
        
        return {
            'last_update': latest,
            'total_tracked': total_count,
            'visible_in_top250': visible_count,
            'visibility_rate': f"{(visible_count/total_count*100):.1f}%",
            'avg_rank': f"{avg_rank:.1f}" if not pd.isna(avg_rank) else "N/A",
            'top_keywords': top_keywords
        }
    
    def run_daily_check(self) -> Dict:
        """
        Ejecutar check diario completo
        
        Returns:
            Diccionario con resultados y cambios detectados
        """
        logger.info("=" * 60)
        logger.info("🔍 INICIANDO CHECK DIARIO DE ASO RANK GUARD")
        logger.info("=" * 60)
        
        # 1. Rastrear keywords
        current_results = self.track_all_keywords()
        
        # 2. Detectar cambios
        changes = self.detect_changes(current_results)
        
        # 3. Guardar resultados
        self.save_results(current_results)
        
        # 4. Obtener estadísticas
        stats = self.get_summary_stats()
        
        logger.info("=" * 60)
        logger.info(f"✅ Check completado - {len(changes)} cambios detectados")
        logger.info("=" * 60)
        
        return {
            'results': current_results,
            'changes': changes,
            'stats': stats,
            'timestamp': datetime.now()
        }


def main():
    """Función principal - ejecutar check diario"""
    try:
        # Inicializar tracker
        tracker = RankTracker()
        
        # Ejecutar check
        report = tracker.run_daily_check()
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DEL TRACKING")
        print("=" * 60)
        
        stats = report['stats']
        if stats:
            print(f"🕐 Última actualización: {stats['last_update']}")
            print(f"📱 Keywords visibles: {stats['visible_in_top250']}/{stats['total_tracked']} ({stats['visibility_rate']})")
            print(f"📈 Ranking promedio: {stats['avg_rank']}")
            
            if stats['top_keywords']:
                print(f"\n🏆 Top 5 Keywords:")
                for kw in stats['top_keywords']:
                    print(f"   #{kw['rank']} - '{kw['keyword']}' ({kw['country']})")
        
        changes = report['changes']
        if changes:
            print(f"\n⚠️  CAMBIOS DETECTADOS: {len(changes)}")
            for change in changes:
                emoji = "⬇️" if change['type'] == 'drop' else "⬆️"
                print(f"   {emoji} '{change['keyword']}' ({change['country']}): "
                      f"#{change['prev_rank']} → #{change['current_rank']} "
                      f"({change['diff']:+d})")
        else:
            print("\n✅ No hay cambios significativos detectados")
        
        print("=" * 60 + "\n")
        
        return report
        
    except Exception as e:
        logger.error(f"💥 Error en ejecución principal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
