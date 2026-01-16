#!/usr/bin/env python3
"""Script temporal para simular datos de ayer"""
import pandas as pd
from datetime import datetime, timedelta

# Leer datos actuales
df = pd.read_csv('data/ranks.csv')
print(f"📊 Datos actuales: {len(df)} registros")

# Crear datos de ayer
df_yesterday = df.copy()
df_yesterday['date'] = df_yesterday['date'].str.replace('2026-01-15', '2026-01-14')

# Modificar rankings para simular cambios CRÍTICOS
df_yesterday.loc[df_yesterday['keyword'] == 'bible sleep', 'rank'] = 5
df_yesterday.loc[df_yesterday['keyword'] == 'bible sleep stories', 'rank'] = 6
df_yesterday.loc[df_yesterday['keyword'] == 'bedtime bible stories', 'rank'] = 10
df_yesterday.loc[df_yesterday['keyword'] == 'bible for sleep', 'rank'] = 50

# Combinar ayer + hoy
df_combined = pd.concat([df_yesterday, df], ignore_index=True)
df_combined.to_csv('data/ranks.csv', index=False)

print(f"✅ Total después: {len(df_combined)} registros")
print(f"\n🎯 Cambios simulados (ayer → hoy):")
print(f"  🚨 bible sleep: #5 → #19 (caída -14 CRITICAL)")
print(f"  🚨 bible sleep stories: #6 → #16 (caída -10 CRITICAL)")
print(f"  🚨 bedtime bible stories: #10 → #21 (salió del top 10)")
print(f"  🎉 bible for sleep: #50 → #31 (subida +19 CELEBRATION)")
print(f"\n✅ Ahora ejecuta: python src/rank_tracker.py")
