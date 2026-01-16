#!/usr/bin/env python3
"""
API REST para ASO Rank Guard
Endpoints para consultar rankings, históricos y estadísticas
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging
from functools import lru_cache
import time

app = FastAPI(
    title="ASO Rank Guard API",
    description="API REST para consultar rankings de keywords ASO",
    version="1.0.0"
)

# CORS más restrictivo (solo servidor y localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://194.164.160.111",
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Compresión GZip para respuestas grandes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rutas de archivos
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
RANKS_FILE = BASE_DIR / "data" / "ranks.csv"

# Cache global
_rankings_cache = None
_rankings_cache_time = 0
CACHE_TTL = 300  # 5 minutos

@lru_cache(maxsize=1)
def load_config():
    """Cargar configuración (cached)"""
    try:
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise HTTPException(status_code=500, detail="Error loading configuration")

def load_rankings(force_refresh: bool = False):
    """Cargar rankings desde CSV con caché de 5 minutos"""
    global _rankings_cache, _rankings_cache_time
    
    current_time = time.time()
    
    # Usar caché si está fresco
    if not force_refresh and _rankings_cache is not None and (current_time - _rankings_cache_time) < CACHE_TTL:
        return _rankings_cache.copy()
    
    # Recargar datos
    try:
        if not RANKS_FILE.exists():
            raise HTTPException(status_code=404, detail="No hay datos de rankings")
        
        logger.info("Loading rankings from CSV...")
        df = pd.read_csv(RANKS_FILE)
        
        # Renombrar 'date' a 'timestamp' para compatibilidad
        if 'date' in df.columns:
            df.rename(columns={'date': 'timestamp'}, inplace=True)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Actualizar caché
        _rankings_cache = df
        _rankings_cache_time = current_time
        
        logger.info(f"Loaded {len(df)} records into cache")
        return df.copy()
    
    except Exception as e:
        logger.error(f"Error loading rankings: {e}")
        raise HTTPException(status_code=500, detail="Error loading rankings data")

@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    """Endpoint raíz - información de la API"""
    logger.info(f"Root endpoint accessed from {get_remote_address(request)}")
    return {
        "name": "ASO Rank Guard API",
        "version": "2.0.0",
        "status": "running",
        "cache_ttl_seconds": CACHE_TTL,
        "rate_limit": "60 requests/minute per IP",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "config": "/api/config",
            "current": "/api/rankings/current",
            "history": "/api/rankings/history",
            "keyword": "/api/rankings/keyword/{keyword}",
            "stats": "/api/stats",
            "changes": "/api/changes",
            "dashboard": "/dashboard"
        }
    }

@app.get("/health")
@limiter.limit("120/minute")
async def health_check(request: Request):
    """Health check endpoint con métricas detalladas"""
    try:
        data_exists = RANKS_FILE.exists()
        cache_age = time.time() - _rankings_cache_time if _rankings_cache is not None else None
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "data_available": data_exists,
            "cache": {
                "active": _rankings_cache is not None,
                "age_seconds": int(cache_age) if cache_age else None,
                "ttl_seconds": CACHE_TTL
            }
        }
        
        if data_exists:
            file_stat = RANKS_FILE.stat()
            health_data["data_file"] = {
                "size_kb": round(file_stat.st_size / 1024, 2),
                "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            }
        
        return health_data
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/api/config")
async def get_config():
    """Obtener configuración (sin credenciales)"""
    config = load_config()
    
    # Eliminar info sensible
    safe_config = {
        "app": config.get("app", {}),
        "keywords": config.get("keywords", []),
        "countries": config.get("countries", []),
        "schedule": config.get("schedule", {})
    }
    
    return safe_config

@app.get("/api/rankings/current")
async def get_current_rankings():
    """Obtener rankings más recientes"""
    df = load_rankings()
    
    # Últimas posiciones de cada keyword
    latest = df.sort_values('timestamp').groupby(['keyword', 'country']).last().reset_index()
    
    rankings = []
    for _, row in latest.iterrows():
        rankings.append({
            "keyword": row['keyword'],
            "country": row['country'],
            "rank": int(row['rank']) if pd.notna(row['rank']) else None,
            "timestamp": row['timestamp'].isoformat()
        })
    
    return {
        "total": len(rankings),
        "last_update": latest['timestamp'].max().isoformat(),
        "rankings": rankings
    }

@app.get("/api/rankings/history")
async def get_history(days: int = 30, keyword: str = None, country: str = "US"):
    """Obtener histórico de rankings"""
    df = load_rankings()
    
    # Filtrar por fecha
    cutoff_date = datetime.now() - timedelta(days=days)
    df = df[df['timestamp'] >= cutoff_date]
    
    # Filtrar por keyword si se especifica
    if keyword:
        df = df[df['keyword'] == keyword]
    
    # Filtrar por país
    df = df[df['country'] == country]
    
    history = []
    for _, row in df.iterrows():
        history.append({
            "keyword": row['keyword'],
            "country": row['country'],
            "rank": int(row['rank']) if pd.notna(row['rank']) else None,
            "timestamp": row['timestamp'].isoformat()
        })
    
    return {
        "total": len(history),
        "days": days,
        "keyword": keyword,
        "country": country,
        "history": history
    }

@app.get("/api/rankings/keyword/{keyword}")
async def get_keyword_ranking(keyword: str, days: int = 30):
    """Obtener histórico de una keyword específica"""
    df = load_rankings()
    
    # Filtrar por keyword
    df = df[df['keyword'] == keyword]
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Keyword '{keyword}' no encontrada")
    
    # Últimos N días
    cutoff_date = datetime.now() - timedelta(days=days)
    df = df[df['timestamp'] >= cutoff_date]
    
    # Ordenar por fecha
    df = df.sort_values('timestamp')
    
    history = []
    for _, row in df.iterrows():
        history.append({
            "rank": int(row['rank']) if pd.notna(row['rank']) else None,
            "country": row['country'],
            "timestamp": row['timestamp'].isoformat()
        })
    
    # Calcular stats
    ranks = df['rank'].dropna()
    current_rank = int(df.iloc[-1]['rank']) if not df.empty and pd.notna(df.iloc[-1]['rank']) else None
    best_rank = int(ranks.min()) if len(ranks) > 0 else None
    worst_rank = int(ranks.max()) if len(ranks) > 0 else None
    avg_rank = round(ranks.mean(), 1) if len(ranks) > 0 else None
    
    return {
        "keyword": keyword,
        "current_rank": current_rank,
        "best_rank": best_rank,
        "worst_rank": worst_rank,
        "average_rank": avg_rank,
        "total_checks": len(history),
        "history": history
    }

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas generales"""
    df = load_rankings()
    config = load_config()
    
    # Stats generales
    total_keywords = len(df['keyword'].unique())
    total_checks = len(df)
    
    # Rankings actuales
    latest = df.sort_values('timestamp').groupby('keyword').last()
    
    # Top keywords (mejor ranking)
    top_keywords = latest.nsmallest(10, 'rank')[['rank']].to_dict()['rank']
    top_keywords = {k: int(v) if pd.notna(v) else None for k, v in top_keywords.items()}
    
    # Keywords en top 10
    in_top_10 = len(latest[latest['rank'] <= 10])
    in_top_50 = len(latest[latest['rank'] <= 50])
    in_top_100 = len(latest[latest['rank'] <= 100])
    
    return {
        "total_keywords": total_keywords,
        "total_checks": total_checks,
        "last_check": df['timestamp'].max().isoformat(),
        "top_10_keywords": in_top_10,
        "top_50_keywords": in_top_50,
        "top_100_keywords": in_top_100,
        "best_keywords": top_keywords
    }

