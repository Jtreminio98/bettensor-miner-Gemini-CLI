#!/usr/bin/env python3
"""
Check Specific Game IDs and Explore Trending Games
=================================================

This script checks if the specific game IDs you mentioned are present in the 
Bettensor API data and explores alternative ways to find trending games with
many predictions.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

class BettensorGameChecker:
    """Checks for specific games and explores trending game discovery methods."""
    
    def __init__(self, api_base_url: str = "https://dev-bettensor-api.azurewebsites.net"):
        self.api_base_url = api_base_url
        self.headers = {"Content-Type": "application/json"}
    
    async def check_specific_games(self, game_ids: List[str]) -> Dict:
        """Check if specific game IDs exist in the API data."""
        print(f"🔍 Checking for specific game IDs: {game_ids}")
        
        # First, get all games from the API (broader search)
        all_games = await self._fetch_all_games()
        
        results = {
            "found_games": [],
            "missing_games": [],
            "games_with_predictions": [],
            "total_games_checked": len(all_games)
        }
        
        # Create a lookup dictionary for faster searching
        games_by_id = {str(game.get('externalId', '')): game for game in all_games}
        
        for game_id in game_ids:
            if game_id in games_by_id:
                game = games_by_id[game_id]
                prediction_count = game.get('stats', {}).get('totalPredictionCount', 0)
                
                game_info = {
                    "game_id": game_id,
                    "team_a": game.get('teamA', ''),
                    "team_b": game.get('teamB', ''),
                    "sport": game.get('sport', ''),
                    "league": game.get('league', ''),
                    "date": game.get('date', ''),
                    "prediction_count": prediction_count,
                    "full_game_data": game
                }
                
                results["found_games"].append(game_info)
                
                if prediction_count > 0:
                    results["games_with_predictions"].append(game_info)
                    
                print(f"✅ Found {game_id}: {game_info['team_a']} vs {game_info['team_b']} - {prediction_count} predictions")
            else:
                results["missing_games"].append(game_id)
                print(f"❌ Game ID {game_id} not found in API data")
        
        return results
    
    async def explore_trending_endpoints(self) -> Dict:
        """Explore alternative API endpoints that might contain trending games."""
        print("🔍 Exploring alternative API endpoints for trending games...")
        
        endpoints_to_try = [
            "/Games/TeamGames/Search",
            "/Games/TeamGames/GetTrendingGames",
            "/Games/TeamGames/GetHotGames",
            "/Games/TeamGames/GetPopularGames",
            "/Games/TeamGames/GetMostPredicted",
            "/Games/TeamGames/GetActiveGames",
            "/Games/TeamGames/GetLiveGames",
            "/Games/TeamGames/GetUpcomingGames",
            "/Games/TeamGames/GetRecentGames",
            "/Games/TeamGames/GetFeaturedGames",
            "/Games/TeamGames/GetTopGames",
            "/Games/TeamGames/GetGamesByPredictionCount",
            "/Games/TeamGames/GetGameStats",
            "/Games/TeamGames/GetGamePredictions",
            "/Games/TeamGames/GetGamesByPopularity",
            "/Games/TeamGames/GetGamesByActivity",
            "/Games/GetTrendingGames",
            "/Games/GetHotGames",
            "/Games/GetPopularGames",
            "/Games/GetMostPredicted",
            "/Games/GetActiveGames",
            "/Games/GetLiveGames",
            "/Games/GetUpcomingGames",
            "/Games/GetRecentGames",
            "/Games/GetFeaturedGames",
            "/Games/GetTopGames",
            "/Games/GetGamesByPredictionCount",
            "/Games/GetGameStats",
            "/Games/GetGamePredictions",
            "/Games/GetGamesByPopularity",
            "/Games/GetGamesByActivity",
            "/Predictions/GetTrendingPredictions",
            "/Predictions/GetHotPredictions",
            "/Predictions/GetPopularPredictions",
            "/Predictions/GetMostActivePredictions",
            "/Predictions/GetRecentPredictions",
            "/Predictions/GetFeaturedPredictions",
            "/Predictions/GetTopPredictions",
            "/Predictions/GetPredictionsByGameId",
            "/Predictions/GetPredictionsByPopularity",
            "/Predictions/GetPredictionsByActivity",
            "/Stats/GetTrendingStats",
            "/Stats/GetHotStats",
            "/Stats/GetPopularStats",
            "/Stats/GetMostActiveStats",
            "/Stats/GetRecentStats",
            "/Stats/GetFeaturedStats",
            "/Stats/GetTopStats",
            "/Stats/GetStatsByGameId",
            "/Stats/GetStatsByPopularity",
            "/Stats/GetStatsByActivity"
        ]
        
        results = {
            "working_endpoints": [],
            "error_endpoints": [],
            "rate_limited_endpoints": [],
            "promising_endpoints": []
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints_to_try:
                try:
                    print(f"  Testing: {endpoint}")
                    
                    # Try with basic parameters first
                    response = await session.get(
                        f"{self.api_base_url}{endpoint}",
                        headers=self.headers
                    )
                    
                    if response.status == 200:
                        data = await response.json()
                        results["working_endpoints"].append({
                            "endpoint": endpoint,
                            "status": response.status,
                            "data_length": len(data) if isinstance(data, list) else 1,
                            "sample_data": data[:2] if isinstance(data, list) and len(data) > 0 else data
                        })
                        print(f"    ✅ {endpoint} - Status: {response.status}, Data length: {len(data) if isinstance(data, list) else 1}")
                        
                        # Check if this endpoint has games with predictions
                        if isinstance(data, list) and len(data) > 0:
                            games_with_predictions = [
                                game for game in data 
                                if isinstance(game, dict) and 
                                game.get('stats', {}).get('totalPredictionCount', 0) > 0
                            ]
                            if games_with_predictions:
                                results["promising_endpoints"].append({
                                    "endpoint": endpoint,
                                    "games_with_predictions": len(games_with_predictions),
                                    "sample_games": games_with_predictions[:3]
                                })
                                print(f"    🎯 {endpoint} - Found {len(games_with_predictions)} games with predictions!")
                    
                    elif response.status == 429:
                        results["rate_limited_endpoints"].append(endpoint)
                        print(f"    ⏱️ {endpoint} - Rate limited")
                        await asyncio.sleep(2)  # Brief pause for rate limiting
                    
                    else:
                        results["error_endpoints"].append({
                            "endpoint": endpoint,
                            "status": response.status
                        })
                        print(f"    ❌ {endpoint} - Status: {response.status}")
                
                except Exception as e:
                    results["error_endpoints"].append({
                        "endpoint": endpoint,
                        "error": str(e)
                    })
                    print(f"    ❌ {endpoint} - Error: {e}")
                
                # Small delay between requests to avoid rate limiting
                await asyncio.sleep(0.5)
        
        return results
    
    async def check_prediction_data_directly(self, game_ids: List[str]) -> Dict:
        """Try to query prediction data directly for specific game IDs."""
        print(f"🔍 Checking prediction data directly for game IDs: {game_ids}")
        
        results = {
            "games_with_prediction_data": [],
            "games_without_prediction_data": [],
            "errors": []
        }
        
        prediction_endpoints = [
            "/Predictions/GetPredictionsByGameId",
            "/Games/TeamGames/GetGamePredictions",
            "/Stats/GetStatsByGameId"
        ]
        
        async with aiohttp.ClientSession() as session:
            for game_id in game_ids:
                for endpoint in prediction_endpoints:
                    try:
                        print(f"  Testing {endpoint} for game {game_id}")
                        
                        # Try different parameter formats
                        params_to_try = [
                            {"gameId": game_id},
                            {"game_id": game_id},
                            {"externalId": game_id},
                            {"id": game_id},
                            {"GameId": game_id},
                            {"Game_Id": game_id},
                            {"ExternalId": game_id},
                            {"Id": game_id}
                        ]
                        
                        for params in params_to_try:
                            response = await session.get(
                                f"{self.api_base_url}{endpoint}",
                                params=params,
                                headers=self.headers
                            )
                            
                            if response.status == 200:
                                data = await response.json()
                                if data and (isinstance(data, list) and len(data) > 0 or isinstance(data, dict)):
                                    results["games_with_prediction_data"].append({
                                        "game_id": game_id,
                                        "endpoint": endpoint,
                                        "params": params,
                                        "data": data
                                    })
                                    print(f"    ✅ Found prediction data for {game_id} at {endpoint}")
                                    break
                            
                            await asyncio.sleep(0.2)  # Small delay
                        
                        await asyncio.sleep(0.5)  # Delay between endpoints
                        
                    except Exception as e:
                        results["errors"].append({
                            "game_id": game_id,
                            "endpoint": endpoint,
                            "error": str(e)
                        })
        
        return results
    
    async def _fetch_all_games(self, max_days_back: int = 30, max_days_forward: int = 30) -> List[Dict]:
        """Fetch all games from the API (past and future)."""
        print(f"📡 Fetching all games from {max_days_back} days back to {max_days_forward} days forward...")
        
        all_games = []
        current_time = datetime.now(timezone.utc)
        
        async with aiohttp.ClientSession() as session:
            # Get games from the past
            start_date = (current_time - timedelta(days=max_days_back)).isoformat()
            end_date = (current_time + timedelta(days=max_days_forward)).isoformat()
            
            try:
                params = {
                    "PageIndex": 0,
                    "ItemsPerPage": 200,  # Get maximum games per request
                    "SortOrder": "StartDate",
                    "StartDate": start_date,
                    "EndDate": end_date,
                    "LeagueFilter": "false",
                }
                
                print(f"  Fetching games from {start_date} to {end_date}")
                response = await session.get(
                    f"{self.api_base_url}/Games/TeamGames/Search",
                    params=params,
                    headers=self.headers
                )
                
                if response.status == 200:
                    games_data = await response.json()
                    print(f"  Found {len(games_data)} total games")
                    all_games.extend(games_data)
                else:
                    print(f"  API error {response.status}")
                    
            except Exception as e:
                print(f"  Error fetching games: {e}")
        
        return all_games


async def main():
    """Main function to check specific games and explore trending endpoints."""
    print("🚀 Starting Specific Game Check and Trending Game Discovery")
    print("=" * 60)
    
    checker = BettensorGameChecker()
    
    # Game IDs you mentioned from your manual data
    specific_game_ids = [
        "40274430",  # Mets vs Braves
        "40274431",  # Guardians vs White Sox  
        "40274432",  # Rays vs Red Sox
        "40274433",  # Orioles vs Yankees
        "40274434",  # Phillies vs Nationals
        "40274435",  # Marlins vs Braves
        "40274436",  # Blue Jays vs Twins
        "40274437",  # Royals vs Tigers
        "40274438",  # Astros vs Angels
        "40274439",  # Mariners vs Rangers
        "40274440",  # Dodgers vs Padres
        "40274441",  # Giants vs Rockies
        "40274442",  # Diamondbacks vs Brewers
        "40274443",  # Cardinals vs Cubs
        "40274444",  # Reds vs Pirates
    ]
    
    # 1. Check if specific game IDs exist in the API
    print("\n1. CHECKING SPECIFIC GAME IDs IN API DATA")
    print("-" * 40)
    game_check_results = await checker.check_specific_games(specific_game_ids)
    
    print(f"\n📊 GAME CHECK RESULTS:")
    print(f"  Total games in API: {game_check_results['total_games_checked']}")
    print(f"  Found games: {len(game_check_results['found_games'])}")
    print(f"  Missing games: {len(game_check_results['missing_games'])}")
    print(f"  Games with predictions: {len(game_check_results['games_with_predictions'])}")
    
    if game_check_results['missing_games']:
        print(f"\n❌ MISSING GAME IDs: {game_check_results['missing_games']}")
    
    if game_check_results['games_with_predictions']:
        print(f"\n🎯 GAMES WITH PREDICTIONS:")
        for game in game_check_results['games_with_predictions']:
            print(f"  {game['game_id']}: {game['team_a']} vs {game['team_b']} - {game['prediction_count']} predictions")
    
    # 2. Explore alternative endpoints
    print("\n\n2. EXPLORING ALTERNATIVE API ENDPOINTS")
    print("-" * 40)
    endpoint_results = await checker.explore_trending_endpoints()
    
    print(f"\n📊 ENDPOINT EXPLORATION RESULTS:")
    print(f"  Working endpoints: {len(endpoint_results['working_endpoints'])}")
    print(f"  Error endpoints: {len(endpoint_results['error_endpoints'])}")
    print(f"  Rate limited endpoints: {len(endpoint_results['rate_limited_endpoints'])}")
    print(f"  Promising endpoints: {len(endpoint_results['promising_endpoints'])}")
    
    if endpoint_results['working_endpoints']:
        print(f"\n✅ WORKING ENDPOINTS:")
        for endpoint in endpoint_results['working_endpoints']:
            print(f"  {endpoint['endpoint']} - Status: {endpoint['status']}, Data length: {endpoint['data_length']}")
    
    if endpoint_results['promising_endpoints']:
        print(f"\n🎯 PROMISING ENDPOINTS WITH PREDICTIONS:")
        for endpoint in endpoint_results['promising_endpoints']:
            print(f"  {endpoint['endpoint']} - {endpoint['games_with_predictions']} games with predictions")
    
    # 3. Check prediction data directly
    print("\n\n3. CHECKING PREDICTION DATA DIRECTLY")
    print("-" * 40)
    prediction_results = await checker.check_prediction_data_directly(specific_game_ids[:5])  # Test first 5 games
    
    print(f"\n📊 PREDICTION DATA RESULTS:")
    print(f"  Games with prediction data: {len(prediction_results['games_with_prediction_data'])}")
    print(f"  Games without prediction data: {len(prediction_results['games_without_prediction_data'])}")
    print(f"  Errors: {len(prediction_results['errors'])}")
    
    if prediction_results['games_with_prediction_data']:
        print(f"\n🎯 GAMES WITH DIRECT PREDICTION DATA:")
        for game in prediction_results['games_with_prediction_data']:
            print(f"  {game['game_id']}: Found at {game['endpoint']}")
    
    # 4. Summary and recommendations
    print("\n\n4. SUMMARY AND RECOMMENDATIONS")
    print("-" * 40)
    
    # Save detailed results to file
    with open("game_check_results.json", "w") as f:
        json.dump({
            "game_check_results": game_check_results,
            "endpoint_results": endpoint_results,
            "prediction_results": prediction_results
        }, f, indent=2, default=str)
    
    print(f"✅ Detailed results saved to game_check_results.json")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if game_check_results['found_games']:
        print(f"  • {len(game_check_results['found_games'])} of your specific game IDs were found in the API")
        
    if game_check_results['missing_games']:
        print(f"  • {len(game_check_results['missing_games'])} game IDs were not found - they may be:")
        print(f"    - From a different time period not covered by the API")
        print(f"    - Using a different ID format")
        print(f"    - From a different data source")
        
    if endpoint_results['promising_endpoints']:
        print(f"  • Found {len(endpoint_results['promising_endpoints'])} alternative endpoints with games that have predictions")
        print(f"  • These endpoints might be better for finding trending games")
        
    if not game_check_results['games_with_predictions']:
        print(f"  • No games with predictions found in the main API - this suggests:")
        print(f"    - Prediction data might be stored/accessed differently")
        print(f"    - Trending games might use a different API endpoint")
        print(f"    - The games with many predictions might not be visible in the games table")


if __name__ == "__main__":
    asyncio.run(main())
