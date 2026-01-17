#!/usr/bin/env python3
"""
Track keywords in App Store and save rankings to Supabase
"""
import json
import urllib.request
import time
import os
from datetime import datetime
from supabase import create_client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
APP_ID = 'd30da119-98d7-4c12-9e9f-13f3726c82fe'
APP_STORE_ID = 6749528117

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

def search_keyword_rank(keyword: str, country: str) -> int | None:
    """Search for app rank in App Store for a keyword"""
    search_term = keyword.replace(" ", "+")
    url = f"https://itunes.apple.com/search?term={search_term}&country={country}&entity=software&limit=200"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
        
        for idx, app in enumerate(data.get('results', []), 1):
            if app.get('trackId') == APP_STORE_ID:
                return idx
        
        return None  # Not found in top 200
        
    except Exception as e:
        print(f"⚠️  Error searching {keyword}: {e}")
        return None

def track_all_keywords():
    """Track all active keywords and save to Supabase"""
    
    # Get active keywords
    result = supabase.table('keywords').select('id, keyword, country').eq('app_id', APP_ID).eq('is_active', True).execute()
    
    keywords = result.data
    print(f"\n🔍 Tracking {len(keywords)} keywords...\n")
    
    rankings_to_insert = []
    
    for idx, kw in enumerate(keywords, 1):  # Track ALL keywords
        keyword_id = kw['id']
        keyword = kw['keyword']
        country = kw['country']
        
        rank = search_keyword_rank(keyword, country)
        
        if rank:
            print(f"✅ [{idx}/{len(keywords)}] {keyword[:40]:40} ({country}) → Rank {rank}")
            rankings_to_insert.append({
                'keyword_id': keyword_id,
                'rank': rank,
                'tracked_at': datetime.now().isoformat()
            })
        else:
            print(f"❌ [{idx}/{len(keywords)}] {keyword[:40]:40} ({country}) → Not in top 200")
            rankings_to_insert.append({
                'keyword_id': keyword_id,
                'rank': 999,  # Use 999 for "not found"
                'tracked_at': datetime.now().isoformat()
            })
        
        time.sleep(2)  # Rate limiting (increased to avoid throttling)
    
    # Save all rankings to Supabase
    if rankings_to_insert:
        result = supabase.table('rankings').insert(rankings_to_insert).execute()
        print(f"\n💾 Saved {len(rankings_to_insert)} rankings to Supabase")
        
        # Show summary
        summary = supabase.rpc('get_app_stats', {'p_app_id': APP_ID}).execute()
        print(f"\n📊 STATS: {json.dumps(summary.data, indent=2)}")

if __name__ == '__main__':
    track_all_keywords()