@app.get("/api/changes")
async def get_recent_changes(hours: int = 24):
    """Obtener cambios recientes en rankings"""
    df = load_rankings()
    
    # Obtener datos de las últimas X horas
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_df = df[df['timestamp'] >= cutoff_time]
    
    if recent_df.empty:
        return {"changes": [], "total": 0}
    
    # Para cada keyword, comparar primera vs última posición en el periodo
    changes = []
    for keyword in recent_df['keyword'].unique():
        kw_df = recent_df[recent_df['keyword'] == keyword].sort_values('timestamp')
        
        if len(kw_df) < 2:
            continue
        
        first_rank = kw_df.iloc[0]['rank']
        last_rank = kw_df.iloc[-1]['rank']
        
        if pd.notna(first_rank) and pd.notna(last_rank) and first_rank != last_rank:
            change = int(first_rank - last_rank)  # Positivo = subió
            changes.append({
                "keyword": keyword,
                "old_rank": int(first_rank),
                "new_rank": int(last_rank),
                "change": change,
                "timestamp": kw_df.iloc[-1]['timestamp'].isoformat()
            })
    
    # Ordenar por magnitud del cambio
    changes.sort(key=lambda x: abs(x['change']), reverse=True)
    
    return {
        "total": len(changes),
        "hours": hours,
        "changes": changes
    }

@app.get("/dashboard")
async def get_dashboard():
    """Servir el dashboard HTML"""
    dashboard_file = BASE_DIR / "web" / "dashboard.html"
    if not dashboard_file.exists():
        raise HTTPException(status_code=404, detail="Dashboard no encontrado")
    
    return FileResponse(dashboard_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
