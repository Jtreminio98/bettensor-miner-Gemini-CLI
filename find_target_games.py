#!/usr/bin/env python3
"""
Find the specific games that have predictions on the Bettensor website.
Target Game IDs: 351803 (Padres vs Rangers), 352143 (Lynx vs Valkyries)
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta

async def find_target_games():
    """Find the games that actually have predictions."""
    base_url = "https://dev-bettensor-api.azurewebsites.net/"
    
    print("=== Finding Target Games with Predictions ===")
    
    headers = {"Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Search for games from past few days (where predictions might exist)
        print("\n1. Searching for recent games with predictions...")
        
        # Try different date ranges - predictions might be on games from yesterday or a few days ago
        date_ranges = [
            ("today", 0),
            ("yesterday", -1), 
            ("2 days ago", -2),
            ("3 days ago", -3),
            ("1 week ago", -7)
        ]
        
        target_games = {
            "351803": "San Diego Padres vs Texas Rangers",
            "352143": "Minnesota Lynx W vs Golden State Valkyries W"
        }
        
        found_games = {}
        
        for range_name, days_offset in date_ranges:
            print(f"\n--- Checking {range_name} ---")
            
            start_date = (datetime.now(timezone.utc) + timedelta(days=days_offset)).isoformat()
            end_date = (datetime.now(timezone.utc) + timedelta(days=days_offset + 1)).isoformat()
            
            try:
                # Search with different parameters
                params = {
                    "PageIndex": 0,
                    "ItemsPerPage": 100,  # Get more games
                    "SortOrder": "StartDate",
                    "StartDate": start_date,
                    "LeagueFilter": "true",
                }
                
                response = await session.get(
                    f"{base_url}/Games/TeamGames/Search",
                    params=params,
                    headers=headers
                )
                
                if response.status == 200:
                    games = await response.json()
                    print(f"Found {len(games)} games for {range_name}")
                    
                    # Look for our target games
                    for game in games:
                        game_id = str(game.get('externalId', ''))
                        if game_id in target_games:
                            print(f"🎯 FOUND TARGET GAME: {game_id}")
                            print(f"   {game.get('teamA')} vs {game.get('teamB')}")
                            print(f"   Sport: {game.get('sport')}, League: {game.get('league')}")
                            print(f"   Date: {game.get('date')}")
                            print(f"   Game details: {json.dumps(game, indent=2)}")
                            found_games[game_id] = game
                        
                        # Also check for MLB and NBA games with predictions
                        sport = game.get('sport', '').lower()
                        league = game.get('league', '').lower()
                        if ('mlb' in league or 'baseball' in sport or 
                            'nba' in league or 'basketball' in sport):
                            total_predictions = game.get('stats', {}).get('totalPredictionCount', 0)
                            if total_predictions and total_predictions > 0:
                                print(f"⭐ Found {sport}/{league} game with {total_predictions} predictions:")
                                print(f"   ID: {game.get('externalId')} - {game.get('teamA')} vs {game.get('teamB')}")
                
                else:
                    print(f"Error: {response.status}")
                    
            except Exception as e:
                print(f"Error searching {range_name}: {e}")
        
        # Test 2: Try direct API calls for specific game IDs
        print(f"\n2. Trying direct API calls for target game IDs...")
        
        for game_id, description in target_games.items():
            try:
                print(f"\n--- Looking for Game ID {game_id}: {description} ---")
                
                # Try direct game lookup
                response = await session.get(
                    f"{base_url}/Games/TeamGames/{game_id}",
                    headers=headers
                )
                
                print(f"Direct lookup status: {response.status}")
                if response.status == 200:
                    game_data = await response.json()
                    print(f"✅ Found game directly!")
                    print(f"Game data: {json.dumps(game_data, indent=2)}")
                    found_games[game_id] = game_data
                elif response.status == 404:
                    print(f"❌ Game {game_id} not found in API")
                else:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    
            except Exception as e:
                print(f"Error looking up game {game_id}: {e}")
        
        # Test 3: Search with broader parameters
        print(f"\n3. Broader search for popular games...")
        
        try:
            # Search for games with no date filter
            params = {
                "PageIndex": 0,
                "ItemsPerPage": 50,
                "SortOrder": "StartDate",
                "LeagueFilter": "false",  # Don't filter by league
            }
            
            response = await session.get(
                f"{base_url}/Games/TeamGames/Search",
                params=params,
                headers=headers
            )
            
            if response.status == 200:
                games = await response.json()
                print(f"Found {len(games)} games in broad search")
                
                # Look for games with predictions
                games_with_predictions = []
                for game in games:
                    total_predictions = game.get('stats', {}).get('totalPredictionCount', 0)
                    if total_predictions and total_predictions > 0:
                        games_with_predictions.append({
                            'id': game.get('externalId'),
                            'teams': f"{game.get('teamA')} vs {game.get('teamB')}",
                            'sport': game.get('sport'),
                            'league': game.get('league'),
                            'predictions': total_predictions,
                            'date': game.get('date')
                        })
                
                if games_with_predictions:
                    print(f"\n🎯 Found {len(games_with_predictions)} games with predictions:")
                    for game in sorted(games_with_predictions, key=lambda x: x['predictions'], reverse=True)[:10]:
                        print(f"   ID: {game['id']} - {game['teams']} ({game['sport']}/{game['league']}) - {game['predictions']} predictions")
                else:
                    print("❌ No games found with prediction counts > 0")
                    
        except Exception as e:
            print(f"Error in broad search: {e}")
        
        print(f"\n=== Summary ===")
        if found_games:
            print(f"Found {len(found_games)} target games:")
            for game_id, game in found_games.items():
                print(f"  {game_id}: {game.get('teamA')} vs {game.get('teamB')}")
        else:
            print("❌ Target games not found in API")
            print("This suggests the API might be showing different games than the website")
            print("or the website is showing games from a different data source")

if __name__ == "__main__":
    asyncio.run(find_target_games())
