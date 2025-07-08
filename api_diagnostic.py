#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta
import time

def test_api_endpoints():
    """Test different API endpoints and date ranges to diagnose the issue."""
    
    base_url = "https://dev-bettensor-api.azurewebsites.net"
    
    # Test different endpoints
    endpoints = [
        "/Games/TeamGames/Search",
        "/Games/TeamGames",
        "/Games",
        "/api/Games/TeamGames/Search",
        "/api/Games/TeamGames",
        "/api/Games"
    ]
    
    now = datetime.now()
    
    # Test different date ranges
    date_ranges = [
        # Past 30 days (to see if there's any historical data)
        (now - timedelta(days=30), now),
        # Next 30 days
        (now, now + timedelta(days=30)),
        # Next 60 days
        (now, now + timedelta(days=60)),
        # Wide range: past 7 days to future 30 days
        (now - timedelta(days=7), now + timedelta(days=30))
    ]
    
    print(f"Current time: {now}")
    print("=" * 80)
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        print("-" * 50)
        
        url = base_url + endpoint
        
        # First try without date parameters
        try:
            print(f"Testing without date filters...")
            response = requests.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response type: {type(data)}")
                if isinstance(data, list):
                    print(f"Number of items: {len(data)}")
                    if data:
                        print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                        print(f"Sample item: {json.dumps(data[0], indent=2, default=str)[:500]}...")
                elif isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    print(f"Sample response: {json.dumps(data, indent=2, default=str)[:500]}...")
                else:
                    print(f"Response data: {data}")
            else:
                print(f"Error response: {response.text[:200]}")
                
        except Exception as e:
            print(f"Error testing endpoint: {e}")
            
        # Now try with date parameters for the main search endpoint
        if "Search" in endpoint:
            for start_date, end_date in date_ranges:
                try:
                    print(f"\nTesting with date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                    
                    params = {
                        'startDate': start_date.strftime('%Y-%m-%d'),
                        'endDate': end_date.strftime('%Y-%m-%d')
                    }
                    
                    response = requests.get(url, params=params, timeout=30)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"Number of games: {len(data)}")
                            if data:
                                print(f"Sample game: {json.dumps(data[0], indent=2, default=str)[:300]}...")
                        else:
                            print(f"Response: {data}")
                    else:
                        print(f"Error: {response.text[:200]}")
                        
                    time.sleep(0.5)  # Rate limit prevention
                    
                except Exception as e:
                    print(f"Error with date range: {e}")
        
        print("\n" + "="*80)
        time.sleep(1)  # Rate limit prevention between endpoints

if __name__ == "__main__":
    test_api_endpoints()
