#!/usr/bin/env python3
"""
Vista completa de resultados con comparación de rankings
"""

import pandas as pd
import sys

# Leer datos
df = pd.read_csv('data/ranks.csv')
df['date'] = pd.to_datetime(df['date'])
df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
df['date_only'] = df['date'].dt.date

# Obtener últimas 2 mediciones
unique_dates = sorted(df['date_only'].unique())
latest_date = unique_dates[-1]
previous_date = unique_dates[-2] if len(unique_dates) >= 2 else None

latest = df[df['date_only'] == latest_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
previous = df[df['date_only'] == previous_date].drop_duplicates(subset=['keyword', 'country'], keep='last') if previous_date else pd.DataFrame()

print("\n" + "="*100)
print(f"📊 ANÁLISIS COMPLETO - TODAS LAS KEYWORDS")
print("="*100)
print(f"📅 Comparando: {previous_date} → {latest_date}")
print(f"📊 Keywords tracked: {len(latest)}\n")

# Crear tabla de comparación
results = []
for _, row in latest.iterrows():
    kw = row['keyword']
    rank_now = int(row['rank']) if row['rank'] < 999 else 999
    
    # Buscar rank anterior
    if len(previous) > 0:
        prev_row = previous[previous['keyword'] == kw]
        if len(prev_row) > 0:
            rank_prev = int(prev_row.iloc[0]['rank']) if prev_row.iloc[0]['rank'] < 999 else 999
            delta = rank_prev - rank_now  # Positivo = mejoró
        else:
            rank_prev = None
            delta = None
    else:
        rank_prev = None
        delta = None
    
    results.append({
        'keyword': kw,
        'rank_now': rank_now,
        'rank_prev': rank_prev,
        'delta': delta
    })

# Ordenar por rank actual
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('rank_now')

# Mostrar TOP 50
print("🏆 TOP 50 KEYWORDS (con comparación)\n")
print(f"{'Rank':<6} {'Δ':<8} {'Prev':<6} {'Keyword':<50}")
print("-" * 100)

for _, row in results_df.head(50).iterrows():
    rank = row['rank_now']
    prev = row['rank_prev']
    delta = row['delta']
    kw = row['keyword'][:47]
    
    if rank >= 250:
        continue
        
    # Emoji según delta
    if delta is None:
        delta_str = "NEW"
        emoji = "🆕"
    elif delta > 0:
        delta_str = f"+{int(delta)}"
        emoji = "⬆️" if delta >= 5 else "↗️"
    elif delta < 0:
        delta_str = f"{int(delta)}"
        emoji = "⬇️" if delta <= -5 else "↘️"
    else:
        delta_str = "="
        emoji = "➡️"
    
    prev_str = f"#{int(prev)}" if prev else "—"
    
    print(f"{emoji} #{rank:<4} {delta_str:<6} {prev_str:<6} {kw}")

print("\n" + "="*100)
print(f"\n⬆️  MAYORES SUBIDAS (Top 15)\n")
print(f"{'Keyword':<50} {'Prev':<6} {'Now':<6} {'Δ':<6}")
print("-" * 100)

gainers = results_df[results_df['delta'].notna() & (results_df['delta'] > 0)].sort_values('delta', ascending=False).head(15)
for _, row in gainers.iterrows():
    print(f"{row['keyword'][:47]:<50} #{int(row['rank_prev']):<5} #{int(row['rank_now']):<5} +{int(row['delta'])}")

print("\n" + "="*100)
print(f"\n⬇️  MAYORES CAÍDAS (Top 15)\n")
print(f"{'Keyword':<50} {'Prev':<6} {'Now':<6} {'Δ':<6}")
print("-" * 100)

losers = results_df[results_df['delta'].notna() & (results_df['delta'] < 0)].sort_values('delta').head(15)
for _, row in losers.iterrows():
    print(f"{row['keyword'][:47]:<50} #{int(row['rank_prev']):<5} #{int(row['rank_now']):<5} {int(row['delta'])}")

# Estadísticas
visible = results_df[results_df['rank_now'] < 250]
print("\n" + "="*100)
print("\n📊 ESTADÍSTICAS GENERALES\n")
print(f"✅ Visibles (top 250): {len(visible)}/{len(results_df)} ({len(visible)/len(results_df)*100:.1f}%)")
print(f"📈 Ranking promedio: #{visible['rank_now'].mean():.1f}")
print(f"🏆 Mejor ranking: #{int(visible['rank_now'].min())}")
print(f"\nDistribución:")
print(f"  🥇 Top 10:  {len(visible[visible['rank_now'] <= 10])} keywords")
print(f"  🥈 Top 30:  {len(visible[visible['rank_now'] <= 30])} keywords")
print(f"  🥉 Top 50:  {len(visible[visible['rank_now'] <= 50])} keywords")
print(f"  🎯 Top 100: {len(visible[visible['rank_now'] <= 100])} keywords")

print("\n" + "="*100)
