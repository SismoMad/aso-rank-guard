"""
FastAPI server for ASO Rank Guard Dashboard
Serves data from Supabase to the HTML dashboard
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="ASO Rank Guard API", version="2.0")

# CORS para permitir acceso desde el dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Service role para server-side
)

APP_ID = "d30da119-98d7-4c12-9e9f-13f3726c82fe"


# === AUTH MIDDLEWARE ===
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Verificar token de Supabase Auth (opcional para desarrollo)
    En producción, descomentar para requerir autenticación
    """
    # if not authorization:
    #     raise HTTPException(status_code=401, detail="No authorization header")
    # 
    # token = authorization.replace("Bearer ", "")
    # user = supabase.auth.get_user(token)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Invalid token")
    # return user
    return {"id": "5126950f-9eb9-4ea4-bf79-9ac2f65984fa"}  # Mock user for dev


# === ENDPOINTS ===

@app.get("/")
async def root():
    return {
        "app": "ASO Rank Guard API",
        "version": "2.0",
        "status": "operational",
        "endpoints": {
            "stats": "/api/stats",
            "current": "/api/rankings/current",
            "history": "/api/rankings/history?days=7",
            "changes": "/api/changes?hours=24"
        }
    }


@app.get("/api/stats")
async def get_stats(user = Depends(get_current_user)):
    """
    Estadísticas generales del sistema
    """
    try:
        # Total keywords
        keywords_result = supabase.table("keywords")\
            .select("id", count="exact")\
            .eq("app_id", APP_ID)\
            .eq("is_active", True)\
            .execute()
        
        total_keywords = keywords_result.count
        
        # Obtener rankings más recientes
        rankings_result = supabase.table("rankings")\
            .select("keyword_id, rank, tracked_at")\
            .order("tracked_at", desc=True)\
            .limit(1000)\
            .execute()
        
        # Agrupar por keyword_id y tomar el más reciente
        latest_ranks = {}
        for r in rankings_result.data:
            kw_id = r["keyword_id"]
            if kw_id not in latest_ranks:
                latest_ranks[kw_id] = r["rank"]
        
        # Contar por rangos
        top_10 = sum(1 for rank in latest_ranks.values() if rank <= 10)
        top_50 = sum(1 for rank in latest_ranks.values() if rank <= 50)
        
        # Última actualización
        last_ranking = rankings_result.data[0] if rankings_result.data else None
        last_check = last_ranking["tracked_at"] if last_ranking else datetime.now().isoformat()
        
        return {
            "total_keywords": total_keywords,
            "top_10_keywords": top_10,
            "top_50_keywords": top_50,
            "last_check": last_check,
            "cached": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rankings/current")
async def get_current_rankings(user = Depends(get_current_user)):
    """
    Rankings actuales de todas las keywords
    """
    try:
        # Obtener keywords con sus rankings más recientes
        query = """
        WITH latest_rankings AS (
            SELECT DISTINCT ON (keyword_id)
                keyword_id,
                rank,
                tracked_at
            FROM rankings
            ORDER BY keyword_id, tracked_at DESC
        )
        SELECT 
            k.id,
            k.keyword,
            k.country,
            k.app_id,
            lr.rank,
            lr.tracked_at
        FROM keywords k
        LEFT JOIN latest_rankings lr ON lr.keyword_id = k.id
        WHERE k.app_id = %s AND k.is_active = true
        ORDER BY COALESCE(lr.rank, 999), k.keyword
        """
        
        result = supabase.rpc("exec_sql", {"query": query, "params": [APP_ID]}).execute()
        
        # Alternativa sin SQL custom (más simple pero menos eficiente)
        keywords_result = supabase.table("keywords")\
            .select("id, keyword, country, app_id")\
            .eq("app_id", APP_ID)\
            .eq("is_active", True)\
            .execute()
        
        rankings_by_keyword = {}
        for kw in keywords_result.data:
            ranking = supabase.table("rankings")\
                .select("rank, tracked_at")\
                .eq("keyword_id", kw["id"])\
                .order("tracked_at", desc=True)\
                .limit(1)\
                .execute()
            
            rankings_by_keyword[kw["id"]] = {
                **kw,
                "rank": ranking.data[0]["rank"] if ranking.data else None,
                "tracked_at": ranking.data[0]["tracked_at"] if ranking.data else None
            }
        
        rankings_list = sorted(
            rankings_by_keyword.values(),
            key=lambda x: x["rank"] if x["rank"] else 999
        )
        
        return {
            "rankings": rankings_list,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rankings/history")
async def get_rankings_history(days: int = 7, user = Depends(get_current_user)):
    """
    Histórico de rankings (últimos N días)
    """
    try:
        since = datetime.now() - timedelta(days=days)
        
        # Obtener keywords primero
        keywords_result = supabase.table("keywords")\
            .select("id, keyword")\
            .eq("app_id", APP_ID)\
            .eq("is_active", True)\
            .execute()
        
        keyword_map = {kw["id"]: kw["keyword"] for kw in keywords_result.data}
        keyword_ids = list(keyword_map.keys())
        
        # Obtener rankings históricos
        rankings_result = supabase.table("rankings")\
            .select("keyword_id, rank, tracked_at")\
            .in_("keyword_id", keyword_ids)\
            .gte("tracked_at", since.isoformat())\
            .order("tracked_at", desc=False)\
            .execute()
        
        # Agregar nombres de keywords
        history = []
        for r in rankings_result.data:
            history.append({
                "keyword": keyword_map.get(r["keyword_id"], "Unknown"),
                "rank": r["rank"],
                "timestamp": r["tracked_at"]
            })
        
        return {
            "history": history,
            "days": days,
            "from": since.isoformat(),
            "to": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/changes")
async def get_ranking_changes(hours: int = 24, user = Depends(get_current_user)):
    """
    Cambios de ranking en las últimas N horas
    """
    try:
        since = datetime.now() - timedelta(hours=hours)
        
        # Obtener keywords
        keywords_result = supabase.table("keywords")\
            .select("id, keyword")\
            .eq("app_id", APP_ID)\
            .eq("is_active", True)\
            .execute()
        
        changes = []
        
        for kw in keywords_result.data:
            # Ranking más reciente
            recent = supabase.table("rankings")\
                .select("rank, tracked_at")\
                .eq("keyword_id", kw["id"])\
                .order("tracked_at", desc=True)\
                .limit(1)\
                .execute()
            
            # Ranking anterior (hace N horas)
            previous = supabase.table("rankings")\
                .select("rank, tracked_at")\
                .eq("keyword_id", kw["id"])\
                .lt("tracked_at", since.isoformat())\
                .order("tracked_at", desc=True)\
                .limit(1)\
                .execute()
            
            if recent.data and previous.data:
                new_rank = recent.data[0]["rank"]
                old_rank = previous.data[0]["rank"]
                change = new_rank - old_rank  # Positivo = empeoró, negativo = mejoró
                
                if change != 0:
                    changes.append({
                        "keyword": kw["keyword"],
                        "old_rank": old_rank,
                        "new_rank": new_rank,
                        "change": change,
                        "timestamp": recent.data[0]["tracked_at"]
                    })
        
        return {
            "changes": sorted(changes, key=lambda x: abs(x["change"]), reverse=True),
            "hours": hours,
            "since": since.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Verificar conexión a Supabase
        supabase.table("keywords").select("id", count="exact").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
