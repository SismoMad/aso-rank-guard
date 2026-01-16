#!/usr/bin/env python3
"""
Report Formatter - Genera reportes formateados para Telegram
Separación de responsabilidades: tracking vs presentación
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportFormatter:
    """Formateador de reportes para tracking de keywords"""
    
    # Volumen proxy basado en tipo de keyword (sin API)
    VOLUME_PATTERNS = {
        'brand': 500,        # "biblenow"
        'generic_2w': 300,   # "bible chat"
        'generic_3w': 150,   # "audio bible stories"
        'long_tail': 50,     # "kids calming audio bible"
        'very_long': 20      # >5 palabras
    }
    
    def __init__(self, max_kw_length: int = 30, config_path: str = 'config/config.yaml'):
        """
        Inicializar formateador
        
        Args:
            max_kw_length: Longitud máxima para truncar keywords en el reporte
            config_path: Ruta al archivo de configuración
        """
        self.max_kw_length = max_kw_length
        
        # Cargar config para detectar brand keywords
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.app_name = self.config['app']['name']
            self.brand_keywords = self._detect_brand_keywords()
        except Exception as e:
            logger.warning(f"No se pudo cargar config: {e}")
            self.config = {}
            self.app_name = ""
            self.brand_keywords = []
    
    def _detect_brand_keywords(self) -> List[str]:
        """Detectar keywords de marca"""
        if not self.app_name:
            return []
        app_name_lower = self.app_name.lower()
        brand_words = app_name_lower.split()
        return [kw for kw in self.config.get('keywords', []) 
                if any(brand in kw.lower() for brand in brand_words)]
    
    def _estimate_volume(self, keyword: str) -> int:
        """Estimar volumen de búsqueda (proxy sin API)"""
        kw_lower = keyword.lower()
        word_count = len(kw_lower.split())
        
        # Brand keywords
        if keyword in self.brand_keywords:
            return self.VOLUME_PATTERNS['brand']
        
        # Long tail (5+ palabras)
        if word_count >= 5:
            return self.VOLUME_PATTERNS['very_long']
        
        # 3-4 palabras
        if word_count >= 3:
            return self.VOLUME_PATTERNS['long_tail']
        
        # Generic 2-3 palabras
        # Boost si contiene términos populares
        popular_terms = ['bible', 'audio', 'chat', 'stories', 'sleep', 'kids']
        if any(term in kw_lower for term in popular_terms):
            return self.VOLUME_PATTERNS['generic_3w']
        
        return self.VOLUME_PATTERNS['generic_2w']
    
    def _calculate_difficulty(self, rank: int, volume: int) -> str:
        """Calcular dificultad estimada"""
        # Heurística simple: rank alto + volumen alto = difícil
        if rank < 20 and volume > 200:
            return "high"
        elif rank < 50 and volume > 100:
            return "medium"
        elif rank > 150:
            return "high"  # Muy abajo = muy competido o irrelevante
        else:
            return "low"
    
    def _format_volume(self, volume: int) -> str:
        """Formatear volumen para display"""
        if volume >= 400:
            return "🔥"  # Alto
        elif volume >= 100:
            return "📊"  # Medio
        else:
            return "📉"  # Bajo
    
    def _format_difficulty(self, difficulty: str) -> str:
        """Formatear difficulty para display"""
        if difficulty == "high":
            return "🔴"
        elif difficulty == "medium":
            return "🟡"
        else:
            return "🟢"
    
    def format_tracking_report(
        self, 
        df_results: pd.DataFrame,
        df_all: pd.DataFrame,
        has_previous: bool
    ) -> str:
        """
        Generar reporte completo de tracking formateado para Telegram
        
        Args:
            df_results: DataFrame con resultados del tracking actual
            df_all: DataFrame con todo el histórico
            has_previous: Si hay datos de un snapshot anterior
        
        Returns:
            String formateado en Markdown para Telegram
        """
        try:
            # Procesar datos
            changes = self._calculate_changes(df_all, has_previous)
            
            if not changes:
                return "⚠️ No se pudieron calcular cambios"
            
            df_changes = pd.DataFrame(changes).sort_values('rank')
            
            # Categorizar por ranking
            top10 = df_changes[df_changes['rank'] <= 10]
            top30 = df_changes[(df_changes['rank'] > 10) & (df_changes['rank'] <= 30)]
            top100 = df_changes[(df_changes['rank'] > 30) & (df_changes['rank'] <= 100)]
            
            # Construir mensaje
            message = self._build_header(df_results, has_previous)
            message += self._build_top_keywords(top10, top30, top100)
            
            if has_previous:
                message += self._build_movers(df_changes)
            
            message += f"🕒 {datetime.now().strftime('%H:%M')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formateando reporte: {e}", exc_info=True)
            return f"❌ Error generando reporte: {str(e)}"
    
    def _calculate_changes(
        self, 
        df_all: pd.DataFrame, 
        has_previous: bool
    ) -> List[Dict]:
        """Calcular cambios entre snapshot actual y anterior"""
        
        df_all['date'] = pd.to_datetime(df_all['date'])
        df_all['date_only'] = df_all['date'].dt.date
        
        unique_dates = sorted(df_all['date_only'].unique())
        latest_date = unique_dates[-1]
        previous_date = unique_dates[-2] if len(unique_dates) > 1 else None
        
        # Datos actuales (sin duplicados)
        df_latest = df_all[df_all['date_only'] == latest_date].drop_duplicates(
            subset=['keyword'], keep='last'
        )
        
        # Datos anteriores
        if has_previous and previous_date:
            df_previous = df_all[df_all['date_only'] == previous_date].drop_duplicates(
                subset=['keyword'], keep='last'
            )
        else:
            df_previous = pd.DataFrame()
        
        # Calcular cambios
        changes = []
        for _, row in df_latest.iterrows():
            keyword = row['keyword']
            current_rank = row['rank']
            
            # Buscar rank anterior
            change = "NEW"
            diff = 0
            
            if has_previous and len(df_previous) > 0:
                prev_row = df_previous[df_previous['keyword'] == keyword]
                if len(prev_row) > 0:
                    prev_rank = prev_row.iloc[0]['rank']
                    diff = prev_rank - current_rank  # Positivo = subió
                    
                    if diff > 0:
                        change = f"↑{abs(diff)}"
                    elif diff < 0:
                        change = f"↓{abs(diff)}"
                    else:
                        change = "="
            
            # Calcular volume y difficulty
            volume = self._estimate_volume(keyword)
            difficulty = self._calculate_difficulty(current_rank, volume)
            
            changes.append({
                'keyword': keyword,
                'rank': current_rank,
                'change': change,
                'diff_value': diff,
                'volume': volume,
                'difficulty': difficulty
            })
        
        return changes
    
    def _build_header(self, df_results: pd.DataFrame, has_previous: bool) -> str:
        """Construir header del reporte"""
        total = len(df_results)
        visible = len(df_results[df_results['rank'] < 250])
        
        message = "✅ *Tracking completado*\n\n"
        message += f"📊 Total: {total} keywords\n"
        message += f"👁️ Visibles: {visible}\n"
        
        if not has_previous:
            message += "⚠️ Primera ejecución - sin comparación\n"
        
        message += "\n"
        message += "_Leyenda: 🔥📊📉=vol · 🔴🟡🟢=diff_\n\n"
        
        return message
    
    def _build_top_keywords(
        self, 
        top10: pd.DataFrame, 
        top30: pd.DataFrame, 
        top100: pd.DataFrame
    ) -> str:
        """Construir secciones de top keywords"""
        message = ""
        
        # TOP 10
        if len(top10) > 0:
            message += "🏆 *TOP 10*\n"
            for _, row in top10.iterrows():
                kw = self._truncate_keyword(row['keyword'])
                vol_emoji = self._format_volume(row['volume'])
                diff_emoji = self._format_difficulty(row['difficulty'])
                message += f"#{int(row['rank'])} {row['change']} {vol_emoji}{diff_emoji} · `{kw}`\n"
            message += "\n"
        
        # TOP 11-30
        if len(top30) > 0:
            message += "🥈 *TOP 11-30*\n"
            for _, row in top30.iterrows():
                kw = self._truncate_keyword(row['keyword'])
                vol_emoji = self._format_volume(row['volume'])
                diff_emoji = self._format_difficulty(row['difficulty'])
                message += f"#{int(row['rank'])} {row['change']} {vol_emoji}{diff_emoji} · `{kw}`\n"
            message += "\n"
        
        # TOP 31-100
        if len(top100) > 0:
            message += "📈 *TOP 31-100*\n"
            for _, row in top100.iterrows():
                kw = self._truncate_keyword(row['keyword'])
                vol_emoji = self._format_volume(row['volume'])
                diff_emoji = self._format_difficulty(row['difficulty'])
                message += f"#{int(row['rank'])} {row['change']} {vol_emoji}{diff_emoji} · `{kw}`\n"
            message += "\n"
        
        return message
    
    def _build_movers(self, df_changes: pd.DataFrame) -> str:
        """Construir sección de mayores subidas/caídas"""
        message = ""
        
        top_gains = df_changes[df_changes['diff_value'] > 0].nlargest(3, 'diff_value')
        top_drops = df_changes[df_changes['diff_value'] < 0].nsmallest(3, 'diff_value')
        
        if len(top_gains) > 0:
            message += "🚀 *Mayores subidas*\n"
            for _, row in top_gains.iterrows():
                kw = self._truncate_keyword(row['keyword'])
                message += f"#{int(row['rank'])} {row['change']} · `{kw}`\n"
            message += "\n"
        
        if len(top_drops) > 0:
            message += "📉 *Mayores caídas*\n"
            for _, row in top_drops.iterrows():
                kw = self._truncate_keyword(row['keyword'])
                message += f"#{int(row['rank'])} {row['change']} · `{kw}`\n"
            message += "\n"
        
        return message
    
    def _truncate_keyword(self, keyword: str) -> str:
        """Truncar keyword si es muy larga"""
        if len(keyword) > self.max_kw_length:
            return keyword[:self.max_kw_length]
        return keyword
    
    def split_long_message(self, message: str, max_length: int = 4000) -> List[str]:
        """
        Dividir mensaje largo en partes respetando formato Markdown
        
        Args:
            message: Mensaje completo
            max_length: Longitud máxima por parte
        
        Returns:
            Lista de mensajes divididos
        """
        if len(message) <= max_length:
            return [message]
        
        # Dividir por secciones (líneas que empiezan con emoji de sección)
        parts = []
        current_part = ""
        
        for line in message.split('\n'):
            # Si añadir esta línea supera el límite y ya hay contenido
            if len(current_part) + len(line) + 1 > max_length and current_part:
                parts.append(current_part.strip())
                current_part = ""
            
            current_part += line + "\n"
        
        # Añadir última parte
        if current_part.strip():
            parts.append(current_part.strip())
        
        return parts
