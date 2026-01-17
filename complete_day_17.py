#!/usr/bin/env python3
"""
Completar el día 17 con todos los rankings faltantes
"""
import csv
from datetime import datetime
from src.supabase_client import get_supabase_client

def complete_day_17():
    supabase_wrapper = get_supabase_client()
    supabase = supabase_wrapper.client
    
    # Obtener keywords
    response = supabase.table('keywords').select('id, keyword, country').eq('app_id', 'd30da119-98d7-4c12-9e9f-13f3726c82fe').execute()
    keywords_map = {f"{kw['keyword']}_{kw['country']}": kw['id'] for kw in response.data}
    
    # Procesar días 16 y 17
    for day in [16, 17]:
        print(f"\n{'='*60}")
        print(f"Procesando día {day} de enero")
        print(f"{'='*60}")
        
        # Leer rankings del día del CSV
        rankings_day = []
        with open('data/ranks.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row['date']
                try:
                    tracked_at = datetime.fromisoformat(date_str.replace(' ', 'T'))
                except:
                    tracked_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                
                if tracked_at.day == day:
                    key = f"{row['keyword']}_{row['country']}"
                    keyword_id = keywords_map.get(key)
                    if keyword_id:
                        rankings_day.append({
                            'keyword_id': keyword_id,
                            'rank': int(row['rank']),
                            'tracked_at': tracked_at.isoformat()
                        })
        
        print(f"📊 Rankings del día {day} en CSV: {len(rankings_day)}")
        
        # Usar timestamp único
        timestamp = f'2026-01-{day}T18:00:00+00:00'
        
        # Borrar los del día
        print(f"\n🗑️  Borrando rankings del día {day}...")
        for keyword_id in keywords_map.values():
            supabase.table('rankings').delete().eq('keyword_id', keyword_id).gte('tracked_at', f'2026-01-{day}').lt('tracked_at', f'2026-01-{day+1}').execute()
        
        print("✅ Borrados")
        
        # Insertar todos con el mismo timestamp
        rankings_to_insert = []
        seen_keywords = set()
        
        for r in rankings_day:
            if r['keyword_id'] not in seen_keywords:
                rankings_to_insert.append({
                    'keyword_id': r['keyword_id'],
                    'rank': r['rank'],
                    'tracked_at': timestamp
                })
                seen_keywords.add(r['keyword_id'])
        
        print(f"\n💾 Insertando {len(rankings_to_insert)} rankings únicos...")
        
        # Insertar en lotes de 50
        for i in range(0, len(rankings_to_insert), 50):
            batch = rankings_to_insert[i:i+50]
            supabase.table('rankings').insert(batch).execute()
            print(f"  ✅ {min(i+50, len(rankings_to_insert))}/{len(rankings_to_insert)}")
        
        # Verificar
        result = supabase.table('rankings').select('id').gte('tracked_at', f'2026-01-{day}').lt('tracked_at', f'2026-01-{day+1}').execute()
        print(f"✅ Rankings del día {day} en Supabase: {len(result.data)}")
    
    print("\n" + "="*60)
    print("🎉 Proceso completado!")
    print("="*60)

if __name__ == '__main__':
    complete_day_17()
