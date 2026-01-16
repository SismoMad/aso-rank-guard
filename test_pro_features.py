#!/usr/bin/env python3
"""
Test Suite para ASO Rank Guard PRO Features
Tests rápidos de cada módulo nuevo
"""

import sys
import yaml
from pathlib import Path

def test_competitor_tracker():
    """Test Competitor Tracker"""
    print("🧪 Testing Competitor Tracker...")
    try:
        from src.competitor_tracker import CompetitorTracker
        
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)
        
        tracker = CompetitorTracker(config)
        
        # Test con 1 keyword
        test_keywords = config['keywords'][:1]
        results = tracker.track_all_competitors(keywords=test_keywords)
        
        assert len(results) > 0, "No competitors found"
        
        print(f"   ✅ OK - Found {len(results)} competitors")
        return True
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        return False


def test_ab_testing():
    """Test A/B Testing Tracker"""
    print("🧪 Testing A/B Testing Tracker...")
    try:
        from src.ab_testing_tracker import ABTestingTracker
        
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)
        
        tracker = ABTestingTracker(config)
        
        # Crear experimento test
        baseline = {
            'avg_rank': 45.5,
            'top_10_count': 2,
            'visibility_rate': 75.0,
            'keyword_ranks': {'test': 45}
        }
        
        exp = tracker.create_experiment(
            name="Test Experiment",
            hypothesis="Test hypothesis",
            change_type="subtitle",
            description="Test description",
            baseline_metrics=baseline
        )
        
        assert exp is not None, "Failed to create experiment"
        
        print(f"   ✅ OK - Created experiment: {exp.name}")
        return True
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        return False


def test_keyword_discovery():
    """Test Keyword Discovery Engine"""
    print("🧪 Testing Keyword Discovery Engine...")
    try:
        from src.keyword_discovery import KeywordDiscoveryEngine
        
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)
        
        engine = KeywordDiscoveryEngine(config)
        
        # Test long-tail generation
        base_keywords = ['bible stories', 'audio bible']
        discoveries = engine.discover_long_tail_variations(base_keywords)
        
        assert len(discoveries) > 0, "No discoveries found"
        
        print(f"   ✅ OK - Discovered {len(discoveries)} variations")
        return True
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        return False


def test_seasonal_patterns():
    """Test Seasonal Patterns Detector"""
    print("🧪 Testing Seasonal Patterns Detector...")
    try:
        from src.seasonal_patterns import SeasonalPatternsDetector
        
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)
        
        detector = SeasonalPatternsDetector(config)
        
        # Test analysis (puede fallar si no hay datos suficientes)
        analysis = detector.analyze_all_keywords(min_history_days=1)
        
        if 'error' in analysis:
            print(f"   ⚠️  OK (no hay datos suficientes) - {analysis['error']}")
        else:
            print(f"   ✅ OK - Analyzed {analysis['analyzed_keywords']} keywords")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        return False


def test_cost_calculator():
    """Test Cost Calculator"""
    print("🧪 Testing Cost Calculator...")
    try:
        from src.cost_calculator import CostCalculator
        
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)
        
        calculator = CostCalculator(config)
        
        # Test opportunity cost
        opp = calculator.calculate_opportunity_cost(
            current_rank=35,
            target_rank=10,
            keyword_volume=200
        )
        
        assert 'monthly_opportunity_cost' in opp, "Missing opportunity cost"
        assert opp['monthly_opportunity_cost'] > 0, "Invalid opportunity cost"
        
        print(f"   ✅ OK - Calculated ${opp['monthly_opportunity_cost']:.2f}/month opportunity")
        return True
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        return False


def test_dashboard_generator():
    """Test Dashboard Generator"""
    print("🧪 Testing Dashboard Generator...")
    try:
        from src.dashboard_generator import InteractiveDashboard
        
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)
        
        dashboard = InteractiveDashboard(config)
        
        # Test HTML generation
        html = dashboard.generate_html()
        
        assert len(html) > 1000, "HTML too short"
        assert '<html' in html.lower(), "Invalid HTML"
        
        print(f"   ✅ OK - Generated {len(html)} bytes of HTML")
        return True
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("🧪 ASO RANK GUARD PRO - TEST SUITE")
    print("="*60)
    print()
    
    tests = [
        ("Competitor Tracker", test_competitor_tracker),
        ("A/B Testing Tracker", test_ab_testing),
        ("Keyword Discovery", test_keyword_discovery),
        ("Seasonal Patterns", test_seasonal_patterns),
        ("Cost Calculator", test_cost_calculator),
        ("Dashboard Generator", test_dashboard_generator),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"   💥 CRITICAL FAIL - {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        emoji = "✅" if success else "❌"
        print(f"{emoji} {name}")
    
    print()
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
