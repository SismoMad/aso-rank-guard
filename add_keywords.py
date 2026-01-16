#!/usr/bin/env python3
"""
Script para añadir keywords al config.yaml automáticamente
Uso: python3 add_keywords.py "keyword1" "keyword2" ...
"""

import sys
import yaml
from pathlib import Path

def add_keywords(new_keywords):
    """Añadir keywords al config.yaml"""
    config_path = Path(__file__).parent / 'config' / 'config.yaml'
    
    # Leer config actual
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Obtener keywords actuales
    current_keywords = set(config.get('keywords', []))
    initial_count = len(current_keywords)
    
    # Añadir nuevas keywords (convertir a lowercase y eliminar duplicados)
    new_keywords_clean = [kw.lower().strip() for kw in new_keywords]
    added = []
    
    for kw in new_keywords_clean:
        if kw and kw not in current_keywords:
            current_keywords.add(kw)
            added.append(kw)
    
    if not added:
        print("❌ No hay keywords nuevas para añadir (ya existen)")
        return False
    
    # Actualizar config
    config['keywords'] = sorted(list(current_keywords))
    
    # Guardar config
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Keywords añadidas: {len(added)}")
    for kw in added:
        print(f"   ➕ {kw}")
    print(f"\n📊 Total keywords: {initial_count} → {len(current_keywords)}")
    print(f"\n💡 Ejecuta 'python3 src/rank_tracker.py' para trackearlas")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Uso: python3 add_keywords.py 'keyword1' 'keyword2' ...")
        print("\nEjemplo:")
        print("  python3 add_keywords.py 'bible app' 'christian meditation'")
        sys.exit(1)
    
    keywords = sys.argv[1:]
    add_keywords(keywords)
