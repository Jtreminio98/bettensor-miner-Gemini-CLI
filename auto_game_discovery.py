#!/usr/bin/env python3
"""
Automated Game Discovery for Bettensor
======================================

This script automatically finds future games with the most predictions on the Bettensor
sports betting subnet. It eliminates the need for manual website browsing by:

1. Querying the Bettensor API for upcoming games
2. Filtering for games scheduled in the future
3. Sorting by prediction count to find the "hottest" games
4. Returning the top N games for automated data extraction

Usage:
    python auto_game_discovery.py
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GameTarget:
    """Represents a game target for prediction extraction."""
    game_id: str
    team_a: str
    team_b: str
    sport: str
    league: str
    start_date: str
    prediction_count: int
    odds_home: Optional[float] = None
    odds_away: Optional[float] = None

class BettensorGameDiscovery:
    """Discovers future games with the most predictions on Bettensor."""
    
    def __init__(self, api_base_url: str = "https://dev-bettensor-api.azurewebsites.net"):
        self.api_base_url = api_base_url
        self.headers = {"Content-Type": "application/json"}
    
    async def discover_hot_games(self, 
                                top_n: int = 10,
                                min_predictions: int = 1,
                                days_ahead: int = 14,
                                sports_filter: Optional[List[str]] = None,
                                debug: bool = False) -> List[GameTarget]:
        """
        Discovers the top N future games with the most predictions.
        
        Args:
            top_n: Number of top games to return
            min_predictions: Minimum number of predictions a game must have
            days_ahead: How many days ahead to look for games
            sports_filter: Optional list of sports to filter by (e.g., ["baseball", "basketball"])
        
        Returns:
            List of GameTarget objects sorted by prediction count (descending)
        """
        print(f"🔍 Discovering top {top_n} future games with predictions...")
        
        future_games = await self._fetch_future_games(days_ahead, debug)
        
        if not future_games:
            print("❌ No future games found")
            return []
        
        # Filter games with predictions
        games_with_predictions = []
        for game in future_games:
            prediction_count = self._get_prediction_count(game)
            
            if prediction_count >= min_predictions:
                # Apply sports filter if specified
                if sports_filter:
                    game_sport = game.get('sport', '').lower()
                    if not any(sport.lower() in game_sport for sport in sports_filter):
                        continue
                
                game_target = self._create_game_target(game, prediction_count)
                if game_target:
                    games_with_predictions.append(game_target)
        
        # Sort by prediction count (descending) and return top N
        sorted_games = sorted(games_with_predictions, key=lambda x: x.prediction_count, reverse=True)
        top_games = sorted_games[:top_n]
        
        print(f"✅ Found {len(top_games)} hot games with predictions")
        return top_games
    
    async def _fetch_future_games(self, days_ahead: int, debug: bool = False) -> List[Dict]:
        """Fetch all future games from the API."""
        print(f"📡 Fetching future games for next {days_ahead} days...")
        
        all_games = []
        current_time = datetime.now(timezone.utc)
        
        async with aiohttp.ClientSession() as session:
            # Use a single broader time window instead of multiple requests
            start_date = current_time.isoformat()
            end_date = (current_time + timedelta(days=days_ahead)).isoformat()
            
            try:
                params = {
                    "PageIndex": 0,
                    "ItemsPerPage": 100,  # Get maximum games per request
                    "SortOrder": "StartDate",
                    "StartDate": start_date,
                    "EndDate": end_date,
                    "LeagueFilter": "false",  # Don't filter by league
                }
                
                print(f"Making single API call for {start_date} to {end_date}")
                response = await session.get(
                    f"{self.api_base_url}/Games/TeamGames/Search",
                    params=params,
                    headers=self.headers
                )
                
                if response.status == 200:
                    games_data = await response.json()
                    print(f"  Raw API response: {len(games_data)} total games returned")
                    
                    if debug and len(games_data) > 0:
                        print(f"  Sample game data structure: {games_data[0]}")
                    elif debug:
                        print(f"  Full API response: {games_data}")
                    
                    filtered_games = self._filter_future_games(games_data, current_time)
                    all_games.extend(filtered_games)
                    print(f"  Found {len(filtered_games)} future games")
                elif response.status == 429:
                    print(f"  Rate limited (429). Waiting 10 seconds...")
                    await asyncio.sleep(10)
                    # Try one more time
                    response = await session.get(
                        f"{self.api_base_url}/Games/TeamGames/Search",
                        params=params,
                        headers=self.headers
                    )
                    if response.status == 200:
                        games_data = await response.json()
                        print(f"  Raw API response (retry): {len(games_data)} total games returned")
                        
                        if debug and len(games_data) > 0:
                            print(f"  Sample game data structure (retry): {games_data[0]}")
                        elif debug:
                            print(f"  Full API response (retry): {games_data}")
                        
                        filtered_games = self._filter_future_games(games_data, current_time)
                        all_games.extend(filtered_games)
                        print(f"  Found {len(filtered_games)} future games (retry)")
                    else:
                        print(f"  Still getting API error {response.status} after retry")
                else:
                    print(f"  API error {response.status}")
                    
            except Exception as e:
                print(f"  Error fetching games - {e}")
        
        # Remove duplicates based on game ID
        unique_games = {game.get('externalId'): game for game in all_games}
        print(f"📊 Total unique future games found: {len(unique_games)}")
        
        return list(unique_games.values())
    
    def _filter_future_games(self, games: List[Dict], current_time: datetime) -> List[Dict]:
        """Filter games to only include those scheduled in the future."""
        future_games = []
        
        for game in games:
            game_date_str = game.get('date')
            if not game_date_str:
                continue
                
            try:
                # Parse game date
                game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                
                # Only include games that start in the future
                if game_date > current_time:
                    future_games.append(game)
                    
            except (ValueError, TypeError):
                # Skip games with invalid dates
                continue
        
        return future_games
    
    def _get_prediction_count(self, game: Dict) -> int:
        """Extract prediction count from game data."""
        return game.get('stats', {}).get('totalPredictionCount', 0)
    
    def _create_game_target(self, game: Dict, prediction_count: int) -> Optional[GameTarget]:
        """Create a GameTarget object from game data."""
        try:
            game_id = str(game.get('externalId', ''))
            team_a = game.get('teamA', '')
            team_b = game.get('teamB', '')
            sport = game.get('sport', '')
            league = game.get('league', '')
            start_date = game.get('date', '')
            
            # Extract odds if available
            odds_home = None
            odds_away = None
            if 'odds' in game:
                odds_data = game['odds']
                odds_home = odds_data.get('homeOdds')
                odds_away = odds_data.get('awayOdds')
            
            if game_id and team_a and team_b:
                return GameTarget(
                    game_id=game_id,
                    team_a=team_a,
                    team_b=team_b,
                    sport=sport,
                    league=league,
                    start_date=start_date,
                    prediction_count=prediction_count,
                    odds_home=odds_home,
                    odds_away=odds_away
                )
        except Exception as e:
            print(f"Warning: Could not create GameTarget for game {game.get('externalId')}: {e}")
        
        return None
    
    def print_game_targets(self, games: List[GameTarget]):
        """Print discovered game targets in a formatted way."""
        if not games:
            print("❌ No game targets found")
            return
        
        print(f"\n🎯 TOP {len(games)} HOTTEST GAMES FOR PREDICTION EXTRACTION")
        print("=" * 70)
        
        for i, game in enumerate(games, 1):
            print(f"{i:2d}. {game.team_a} vs {game.team_b}")
            print(f"     Sport: {game.sport} | League: {game.league}")
            print(f"     Game ID: {game.game_id}")
            print(f"     Predictions: {game.prediction_count}")
            print(f"     Start Date: {game.start_date}")
            if game.odds_home and game.odds_away:
                print(f"     Odds: {game.odds_home} (Home) / {game.odds_away} (Away)")
            print()
    
    async def get_game_targets_for_extraction(self, **kwargs) -> List[str]:
        """
        Convenience method that returns just the game IDs for data extraction.
        
        Returns:
            List of game IDs (strings) sorted by prediction count
        """
        games = await self.discover_hot_games(**kwargs)
        return [game.game_id for game in games]


async def main():
    """Main function to demonstrate the game discovery system."""
    print("🚀 Starting Automated Game Discovery for Bettensor")
    print("=" * 50)
    
    discovery = BettensorGameDiscovery()
    
    # Discover hot games
    hot_games = await discovery.discover_hot_games(
        top_n=15,
        min_predictions=1,
        days_ahead=14,
        sports_filter=None,  # Set to ["baseball", "basketball"] to filter
        debug=True  # Enable debug output
    )
    
    # Display results
    discovery.print_game_targets(hot_games)
    
    if hot_games:
        print("\n🎯 GAME IDs FOR DATA EXTRACTION:")
        game_ids = [game.game_id for game in hot_games]
        print(f"Target Game IDs: {game_ids}")
        
        # Show breakdown by sport
        sport_counts = {}
        for game in hot_games:
            sport = game.sport or "Unknown"
            sport_counts[sport] = sport_counts.get(sport, 0) + 1
        
        print(f"\n📊 BREAKDOWN BY SPORT:")
        for sport, count in sorted(sport_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {sport}: {count} games")
    
    return hot_games

if __name__ == "__main__":
    asyncio.run(main())
