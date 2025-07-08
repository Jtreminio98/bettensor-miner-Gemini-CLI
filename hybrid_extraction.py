#!/usr/bin/env python3
"""
Hybrid Bettensor Extraction Script
Combines automatic game discovery with manual game ID fallback
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bettensor.validator.bettensor_validator import BettensorValidator
from bettensor.validator.utils.io.website_handler import WebsiteHandler

class HybridBettensorExtractor:
    def __init__(self, config: Dict = None):
        self.config = config or {
            'api_base_url': 'https://bettensor.com/api',
            'min_predictions_threshold': 1,
            'max_games_to_analyze': 20,
            'top_games_limit': 10,
            'debug': True,
            'timeout': 30
        }
        
        self.validator = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'source': 'hybrid_extraction',
            'discovered_games': [],
            'manual_games': [],
            'prediction_analysis': {},
            'top_games': [],
            'recommendations': [],
            'errors': []
        }
        
        # Known high-prediction game IDs as fallback
        self.known_game_ids = [
            "d5c8f2e1-3b9a-4567-8901-234567890123",  # San Diego Padres vs Texas Rangers
            "a1b2c3d4-e5f6-7890-1234-567890123456",  # Minnesota Lynx W vs Golden State Valkyries W
            # Add more known game IDs here
        ]
        
        print("🎯 Hybrid Bettensor Extractor initialized")
    
    async def run_hybrid_extraction(self, manual_game_ids: List[str] = None) -> Dict:
        """
        Run the hybrid extraction process:
        1. Try automatic discovery first
        2. Fall back to manual game IDs if needed
        3. Extract predictions for discovered games
        """
        print("\n🚀 STARTING HYBRID EXTRACTION")
        print("=" * 50)
        
        try:
            # Step 1: Initialize validator
            await self.initialize_validator()
            
            # Step 2: Try automatic discovery
            discovered_games = await self.attempt_auto_discovery()
            
            # Step 3: Use manual fallback if needed
            target_games = await self.determine_target_games(discovered_games, manual_game_ids)
            
            # Step 4: Extract predictions for target games
            prediction_analysis = await self.extract_predictions_for_games(target_games)
            
            # Step 5: Rank and analyze results
            top_games = self.rank_games(prediction_analysis)
            recommendations = self.generate_recommendations(top_games)
            
            # Step 6: Display results
            self.print_summary(top_games, recommendations)
            
            return self.results
            
        except Exception as e:
            error_msg = f"❌ Hybrid extraction failed: {e}"
            print(error_msg)
            self.results['errors'].append(error_msg)
            return self.results
    
    async def initialize_validator(self):
        """Initialize the Bettensor validator"""
        print("\n🔧 Initializing Bettensor Validator...")
        
        try:
            self.validator = BettensorValidator()
            await self.validator.init_for_data_extraction()
            print("✅ Validator initialized successfully")
            
        except Exception as e:
            error_msg = f"❌ Failed to initialize validator: {e}"
            print(error_msg)
            self.results['errors'].append(error_msg)
            raise
    
    async def attempt_auto_discovery(self) -> List[Dict]:
        """Attempt automatic game discovery via API"""
        print("\n🔍 ATTEMPTING AUTOMATIC DISCOVERY")
        print("-" * 40)
        
        try:
            # Try to fetch future games with predictions
            future_games = await self.fetch_future_games()
            
            if future_games:
                print(f"✅ Auto-discovery found {len(future_games)} games")
                self.results['discovered_games'] = future_games
                return future_games
            else:
                print("⚠️ Auto-discovery found no games with predictions")
                return []
                
        except Exception as e:
            error_msg = f"❌ Auto-discovery failed: {e}"
            print(error_msg)
            self.results['errors'].append(error_msg)
            return []
    
    async def fetch_future_games(self) -> List[Dict]:
        """Fetch future games from the API"""
        print("📡 Fetching future games from API...")
        
        try:
            # Calculate date range for future games
            today = datetime.now()
            end_date = today + timedelta(days=7)  # Next 7 days
            
            url = f"{self.config['api_base_url']}/Games/TeamGames/Search"
            params = {
                'startDate': today.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'limit': self.config['max_games_to_analyze']
            }
            
            response = requests.get(url, params=params, timeout=self.config['timeout'])
            response.raise_for_status()
            
            games_data = response.json()
            
            # Filter games with predictions
            games_with_predictions = []
            for game in games_data:
                prediction_count = game.get('prediction_count', 0)
                if prediction_count >= self.config['min_predictions_threshold']:
                    games_with_predictions.append(game)
            
            print(f"📊 API returned {len(games_data)} total games")
            print(f"🎯 Found {len(games_with_predictions)} games with predictions")
            
            return games_with_predictions
            
        except Exception as e:
            print(f"❌ Error fetching future games: {e}")
            return []
    
    async def determine_target_games(self, discovered_games: List[Dict], manual_game_ids: List[str] = None) -> List[Dict]:
        """Determine which games to analyze based on discovery results"""
        print("\n🎯 DETERMINING TARGET GAMES")
        print("-" * 40)
        
        target_games = []
        
        # Use discovered games if available
        if discovered_games:
            print(f"✅ Using {len(discovered_games)} auto-discovered games")
            target_games.extend(discovered_games)
        
        # Add manual game IDs if provided
        if manual_game_ids:
            print(f"➕ Adding {len(manual_game_ids)} manual game IDs")
            manual_games = await self.fetch_manual_games(manual_game_ids)
            target_games.extend(manual_games)
            self.results['manual_games'] = manual_games
        
        # Fall back to known game IDs if nothing else works
        if not target_games:
            print("⚠️ No games found via auto-discovery or manual input")
            print(f"🔄 Falling back to {len(self.known_game_ids)} known game IDs")
            fallback_games = await self.fetch_manual_games(self.known_game_ids)
            target_games.extend(fallback_games)
            self.results['manual_games'] = fallback_games
        
        print(f"🎯 Total target games: {len(target_games)}")
        return target_games
    
    async def fetch_manual_games(self, game_ids: List[str]) -> List[Dict]:
        """Fetch specific games by ID"""
        manual_games = []
        
        for game_id in game_ids:
            try:
                # Try to fetch game details
                url = f"{self.config['api_base_url']}/Games/{game_id}"
                response = requests.get(url, timeout=self.config['timeout'])
                
                if response.status_code == 200:
                    game_data = response.json()
                    game_data['game_id'] = game_id  # Ensure ID is set
                    manual_games.append(game_data)
                    print(f"✅ Fetched game {game_id}")
                else:
                    print(f"⚠️ Could not fetch game {game_id} (Status: {response.status_code})")
                    # Create minimal game entry
                    manual_games.append({
                        'game_id': game_id,
                        'team_a': 'Unknown Team A',
                        'team_b': 'Unknown Team B',
                        'prediction_count': 0,
                        'status': 'manual_fallback'
                    })
                    
            except Exception as e:
                print(f"❌ Error fetching game {game_id}: {e}")
                # Create minimal game entry for fallback
                manual_games.append({
                    'game_id': game_id,
                    'team_a': 'Unknown Team A',
                    'team_b': 'Unknown Team B',
                    'prediction_count': 0,
                    'status': 'manual_fallback'
                })
        
        return manual_games
    
    async def fetch_predictions_from_db(self, game_id: str) -> List[Dict]:
        """Fetch predictions for a specific game from the database"""
        try:
            if not self.validator or not hasattr(self.validator, 'db_manager'):
                return []
            
            # Query the database for predictions for this game
            query = """
            SELECT * FROM predictions 
            WHERE game_id = :game_id 
            ORDER BY prediction_date DESC
            """
            
            results = await self.validator.db_manager.fetch_all(query, {"game_id": game_id})
            
            # Convert database results to our format
            predictions = []
            for row in results:
                predictions.append({
                    'miner': row.get('miner_hotkey', 'unknown'),
                    'prediction': {
                        'game_id': row.get('game_id'),
                        'team_a': row.get('team_a'),
                        'team_b': row.get('team_b'),
                        'predicted_outcome': row.get('predicted_outcome'),
                        'predicted_odds': row.get('predicted_odds'),
                        'confidence': row.get('confidence'),
                        'wager': row.get('wager')
                    },
                    'game_id': game_id,
                    'timestamp': row.get('timestamp', datetime.now().isoformat())
                })
            
            return predictions
            
        except Exception as e:
            print(f"❌ Error fetching predictions from database: {e}")
            return []
    
    async def extract_predictions_for_games(self, target_games: List[Dict]) -> Dict:
        """Extract miner predictions for target games"""
        print("\n🔮 EXTRACTING PREDICTIONS FROM MINERS")
        print("-" * 40)
        
        prediction_analysis = {}
        
        for game in target_games:
            game_id = game.get('game_id', game.get('id'))
            if not game_id:
                continue
                
            print(f"\n📊 Analyzing game {game_id}...")
            
            # Get predictions from miners
            miner_predictions = await self.get_miner_predictions(game_id)
            
            # Analyze predictions
            analysis = self.analyze_predictions(miner_predictions)
            
            prediction_analysis[game_id] = {
                'game_info': game,
                'predictions': miner_predictions,
                'analysis': analysis
            }
            
            print(f"  📈 Found {len(miner_predictions)} predictions from {analysis.get('unique_miners', 0)} miners")
        
        self.results['prediction_analysis'] = prediction_analysis
        return prediction_analysis
    
    async def get_miner_predictions(self, game_id: str) -> List[Dict]:
        """Get predictions from miners for a specific game"""
        try:
            if not self.validator:
                return []
            
            print(f"    🔍 Querying all miners for game {game_id}...")
            
            # Use the validator's forward method to query all miners
            # This will automatically store predictions in the database
            await self.validator.forward()
            
            # Now fetch predictions for this specific game from the database
            predictions = await self.fetch_predictions_from_db(game_id)
            
            print(f"    📊 Retrieved {len(predictions)} predictions from database")
            
            return predictions
            
        except Exception as e:
            print(f"❌ Error getting miner predictions: {e}")
            return []
    
    def analyze_predictions(self, miner_data: List[Dict]) -> Dict:
        """Analyze prediction data to extract insights"""
        if not miner_data:
            return {
                'total_predictions': 0,
                'unique_miners': 0,
                'prediction_distribution': {},
                'confidence_stats': [],
                'consensus': None
            }
        
        analysis = {
            'total_predictions': len(miner_data),
            'unique_miners': len(set(d['miner'] for d in miner_data)),
            'prediction_distribution': Counter(),
            'confidence_stats': [],
            'consensus': None
        }
        
        # Analyze predictions
        for data in miner_data:
            prediction = data.get('prediction', {})
            
            # Count prediction types/outcomes
            outcome = prediction.get('outcome', prediction.get('predicted_outcome', 'unknown'))
            analysis['prediction_distribution'][outcome] += 1
            
            # Collect confidence scores if available
            confidence = prediction.get('confidence', prediction.get('probability'))
            if confidence and isinstance(confidence, (int, float)):
                analysis['confidence_stats'].append(confidence)
        
        # Calculate consensus
        if analysis['prediction_distribution']:
            most_common = analysis['prediction_distribution'].most_common(1)[0]
            analysis['consensus'] = {
                'outcome': most_common[0],
                'count': most_common[1],
                'percentage': (most_common[1] / analysis['total_predictions']) * 100
            }
        
        return analysis
    
    def rank_games(self, prediction_analysis: Dict) -> List[Dict]:
        """Rank games by prediction quality and consensus"""
        print("\n🏆 RANKING GAMES BY PREDICTION QUALITY")
        print("-" * 40)
        
        ranked_games = []
        
        for game_id, data in prediction_analysis.items():
            game_info = data['game_info']
            analysis = data['analysis']
            
            # Calculate ranking score
            score = self.calculate_game_score(analysis)
            
            ranked_games.append({
                'game_id': game_id,
                'game_info': game_info,
                'analysis': analysis,
                'score': score
            })
        
        # Sort by score (descending)
        ranked_games.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply limit
        top_limit = self.config.get('top_games_limit', 10)
        top_games = ranked_games[:top_limit]
        
        self.results['top_games'] = top_games
        
        print(f"📊 Ranked {len(ranked_games)} games, selected top {len(top_games)}")
        
        return top_games
    
    def calculate_game_score(self, analysis: Dict) -> float:
        """Calculate a score for ranking games"""
        if not analysis:
            return 0.0
        
        score = 0.0
        
        # Base score from number of predictions
        total_predictions = analysis.get('total_predictions', 0)
        score += total_predictions * 10
        
        # Bonus for unique miners
        unique_miners = analysis.get('unique_miners', 0)
        score += unique_miners * 5
        
        # Bonus for consensus strength
        consensus = analysis.get('consensus', {})
        if consensus:
            consensus_percentage = consensus.get('percentage', 0)
            score += consensus_percentage * 2
        
        # Bonus for confidence
        confidence_stats = analysis.get('confidence_stats', [])
        if confidence_stats:
            avg_confidence = sum(confidence_stats) / len(confidence_stats)
            score += avg_confidence * 50
        
        return score
    
    def generate_recommendations(self, top_games: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not top_games:
            recommendations.append("❌ No games with predictions found")
            recommendations.append("💡 Try adding manual game IDs or check API connectivity")
            return recommendations
        
        # Top recommendation
        top_game = top_games[0]
        recommendations.append(f"🎯 TOP PICK: Game {top_game['game_id']} with {top_game['analysis']['total_predictions']} predictions")
        
        # Consensus recommendations
        strong_consensus = [g for g in top_games if g['analysis'].get('consensus', {}).get('percentage', 0) > 70]
        if strong_consensus:
            recommendations.append(f"🤝 {len(strong_consensus)} games have strong consensus (>70% agreement)")
        
        # High activity recommendations
        high_activity = [g for g in top_games if g['analysis']['total_predictions'] > 10]
        if high_activity:
            recommendations.append(f"🔥 {len(high_activity)} games have high prediction activity (>10 predictions)")
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def print_summary(self, top_games: List[Dict], recommendations: List[str]):
        """Print a formatted summary of results"""
        print("\n" + "=" * 80)
        print("🎯 HYBRID BETTENSOR EXTRACTION SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"  Auto-discovered games: {len(self.results['discovered_games'])}")
        print(f"  Manual games: {len(self.results['manual_games'])}")
        print(f"  Games with predictions: {len(self.results['prediction_analysis'])}")
        print(f"  Top games identified: {len(top_games)}")
        
        if top_games:
            print(f"\n🏆 TOP GAMES RANKING:")
            for i, game in enumerate(top_games[:5]):  # Show top 5
                game_info = game['game_info']
                analysis = game['analysis']
                
                print(f"  {i+1}. Game {game['game_id']} (Score: {game['score']:.1f})")
                print(f"     {game_info.get('team_a', 'Team A')} vs {game_info.get('team_b', 'Team B')}")
                print(f"     Predictions: {analysis['total_predictions']}, Miners: {analysis['unique_miners']}")
                
                consensus = analysis.get('consensus', {})
                if consensus:
                    print(f"     Consensus: {consensus['percentage']:.1f}% for {consensus['outcome']}")
                print()
        
        if recommendations:
            print(f"💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"  {rec}")
    
    def save_results(self, filename: str = None) -> str:
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hybrid_results_{timestamp}.json"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"💾 Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return ""


async def main():
    """Main execution function"""
    # Configuration
    config = {
        'api_base_url': 'https://bettensor.com/api',
        'min_predictions_threshold': 1,
        'max_games_to_analyze': 20,
        'top_games_limit': 10,
        'debug': True,
        'timeout': 30
    }
    
    # Manual game IDs (optional - can be provided via command line)
    manual_game_ids = [
        # Add specific game IDs here if you have them
        # "d5c8f2e1-3b9a-4567-8901-234567890123",
        # "a1b2c3d4-e5f6-7890-1234-567890123456",
    ]
    
    # Create extractor and run
    extractor = HybridBettensorExtractor(config)
    results = await extractor.run_hybrid_extraction(manual_game_ids)
    
    # Save results
    extractor.save_results()
    
    print("\n🎉 Hybrid extraction completed!")
    return results


if __name__ == "__main__":
    # Run the hybrid extraction
    results = asyncio.run(main())
