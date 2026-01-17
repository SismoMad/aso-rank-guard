#!/usr/bin/env python3
"""
Importar datos históricos del CSV a Supabase
"""
import csv
from datetime import datetime
from src.supabase_client import get_supabase_client

def import_csv_rankings():
    supabase_wrapper = get_supabase_client()
    supabase = supabase_wrapper.client  # Acceder al client interno
    
    # Obtener todas las keywords de la app BibleNow
    print("📋 Obteniendo keywords de Supabase...")
    response = supabase.table('keywords').select('id, keyword, country').eq('app_id', 'd30da119-98d7-4c12-9e9f-13f3726c82fe').execute()
    
    keywords_map = {}
    for kw in response.data:
        # Crear key con keyword+country para hacer match exacto
        key = f"{kw['keyword']}_{kw['country']}"
        keywords_map[key] = kw['id']
    
    print(f"✅ {len(keywords_map)} keywords encontradas en Supabase")
    
    # Leer CSV
    print("\n📂 Leyendo CSV...")
    rankings_to_insert = []
    dates_found = set()
    
    with open('data/ranks.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row['date']
            keyword = row['keyword']
            country = row['country']
            rank = int(row['rank'])
            
            # Parsear fecha
            try:
                tracked_at = datetime.fromisoformat(date_str.replace(' ', 'T'))
            except:
                tracked_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
            
            date_only = tracked_at.date()
            dates_found.add(date_only)
            
            # Solo importar fechas 14, 15, 16, 17 de enero
            if date_only.day not in [14, 15, 16, 17]:
                continue
            
            # Buscar keyword_id
            key = f"{keyword}_{country}"
            keyword_id = keywords_map.get(key)
            
            if not keyword_id:
                print(f"⚠️  Keyword no encontrada en Supabase: {keyword} ({country})")
                continue
            
            rankings_to_insert.append({
                'keyword_id': keyword_id,
                'rank': rank,
                'tracked_at': tracked_at.isoformat()
            })
    
    print(f"\n📅 Fechas encontradas en CSV: {sorted(dates_found)}")
    print(f"📊 Rankings a importar (14 y 15 enero): {len(rankings_to_insert)}")
    
    if not rankings_to_insert:
        print("❌ No hay datos para importar")
        return
    
    # Insertar en lotes de 100
    print("\n💾 Insertando en Supabase...")
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(rankings_to_insert), batch_size):
        batch = rankings_to_insert[i:i+batch_size]
        try:
            supabase.table('rankings').insert(batch).execute()
            total_inserted += len(batch)
            print(f"  ✅ Insertados {total_inserted}/{len(rankings_to_insert)} rankings...")
        except Exception as e:
            print(f"  ❌ Error en lote {i//batch_size + 1}: {e}")
    
    print(f"\n🎉 Importación completada: {total_inserted} rankings insertados")
    
    # Verificar fechas en Supabase
    print("\n🔍 Verificando fechas en Supabase...")
    result = supabase.rpc('execute_sql', {
        'query': '''
            SELECT DATE(tracked_at) as fecha, COUNT(*) as cantidad 
            FROM rankings 
            WHERE keyword_id IN (SELECT id FROM keywords WHERE app_id = 'd30da119-98d7-4c12-9e9f-13f3726c82fe')
            GROUP BY DATE(tracked_at)
            ORDER BY fecha DESC
        '''
    }).execute()
    
    if result.data:
        for row in result.data:
            print(f"  📅 {row['fecha']}: {row['cantidad']} rankings")

if __name__ == '__main__':
    import_csv_rankings()
