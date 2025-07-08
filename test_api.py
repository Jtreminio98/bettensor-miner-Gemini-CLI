#!/usr/bin/env python3
"""
Script to test the Bettensor API directly and see what data is available.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta

async def test_bettensor_api():
    """Test the Bettensor API to see what data is available."""
    base_url = "https://dev-bettensor-api.azurewebsites.net/"
    
    print("=== Testing Bettensor API ===")
    
    # Test without API key first
    headers = {"Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Try to get games without authentication
        print("\n1. Testing games endpoint without authentication...")
        try:
            start_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            params = {
                "PageIndex": 0,
                "ItemsPerPage": 10,
                "SortOrder": "StartDate",
                "StartDate": start_date,
                "LeagueFilter": "true",
            }
            
            response = await session.get(
                f"{base_url}/Games/TeamGames/Search",
                params=params,
                headers=headers
            )
            
            print(f"Status: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"Success! Received {len(data)} games")
                if data:
                    print(f"Sample game: {json.dumps(data[0], indent=2)}")
            else:
                text = await response.text()
                print(f"Error response: {text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: Try to get a simple endpoint
        print("\n2. Testing base endpoint...")
        try:
            response = await session.get(f"{base_url}")
            print(f"Base URL status: {response.status}")
            text = await response.text()
            print(f"Response (first 200 chars): {text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
            
        # Test 3: Check what endpoints are available
        print("\n3. Testing other possible endpoints...")
        endpoints_to_test = [
            "/api/games",
            "/games", 
            "/Games",
            "/Games/TeamGames",
            "/health",
            "/status"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = await session.get(f"{base_url}{endpoint}")
                print(f"{endpoint}: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    print(f"  Content length: {len(text)}")
            except Exception as e:
                print(f"{endpoint}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_bettensor_api())
