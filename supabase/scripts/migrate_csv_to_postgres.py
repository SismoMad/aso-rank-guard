#!/usr/bin/env python3
"""
Supabase Data Migration Script
Migrates CSV data from ASO Rank Guard to Supabase PostgreSQL

Usage:
    python3 migrate_csv_to_postgres.py --supabase-url YOUR_URL --supabase-key YOUR_KEY
    
Requirements:
    pip install supabase pandas python-dotenv
"""

import csv
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List
import pandas as pd

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install supabase pandas python-dotenv")
    sys.exit(1)

# Cargar variables de entorno
load_dotenv()

class SupabaseMigration:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.user_id = None
        self.app_id = None
        self.keyword_map = {}  # keyword text -> UUID
        
    def migrate_all(self, user_email: str):
        """Execute full migration"""
        print("🚀 Starting Supabase migration...\n")
        
        # 1. Create user profile (or get existing)
        print("👤 Step 1: Creating user profile...")
        self.user_id = self.create_user_profile(user_email)
        print(f"   ✅ User ID: {self.user_id}\n")
        
        # 2. Create app from config.yaml
        print("📱 Step 2: Creating app...")
        self.app_id = self.create_app_from_config()
        print(f"   ✅ App ID: {self.app_id}\n")
        
        # 3. Create keywords from config.yaml
        print("🔑 Step 3: Migrating keywords from config.yaml...")
        keyword_count = self.create_keywords_from_config()
        print(f"   ✅ Created {keyword_count} keywords\n")
        
        # 4. Migrate rankings from CSV
        print("📊 Step 4: Migrating rankings from CSV...")
        ranking_count = self.migrate_rankings_from_csv()
        print(f"   ✅ Migrated {ranking_count} rankings\n")
        
        # 5. Create default alerts
        print("🔔 Step 5: Creating default alerts...")
        alert_count = self.create_default_alerts()
        print(f"   ✅ Created {alert_count} alerts\n")
        
        print("🎉 Migration completed successfully!")
        print(f"\n📈 Summary:")
        print(f"   - User: {user_email}")
        print(f"   - Apps: 1")
        print(f"   - Keywords: {keyword_count}")
        print(f"   - Rankings: {ranking_count}")
        print(f"   - Alerts: {alert_count}")
        
    def create_user_profile(self, email: str) -> str:
        """Create or get user profile"""
        # Nota: En producción, esto debe hacerse via Supabase Auth signup
        # Aquí asumimos que el usuario YA está autenticado
        # Este script debe ejecutarse CON el service_role key para insertar datos
        
        # Intentar obtener usuario existente por email
        result = self.supabase.table('profiles').select('id').eq('email', email).execute()
        
        if result.data:
            return result.data[0]['id']
        
        # Si no existe, necesitamos crearlo (requiere service_role key)
        # En producción, esto se haría mediante signup de Supabase Auth
        print("   ⚠️  Usuario no encontrado. Debes crear la cuenta primero via Supabase Auth")
        print("   ℹ️  Ejecuta: supabase auth signup --email", email)
        sys.exit(1)
    
    def create_app_from_config(self) -> str:
        """Create app from config.yaml"""
        import yaml
        
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        app_data = {
            'user_id': self.user_id,
            'name': config['app']['name'],
            'bundle_id': config['app']['bundle_id'],
            'platform': 'ios',  # Asumiendo iOS por el bundle_id format
            'country': config['countries'][0],  # Primer país configurado
            'is_active': True
        }
        
        # Verificar si ya existe
        result = self.supabase.table('apps').select('id').eq('bundle_id', app_data['bundle_id']).eq('user_id', self.user_id).execute()
        
        if result.data:
            return result.data[0]['id']
        
        # Crear nuevo app
        result = self.supabase.table('apps').insert(app_data).execute()
        return result.data[0]['id']
    
    def create_keywords_from_config(self) -> int:
        """Create keywords from config.yaml"""
        import yaml
        
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        keywords = config['keywords']
        created_count = 0
        
        for keyword in keywords:
            keyword_data = {
                'app_id': self.app_id,
                'keyword': keyword,
                'is_active': True
            }
            
            # Verificar si ya existe
            result = self.supabase.table('keywords').select('id, keyword').eq('app_id', self.app_id).eq('keyword', keyword).execute()
            
            if result.data:
                # Ya existe, guardar mapping
                self.keyword_map[keyword] = result.data[0]['id']
                continue
            
            # Crear nuevo keyword
            result = self.supabase.table('keywords').insert(keyword_data).execute()
            self.keyword_map[keyword] = result.data[0]['id']
            created_count += 1
            
            if created_count % 10 == 0:
                print(f"   📝 {created_count}/{len(keywords)} keywords created...")
        
        return created_count
    
    def migrate_rankings_from_csv(self) -> int:
        """Migrate rankings from CSV"""
        csv_path = 'data/ranks.csv'
        
        if not os.path.exists(csv_path):
            print(f"   ⚠️  CSV file not found: {csv_path}")
            return 0
        
        # Leer CSV
        df = pd.read_csv(csv_path)
        total_rows = len(df)
        
        print(f"   📄 Found {total_rows} rankings in CSV")
        
        batch_size = 100
        created_count = 0
        skipped_count = 0
        
        # Procesar en lotes
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            rankings_batch = []
            
            for _, row in batch.iterrows():
                keyword = row['keyword']
                
                # Obtener keyword_id del mapping
                if keyword not in self.keyword_map:
                    skipped_count += 1
                    continue
                
                ranking_data = {
                    'keyword_id': self.keyword_map[keyword],
                    'rank': int(row['rank']),
                    'tracked_at': row['date']
                }
                
                rankings_batch.append(ranking_data)
            
            # Insertar lote (on_conflict='ignore' para evitar duplicados)
            if rankings_batch:
                try:
                    self.supabase.table('rankings').upsert(rankings_batch, on_conflict='keyword_id,tracked_at').execute()
                    created_count += len(rankings_batch)
                    print(f"   📊 {created_count}/{total_rows} rankings migrated...")
                except Exception as e:
                    print(f"   ⚠️  Error inserting batch: {e}")
        
        if skipped_count > 0:
            print(f"   ℹ️  Skipped {skipped_count} rankings (keyword not found)")
        
        return created_count
    
    def create_default_alerts(self) -> int:
        """Create default alert configurations"""
        import yaml
        
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        alerts_config = config['alerts']
        alerts = []
        
        # Alerta de caída significativa
        alerts.append({
            'user_id': self.user_id,
            'app_id': self.app_id,
            'alert_type': 'rank_drop',
            'is_active': True,
            'telegram_enabled': alerts_config['telegram']['enabled'],
            'threshold': alerts_config['drop_threshold']
        })
        
        # Alerta de mejora significativa
        alerts.append({
            'user_id': self.user_id,
            'app_id': self.app_id,
            'alert_type': 'rank_gain',
            'is_active': True,
            'telegram_enabled': alerts_config['telegram']['enabled'],
            'threshold': alerts_config['rise_threshold']
        })
        
        # Resumen diario (si está habilitado)
        if alerts_config['daily_summary']['enabled']:
            alerts.append({
                'user_id': self.user_id,
                'app_id': self.app_id,
                'alert_type': 'daily_summary',
                'is_active': True,
                'telegram_enabled': alerts_config['telegram']['enabled']
            })
        
        # Insertar alertas
        result = self.supabase.table('alerts').insert(alerts).execute()
        return len(result.data)

