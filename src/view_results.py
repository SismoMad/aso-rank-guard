#!/usr/bin/env python3
"""
Visor de resultados de rankings
"""

import pandas as pd
from datetime import datetime
import sys

def show_results():
    try:
        df = pd.read_csv('data/ranks.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        
        # Agrupar por día (ignorar hora/minutos/segundos)
        df['date_only'] = df['date'].dt.date
        
        # Últimos datos (del último día)
        latest_date = df['date_only'].max()
        latest = df[df['date_only'] == latest_date].copy()
        latest = latest.sort_values('rank')
        
        print("\n" + "=" * 80)
        print(f"🛡️  ASO RANK GUARD - RESULTADOS ACTUALES")
        print("=" * 80)
        print(f"📅 Fecha: {latest_date.strftime('%d/%m/%Y %H:%M')}")
        print(f"📱 App: BibleNow (ID: 6749528117)")
        print(f"🌍 Store: US")
        print(f"📊 Keywords monitorizados: {len(latest)}")
        print("=" * 80 + "\n")
        
        # Top keywords
        visible = latest[latest['rank'] < 250]
        invisible = latest[latest['rank'] >= 250]
        
        print(f"✅ Keywords visibles en top 250: {len(visible)}/{len(latest)} ({len(visible)/len(latest)*100:.1f}%)")
        print(f"❌ Keywords no visibles: {len(invisible)}")
        
        if len(visible) > 0:
            avg_rank = visible['rank'].mean()
            best_rank = visible['rank'].min()
            print(f"📈 Ranking promedio: {avg_rank:.1f}")
            print(f"🏆 Mejor ranking: #{int(best_rank)}")
        
        print("\n" + "─" * 80)
        print("🏆 TOP 20 KEYWORDS")
        print("─" * 80 + "\n")
        
        top20 = visible.head(20)
        for idx, (_, row) in enumerate(top20.iterrows(), 1):
            rank = int(row['rank'])
            keyword = row['keyword']
            
            # Emojis según ranking
            if rank <= 10:
                emoji = "🥇"
            elif rank <= 30:
                emoji = "🥈"
            elif rank <= 50:
                emoji = "🥉"
            elif rank <= 100:
                emoji = "🎯"
            else:
                emoji = "📍"
            
            print(f"{emoji} #{rank:3d}  -  {keyword}")
        
        # Keywords críticos
        print("\n" + "─" * 80)
        print("⚠️  KEYWORDS CON PEOR PERFORMANCE (últimos 10 visibles)")
        print("─" * 80 + "\n")
        
        worst10 = visible.tail(10)
        for _, row in worst10.iterrows():
            rank = int(row['rank'])
            keyword = row['keyword']
            print(f"📉 #{rank:3d}  -  {keyword}")
        
        if len(invisible) > 0:
            print("\n" + "─" * 80)
            print(f"❌ KEYWORDS NO VISIBLES (Top 250): {len(invisible)}")
            print("─" * 80 + "\n")
            for _, row in invisible.head(10).iterrows():
                keyword = row['keyword']
                print(f"   • {keyword}")
            
            if len(invisible) > 10:
                print(f"   ... y {len(invisible) - 10} más")
        
        print("\n" + "=" * 80 + "\n")
        
        # Estadísticas por categoría
        print("📊 ESTADÍSTICAS POR CATEGORÍA DE RANKING:\n")
        
        top10_count = len(visible[visible['rank'] <= 10])
        top30_count = len(visible[visible['rank'] <= 30])
        top50_count = len(visible[visible['rank'] <= 50])
        top100_count = len(visible[visible['rank'] <= 100])
        
        print(f"   🥇 Top 10:   {top10_count} keywords")
        print(f"   🥈 Top 30:   {top30_count} keywords")
        print(f"   🥉 Top 50:   {top50_count} keywords")
        print(f"   🎯 Top 100:  {top100_count} keywords")
        print(f"   📍 Top 250:  {len(visible)} keywords")
        
        print("\n" + "=" * 80 + "\n")
        
    except FileNotFoundError:
        print("\n❌ No hay datos disponibles")
        print("   Ejecuta primero: ./run.sh track\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    show_results()
