#!/usr/bin/env python3
"""
Integrated Bettensor Extraction System
======================================

This script combines automated game discovery with miner prediction extraction
to provide a fully automated pipeline for sports betting predictions.

Features:
- Automatically discovers future games with the most predictions
- Queries miners for predictions on those games
- Aggregates and displays results
- Saves data to database for analysis

Usage:
    python integrated_extraction.py
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from auto_game_discovery import BettensorGameDiscovery, GameTarget

class IntegratedBettensorExtraction:
    """
    Integrated system that combines game discovery with prediction extraction.
    """
    
    def __init__(self):
        self.game_discovery = BettensorGameDiscovery()
        # Initialize your existing data extractor here
        # self.data_extractor = YourDataExtractor()
        
    async def run_automated_extraction(self, 
                                     top_n_games: int = 10,
                                     min_predictions: int = 2,
                                     days_ahead: int = 2,
                                     sports_filter: Optional[List[str]] = None,
                                     save_to_db: bool = True) -> Dict:
        """
        Run the complete automated extraction pipeline.
        
        Args:
            top_n_games: Number of top games to extract predictions for
            min_predictions: Minimum predictions required for a game to be included
            days_ahead: How many days ahead to look for games
            sports_filter: Optional list of sports to filter by
            save_to_db: Whether to save results to database
            
        Returns:
            Dict containing extraction results and summary
        """
        print("🚀 Starting Integrated Bettensor Extraction Pipeline")
        print("=" * 60)
        
        # Step 1: Discover hot games
        print("\n📋 STEP 1: Discovering Hot Games")
        hot_games = await self.game_discovery.discover_hot_games(
            top_n=top_n_games,
            min_predictions=min_predictions,
            days_ahead=days_ahead,
            sports_filter=sports_filter
        )
        
        if not hot_games:
            print("❌ No hot games found. Exiting.")
            return {"success": False, "message": "No games found"}
        
        # Display discovered games
        self.game_discovery.print_game_targets(hot_games)
        
        # Step 2: Extract predictions for each game
        print("\n🔍 STEP 2: Extracting Miner Predictions")
        extraction_results = await self._extract_predictions_for_games(hot_games)
        
        # Step 3: Aggregate and analyze results
        print("\n📊 STEP 3: Aggregating Results")
        aggregated_results = self._aggregate_prediction_results(extraction_results)
        
        # Step 4: Display summary
        print("\n📈 STEP 4: Results Summary")
        self._display_results_summary(aggregated_results)
        
        # Step 5: Save to database (optional)
        if save_to_db:
            print("\n💾 STEP 5: Saving to Database")
            await self._save_to_database(aggregated_results)
        
        return {
            "success": True,
            "games_processed": len(hot_games),
            "predictions_extracted": sum(len(result.get("predictions", [])) for result in extraction_results),
            "aggregated_results": aggregated_results
        }
    
    async def _extract_predictions_for_games(self, games: List[GameTarget]) -> List[Dict]:
        """
        Extract predictions for a list of games.
        
        This is where you would integrate your existing prediction extraction logic.
        """
        results = []
        
        for game in games:
            print(f"  🎯 Extracting predictions for {game.team_a} vs {game.team_b} (ID: {game.game_id})")
            
            # TODO: Replace this with your actual prediction extraction logic
            # Example integration with your existing code:
            # predictions = await self.data_extractor.get_predictions_for_game(game.game_id)
            
            # Placeholder for demonstration
            predictions = await self._mock_prediction_extraction(game)
            
            result = {
                "game": game,
                "predictions": predictions,
                "extraction_time": datetime.now().isoformat()
            }
            results.append(result)
            
            print(f"    ✅ Extracted {len(predictions)} predictions")
        
        return results
    
    async def _mock_prediction_extraction(self, game: GameTarget) -> List[Dict]:
        """
        Mock prediction extraction for demonstration.
        Replace this with your actual prediction extraction logic.
        """
        # Simulate some predictions based on game data
        mock_predictions = [
            {
                "miner_uid": f"miner_{i}",
                "prediction": "home" if i % 2 == 0 else "away",
                "confidence": 0.6 + (i * 0.05) % 0.4,
                "timestamp": datetime.now().isoformat()
            }
            for i in range(game.prediction_count)
        ]
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        return mock_predictions
    
    def _aggregate_prediction_results(self, results: List[Dict]) -> Dict:
        """
        Aggregate prediction results across all games.
        """
        aggregated = {
            "games": [],
            "total_predictions": 0,
            "summary_stats": {
                "total_games": len(results),
                "home_predictions": 0,
                "away_predictions": 0,
                "average_confidence": 0.0,
                "top_sports": {}
            }
        }
        
        all_confidences = []
        
        for result in results:
            game = result["game"]
            predictions = result["predictions"]
            
            # Count predictions by outcome
            home_count = sum(1 for p in predictions if p["prediction"] == "home")
            away_count = sum(1 for p in predictions if p["prediction"] == "away")
            
            # Calculate average confidence for this game
            confidences = [p["confidence"] for p in predictions if "confidence" in p]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            all_confidences.extend(confidences)
            
            # Determine consensus prediction
            consensus = "home" if home_count > away_count else "away"
            consensus_strength = max(home_count, away_count) / len(predictions) if predictions else 0
            
            game_summary = {
                "game_id": game.game_id,
                "matchup": f"{game.team_a} vs {game.team_b}",
                "sport": game.sport,
                "league": game.league,
                "start_date": game.start_date,
                "total_predictions": len(predictions),
                "home_predictions": home_count,
                "away_predictions": away_count,
                "consensus_prediction": consensus,
                "consensus_strength": consensus_strength,
                "average_confidence": avg_confidence
            }
            
            aggregated["games"].append(game_summary)
            aggregated["total_predictions"] += len(predictions)
            aggregated["summary_stats"]["home_predictions"] += home_count
            aggregated["summary_stats"]["away_predictions"] += away_count
            
            # Track sports
            sport = game.sport or "Unknown"
            aggregated["summary_stats"]["top_sports"][sport] = aggregated["summary_stats"]["top_sports"].get(sport, 0) + 1
        
        # Calculate overall average confidence
        if all_confidences:
            aggregated["summary_stats"]["average_confidence"] = sum(all_confidences) / len(all_confidences)
        
        return aggregated
    
    def _display_results_summary(self, results: Dict):
        """Display a formatted summary of the extraction results."""
        stats = results["summary_stats"]
        
        print(f"📊 EXTRACTION SUMMARY")
        print("=" * 40)
        print(f"Games Processed: {stats['total_games']}")
        print(f"Total Predictions: {results['total_predictions']}")
        print(f"Home Predictions: {stats['home_predictions']}")
        print(f"Away Predictions: {stats['away_predictions']}")
        print(f"Average Confidence: {stats['average_confidence']:.3f}")
        
        print(f"\n🏆 TOP SPORTS:")
        for sport, count in sorted(stats['top_sports'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {sport}: {count} games")
        
        print(f"\n🎯 GAME PREDICTIONS:")
        for game in results["games"]:
            consensus_emoji = "🏠" if game["consensus_prediction"] == "home" else "🛫"
            print(f"{consensus_emoji} {game['matchup']} - {game['consensus_prediction'].upper()}")
            print(f"    Strength: {game['consensus_strength']:.1%} | Confidence: {game['average_confidence']:.3f}")
            print(f"    Predictions: {game['home_predictions']} home, {game['away_predictions']} away")
    
    async def _save_to_database(self, results: Dict):
        """
        Save results to database.
        
        Implement your database saving logic here.
        """
        print("💾 Saving results to database...")
        
        # TODO: Implement database saving
        # Example:
        # await self.database.save_extraction_results(results)
        
        # For now, save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extraction_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✅ Results saved to {filename}")

async def main():
    """Main function to run the integrated extraction system."""
    extractor = IntegratedBettensorExtraction()
    
    # Run the complete pipeline
    results = await extractor.run_automated_extraction(
        top_n_games=15,
        min_predictions=1,
        days_ahead=7,
        sports_filter=None,  # Set to ["baseball", "basketball"] to filter
        save_to_db=True
    )
    
    if results["success"]:
        print(f"\n🎉 Extraction completed successfully!")
        print(f"   - Games processed: {results['games_processed']}")
        print(f"   - Predictions extracted: {results['predictions_extracted']}")
    else:
        print(f"\n❌ Extraction failed: {results['message']}")

if __name__ == "__main__":
    asyncio.run(main())