def main():
    parser = argparse.ArgumentParser(description='Migrate ASO Rank Guard data to Supabase')
    parser.add_argument('--supabase-url', help='Supabase project URL', default=os.getenv('SUPABASE_URL'))
    parser.add_argument('--supabase-key', help='Supabase service role key (NOT anon key!)', default=os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
    parser.add_argument('--email', help='User email for migration', default=os.getenv('USER_EMAIL'))
    
    args = parser.parse_args()
    
    # Validar parámetros
    if not args.supabase_url:
        print("❌ Missing --supabase-url or SUPABASE_URL env variable")
        sys.exit(1)
    
    if not args.supabase_key:
        print("❌ Missing --supabase-key or SUPABASE_SERVICE_ROLE_KEY env variable")
        sys.exit(1)
    
    if not args.email:
        print("❌ Missing --email or USER_EMAIL env variable")
        sys.exit(1)
    
    # Confirmar migración
    print("⚠️  WARNING: This will migrate data to Supabase")
    print(f"   Project: {args.supabase_url}")
    print(f"   Email: {args.email}")
    response = input("\n   Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Ejecutar migración
    migrator = SupabaseMigration(args.supabase_url, args.supabase_key)
    migrator.migrate_all(args.email)

if __name__ == '__main__':
    main()
