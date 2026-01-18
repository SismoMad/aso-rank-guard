#!/usr/bin/env python3
"""
Script para migrar datos de CSV a Supabase
Convierte el historial existente de ranks.csv a la base de datos
"""

import pandas as pd
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_csv_to_supabase():
    """Migrar datos desde CSV a Supabase"""
    
    logger.info("🚀 Iniciando migración CSV → Supabase...")
    
    # 1. Verificar que existe el CSV
    csv_file = Path('data/ranks.csv')
    if not csv_file.exists():
        logger.error(f"❌ No se encontró {csv_file}")
        logger.info("💡 Ejecuta primero un tracking con el bot CSV")
        sys.exit(1)
    
    # 2. Cargar CSV
    logger.info(f"📂 Cargando {csv_file}...")
    df = pd.read_csv(csv_file)
    logger.info(f"📊 {len(df)} registros encontrados")
    
    # 3. Conectar a Supabase
    logger.info("🔌 Conectando a Supabase...")
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    
    # Test connection
    try:
        supabase.table("profiles").select("id").limit(1).execute()
        logger.info("✅ Conexión establecida")
    except Exception as e:
        logger.error(f"❌ No se pudo conectar a Supabase: {e}")
        sys.exit(1)
    # 4. Obtener o crear usuario admin
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@aso-rank-guard.local')
    logger.info(f"👤 Buscando usuario: {admin_email}")

    result = supabase.table("profiles")\
        .select("id")\
        .eq("email", admin_email)\
        .limit(1)\
        .execute()
    
    if result.data:
        user_id = result.data[0]['id']
        logger.info(f"✅ Usuario encontrado: {user_id}")
    else:
        logger.warning("⚠️ Usuario no encontrado por email. Usando primer perfil disponible.")
        fallback = supabase.table("profiles")\
            .select("id,email")\
            .limit(1)\
            .execute()
        if not fallback.data:
            logger.error("❌ No hay perfiles en Supabase. Crea un usuario primero en Auth.")
            sys.exit(1)
        user_id = fallback.data[0]['id']
        logger.info(f"✅ Usando perfil existente: {fallback.data[0].get('email')}")
    
    # 5. Crear app si no existe
    logger.info("📱 Verificando app...")
    
    # Leer config para obtener datos de la app
    import yaml
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    app_id_int = config['app']['id']
    app_name = config['app']['name']
    bundle_id = config['app'].get('bundle_id', 'com.unknown.app')
    
    # Buscar app existente
    result = supabase.table('apps')\
        .select('id')\
        .eq('app_store_id', str(app_id_int))\
        .limit(1)\
        .execute()
    
    if result.data:
        app_uuid = result.data[0]['id']
        logger.info(f"✅ App encontrada: {app_uuid}")
    else:
        logger.info(f"➕ Creando app: {app_name}")
        new_app = {
            "user_id": user_id,
            "name": app_name,
            "app_store_id": str(app_id_int),
            "bundle_id": bundle_id,
            "platform": "ios"
        }
        result = supabase.table('apps').insert(new_app).execute()
        app_uuid = result.data[0]['id']
        logger.info(f"✅ App creada: {app_uuid}")
    
    # 6. Crear keywords
    logger.info("🔑 Sincronizando keywords...")
    
    unique_keywords = df[['keyword', 'country']].drop_duplicates()
    logger.info(f"📝 {len(unique_keywords)} keywords únicos encontrados")
    
    keyword_map = {}  # {(keyword, country): uuid}
    
    for _, row in unique_keywords.iterrows():
        keyword_text = row['keyword']
        country = row['country']
        
        # Buscar keyword existente
        result = supabase.table('keywords')\
            .select('id')\
            .eq('app_id', app_uuid)\
            .eq('keyword', keyword_text)\
            .eq('country', country)\
            .limit(1)\
            .execute()
        
        if result.data:
            keyword_id = result.data[0]['id']
        else:
            # Crear keyword
            new_keyword = {
                "app_id": app_uuid,
                "keyword": keyword_text,
                "country": country
            }
            result = supabase.table('keywords').insert(new_keyword).execute()
            keyword_id = result.data[0]['id']
        
        keyword_map[(keyword_text, country)] = keyword_id
    
    logger.info(f"✅ {len(keyword_map)} keywords sincronizados")
    
    # 7. Migrar rankings
    logger.info("📊 Migrando rankings...")
    
    rankings_to_insert = []
    batch_size = 500  # Insertar en lotes de 500
    
    for idx, row in df.iterrows():
        keyword_key = (row['keyword'], row['country'])
        keyword_id = keyword_map.get(keyword_key)
        
        if not keyword_id:
            logger.warning(f"⚠️  Keyword no encontrada: {keyword_key}")
            continue
        
        ranking = {
            "keyword_id": keyword_id,
            "rank": int(row['rank']) if pd.notna(row['rank']) else 999,
            "tracked_at": pd.to_datetime(row['date']).isoformat()
        }
        rankings_to_insert.append(ranking)
        
        # Insertar batch cuando alcancemos el tamaño
        if len(rankings_to_insert) >= batch_size:
            supabase.table('rankings')\
                .upsert(rankings_to_insert, on_conflict='keyword_id,tracked_at')\
                .execute()
            logger.info(f"  ✓ {len(rankings_to_insert)} rankings insertados ({idx+1}/{len(df)})")
            rankings_to_insert = []
    
    # Insertar últimos registros
    if rankings_to_insert:
        supabase.table('rankings')\
            .upsert(rankings_to_insert, on_conflict='keyword_id,tracked_at')\
            .execute()
        logger.info(f"  ✓ {len(rankings_to_insert)} rankings insertados (final)")
    
    logger.info(f"✅ {len(df)} rankings migrados exitosamente")
    
    # 8. Verificación
    logger.info("🔍 Verificando migración...")
    
    result = supabase.table('rankings')\
        .select('id', count='exact')\
        .execute()
    
    total_rankings = result.count
    logger.info(f"📊 Total rankings en Supabase: {total_rankings}")
    
    logger.info("\n" + "="*60)
    logger.info("✅ MIGRACIÓN COMPLETADA")
    logger.info("="*60)
    logger.info(f"👤 Usuario: {admin_email}")
    logger.info(f"📱 App: {app_name} ({app_uuid})")
    logger.info(f"🔑 Keywords: {len(keyword_map)}")
    logger.info(f"📊 Rankings: {total_rankings}")
    logger.info("="*60)
    logger.info("\n💡 Ahora puedes usar el bot en modo Supabase:")
    logger.info("   python bot_telegram_hybrid.py")
    logger.info("\n")


if __name__ == '__main__':
    try:
        migrate_csv_to_supabase()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Migración cancelada por usuario")
    except Exception as e:
        logger.error(f"\n❌ Error durante migración: {e}", exc_info=True)
        sys.exit(1)
