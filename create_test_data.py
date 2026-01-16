#!/usr/bin/env python3
"""Script para crear datos de test con cambios claros"""
import pandas as pd
from datetime import datetime, timedelta

# Leer backup limpio
df_today = pd.read_csv('data/ranks.csv')
print(f"📊 Datos de hoy: {len(df_today)} registros")

# Crear datos de ayer (mismo contenido pero ayer)
df_yesterday = df_today.copy()

# Cambiar TODAS las fechas a ayer con misma hora
yesterday_base = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-% d')
for idx, row in df_yesterday.iterrows():
    old_date = row['date']
    # Mantener hora pero cambiar día
    new_date = old_date.replace('2026-01-15', '2026-01-14')
    df_yesterday.at[idx, 'date'] = new_date

# MODIFICAR rankings para ayer (simular que ayer estaban mejor)
df_yesterday.loc[df_yesterday['keyword'] == 'bible sleep', 'rank'] = 5  # hoy 19
df_yesterday.loc[df_yesterday['keyword'] == 'bible sleep stories', 'rank'] = 6  # hoy 16
df_yesterday.loc[df_yesterday['keyword'] == 'bedtime bible stories', 'rank'] = 10  # hoy 21
df_yesterday.loc[df_yesterday['keyword'] == 'bible for sleep', 'rank'] = 50  # hoy 31

# Combinar: AYER primero, luego HOY
df_combined = pd.concat([df_yesterday, df_today], ignore_index=True)

# Guardar
df_combined.to_csv('data/ranks.csv', index=False)

print(f"✅ CSV creado con {len(df_combined)} registros")
print(f"   - Ayer (2026-01-14): {len(df_yesterday)} registros")
print(f"   - Hoy (2026-01-15): {len(df_today)} registros")
print(f"\n🎯 Cambios que se detectarán:")
print(f"   🚨 CRITICAL: bible sleep #5→#19 (-14)")
print(f"   🚨 CRITICAL: bible sleep stories #6→#16 (-10)")
print(f"   🚨 CRITICAL: bedtime bible stories #10→#21 (salió top 10)")  
print(f"   🎉 CELEBRATION: bible for sleep #50→#31 (+19)")
print(f"\n✅ Ahora ejecuta: python src/auto_notifier.py")
