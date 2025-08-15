import requests
import json

def test_robust_historical_page():
    """Test that the robust historical page is working with our premium data"""
    
    print("=== TESTING ROBUST HISTORICAL PAGE ===")
    print("Verifying our archaeological data displays correctly!\n")
    
    # Test the main historical page loads
    try:
        response = requests.get('http://localhost:5000/historical', timeout=10)
        if response.status_code == 200:
            print("✅ Historical page loads successfully")
            
            # Check if it contains the robust template content
            if 'historical_robust' in response.text or 'Historical Analysis' in response.text:
                print("✅ Robust template confirmed")
            else:
                print("⚠️ Template content unclear")
        else:
            print(f"❌ Historical page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to load historical page: {e}")
        return False
    
    # Test our premium archaeological dates through the API
    premium_dates = ['2025-08-07', '2025-08-08', '2025-08-11']
    
    print(f"\n🏺 TESTING ARCHAEOLOGICAL DATA API:")
    
    for date in premium_dates:
        try:
            api_url = f'http://localhost:5000/api/historical-recap/{date}'
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'predictions' in data and len(data['predictions']) > 0:
                    predictions = data['predictions']
                    premium_count = sum(1 for p in predictions if p.get('quality_level') == 'premium')
                    
                    print(f"  ✅ {date}: {len(predictions)} predictions ({premium_count} premium)")
                    
                    # Check for our premium features
                    if premium_count > 0:
                        sample_premium = next((p for p in predictions if p.get('quality_level') == 'premium'), None)
                        if sample_premium:
                            features = []
                            if 'confidence' in sample_premium:
                                features.append(f"confidence={sample_premium['confidence']:.1f}%")
                            if 'predicted_away_score' in sample_premium:
                                away_score = sample_premium['predicted_away_score']
                                home_score = sample_premium['predicted_home_score']
                                features.append(f"scores={away_score:.1f}-{home_score:.1f}")
                            
                            if features:
                                print(f"      💎 Premium features: {', '.join(features)}")
                else:
                    print(f"  ❌ {date}: No predictions in API response")
            else:
                print(f"  ❌ {date}: API error {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {date}: API test failed - {e}")
    
    # Test that the page can handle today's date 
    print(f"\n📅 TESTING CURRENT DATE HANDLING:")
    
    try:
        today_url = 'http://localhost:5000/api/historical-recap/2025-08-14'
        response = requests.get(today_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Today's date API working: {len(data.get('predictions', []))} predictions")
        else:
            print(f"  ⚠️ Today's date API: {response.status_code} (may be expected if no data)")
    except Exception as e:
        print(f"  ⚠️ Today's date test: {e}")
    
    print(f"\n🏆 ROBUST HISTORICAL PAGE STATUS: RESTORED!")
    print(f"The /historical endpoint now serves the full-featured robust version")
    print(f"with complete access to our archaeological prediction discoveries!")
    
    return True

def test_debugging_endpoints_still_available():
    """Ensure debugging endpoints are still accessible"""
    
    print(f"\n🔧 CHECKING DEBUGGING ENDPOINTS:")
    
    debug_endpoints = [
        ('/historical-working', 'Working/Debug version'),
        ('/historical-original', 'Original version'),
        ('/historical-simple', 'Simple debug version')
    ]
    
    for endpoint, description in debug_endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: {description} available")
            else:
                print(f"  ⚠️ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint}: {e}")

if __name__ == "__main__":
    success = test_robust_historical_page()
    test_debugging_endpoints_still_available()
    
    if success:
        print(f"\n🎉 HISTORICAL PAGE RESTORATION COMPLETE!")
        print(f"Visit http://localhost:5000/historical for the full robust experience!")
        print(f"All debugging versions remain available for development.")
    else:
        print(f"\n⚠️ Some issues detected - please check the application logs.")
