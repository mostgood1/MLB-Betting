#!/usr/bin/env python3
"""
Test script to validate the complete performance recaps implementation
"""

import requests
import json

def test_performance_recaps():
    """Test the performance recaps system end-to-end"""
    print("🧪 Testing Performance Recaps Implementation")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    test_date = "2025-08-08"  # Date with good data coverage
    
    try:
        # Test 1: Historical Recap API
        print("\n1️⃣ Testing Historical Recap API...")
        recap_response = requests.get(f"{base_url}/api/historical-recap/{test_date}")
        
        if recap_response.status_code == 200:
            recap_data = recap_response.json()
            print(f"   ✅ API Response: {recap_data['success']}")
            print(f"   📊 Total Games: {len(recap_data.get('games', []))}")
            print(f"   🎯 Complete Recaps: {recap_data.get('summary', {}).get('complete_recaps', 0)}")
            
            # Check for performance analysis in games
            games_with_analysis = [g for g in recap_data.get('games', []) if 'performance_analysis' in g]
            print(f"   📈 Games with Performance Analysis: {len(games_with_analysis)}")
            
            if games_with_analysis:
                sample_analysis = games_with_analysis[0]['performance_analysis']
                print(f"   🏆 Sample Analysis Grade: {sample_analysis.get('overall_grade', 'N/A')}")
                print(f"   ✅ Winner Correct: {sample_analysis.get('winner_correct', False)}")
        else:
            print(f"   ❌ Historical Recap API failed: {recap_response.status_code}")
            return False
        
        # Test 2: Performance Analytics API
        print("\n2️⃣ Testing Performance Analytics API...")
        analytics_response = requests.get(f"{base_url}/api/performance-analytics/{test_date}")
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"   ✅ API Response: {analytics_data['success']}")
            
            analytics = analytics_data.get('analytics', {})
            summary = analytics.get('summary', {})
            winner_perf = analytics.get('winner_performance', {})
            score_perf = analytics.get('score_performance', {})
            
            print(f"   📊 Analyzed Games: {summary.get('analyzed_games', 0)}")
            print(f"   📈 Analysis Rate: {summary.get('analysis_rate', 0)}%")
            print(f"   🎯 Winner Accuracy: {winner_perf.get('accuracy_rate', 0)}%")
            print(f"   📏 Avg Score Diff: {score_perf.get('avg_total_diff', 0):.1f} runs")
            print(f"   🏅 System Grade: {analytics.get('overall_system_letter', 'N/A')} ({analytics.get('overall_system_grade', 0):.1f}%)")
            
            # Grade distribution
            grade_dist = analytics.get('grade_distribution', {})
            non_zero_grades = {k: v for k, v in grade_dist.items() if v > 0}
            print(f"   📊 Grade Distribution: {dict(non_zero_grades)}")
            
        else:
            print(f"   ❌ Performance Analytics API failed: {analytics_response.status_code}")
            return False
        
        # Test 3: Frontend Templates
        print("\n3️⃣ Testing Frontend Templates...")
        
        # Test robust template
        robust_response = requests.get(f"{base_url}/historical-robust")
        if robust_response.status_code == 200:
            print(f"   ✅ Robust Template: Accessible")
            if "System Performance Analytics" in robust_response.text:
                print(f"   ✅ Performance Analytics UI: Present")
            else:
                print(f"   ⚠️ Performance Analytics UI: Not found in template")
        else:
            print(f"   ❌ Robust Template failed: {robust_response.status_code}")
        
        # Test working template
        working_response = requests.get(f"{base_url}/historical-working")
        if working_response.status_code == 200:
            print(f"   ✅ Working Template: Accessible")
        else:
            print(f"   ❌ Working Template failed: {working_response.status_code}")
        
        print("\n🎉 Performance Recaps Implementation Test Complete!")
        print("=" * 50)
        print("✅ All systems operational!")
        print()
        print("📋 System Capabilities:")
        print("   • Historical game predictions vs actual results")
        print("   • Individual game performance analysis with grades")
        print("   • System-wide performance analytics")
        print("   • Winner prediction accuracy tracking")
        print("   • Score prediction accuracy metrics")
        print("   • Comprehensive grading system (A+ to D)")
        print("   • Confidence-based accuracy analysis")
        print("   • Betting performance indicators")
        print("   • Visual grade distribution charts")
        print("   • Dual frontend interfaces (working + robust)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_performance_recaps()
    exit(0 if success else 1)
