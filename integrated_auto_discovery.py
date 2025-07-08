#!/usr/bin/env python3
"""
Integrated Automation Script for Bettensor Game Discovery and Data Extraction
============================================================================

This script combines:
1. Automated game discovery using working API endpoints
2. Data extraction from BettensorValidator
3. Prediction analysis and ranking
4. Automated output generation

Usage:
    python integrated_auto_discovery.py
"""

import json
import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from collections import defaultdict, Counter

# Add the current directory to the path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bettensor.validator.bettensor_validator import BettensorValidator
    from auto_game_discovery import BettensorGameDiscovery
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please make sure you're running this from the bettensor-miner directory")
    sys.exit(1)


class IntegratedBettensorAutomation:
    """
    Integrated automation for game discovery and data extraction
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the automation system"""
        self.config_path = config_path
        self.config = self.load_config()
        self.validator = None
        self.discovery = BettensorGameDiscovery()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'discovered_games': [],
            'prediction_analysis': {},
            'top_games': [],
            'recommendations': []
        }
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_path} not found, using defaults")
            return {
                'top_games_limit': 10,
                'min_predictions': 3,
                'days_ahead': 7,
                'output_format': 'detailed'
            }
    
    def initialize_validator(self) -> bool:
        """Initialize the BettensorValidator for data extraction"""
        try:
            print("🔧 Initializing BettensorValidator...")
            self.validator = BettensorValidator()
            
            # Use the init_for_data_extraction method if available
            if hasattr(self.validator, 'init_for_data_extraction'):
                print("📊 Using data extraction initialization...")
                self.validator.init_for_data_extraction()
            else:
                print("⚠️  Standard initialization used")
            
            print("✅ BettensorValidator initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing validator: {e}")
            return False
    
    async def discover_games(self) -> List[Dict]:
        """Discover available games using working API endpoints"""
        print("\n🔍 DISCOVERING AVAILABLE GAMES")
        print("=" * 50)
        
        discovered_games = []
        
        # Try the working search endpoint
        try:
            print("📡 Using /Games/TeamGames/Search endpoint...")
            search_games = await self.discovery.search_games_endpoint()
            if search_games:
                discovered_games.extend(search_games)
                print(f"✅ Found {len(search_games)} games from search endpoint")
            else:
                print("❌ No games found from search endpoint")
                
        except Exception as e:
            print(f"❌ Error with search endpoint: {e}")
        
        # Try the main discovery method as fallback
        try:
            print("📡 Trying main discovery method...")
            main_games = await self.discovery.discover_hot_games(
                days_ahead=self.config.get('days_ahead', 7)
            )
            if main_games:
                # Avoid duplicates
                existing_ids = {g.get('game_id') for g in discovered_games}
                new_games = [g for g in main_games if g.get('game_id') not in existing_ids]
                discovered_games.extend(new_games)
                print(f"✅ Found {len(new_games)} additional games from main discovery")
            else:
                print("❌ No games found from main discovery")
                
        except Exception as e:
            print(f"❌ Error with main discovery: {e}")
        
        # Store discovered games
        self.results['discovered_games'] = discovered_games
        
        print(f"\n📊 DISCOVERY SUMMARY:")
        print(f"  Total games discovered: {len(discovered_games)}")
        
        if discovered_games:
            print(f"  Games with predictions: {sum(1 for g in discovered_games if g.get('prediction_count', 0) > 0)}")
            print(f"  Average prediction count: {sum(g.get('prediction_count', 0) for g in discovered_games) / len(discovered_games):.1f}")
        
        return discovered_games
    
    def extract_prediction_data(self, games: List[Dict]) -> Dict:
        """Extract prediction data for discovered games"""
        print("\n🎯 EXTRACTING PREDICTION DATA")
        print("=" * 50)
        
        if not self.validator:
            print("❌ Validator not initialized, skipping prediction extraction")
            return {}
        
        prediction_analysis = {}
        
        for game in games:
            game_id = game.get('game_id')
            if not game_id:
                continue
            
            try:
                print(f"📊 Extracting data for game {game_id}...")
                
                # Get miner predictions for this game
                miner_data = self.get_miner_predictions(game_id)
                
                if miner_data:
                    analysis = self.analyze_predictions(miner_data)
                    prediction_analysis[game_id] = {
                        'game_info': game,
                        'miner_data': miner_data,
                        'analysis': analysis
                    }
                    print(f"✅ Found {len(miner_data)} miner predictions for game {game_id}")
                else:
                    print(f"❌ No miner predictions found for game {game_id}")
                    
            except Exception as e:
                print(f"❌ Error extracting data for game {game_id}: {e}")
        
        self.results['prediction_analysis'] = prediction_analysis
        
        print(f"\n📊 EXTRACTION SUMMARY:")
        print(f"  Games with miner data: {len(prediction_analysis)}")
        print(f"  Total predictions extracted: {sum(len(data['miner_data']) for data in prediction_analysis.values())}")
        
        return prediction_analysis
    
    def get_miner_predictions(self, game_id: str) -> List[Dict]:
        """Get miner predictions for a specific game"""
        try:
            # This would use your existing data extraction logic
            # Adapting from your data_extractor.py pattern
            
            # Get all miners
            miners = self.validator.get_all_miners()
            predictions = []
            
            for miner in miners:
                try:
                    # Get prediction for this game from this miner
                    prediction = self.validator.get_prediction_for_game(miner, game_id)
                    if prediction:
                        predictions.append({
                            'miner': miner,
                            'prediction': prediction,
                            'game_id': game_id
                        })
                except Exception as e:
                    # Skip individual miner errors
                    continue
            
            return predictions
            
        except Exception as e:
            print(f"❌ Error getting miner predictions: {e}")
            return []
    
    def analyze_predictions(self, miner_data: List[Dict]) -> Dict:
        """Analyze prediction data to extract insights"""
        if not miner_data:
            return {}
        
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
            outcome = prediction.get('outcome', 'unknown')
            analysis['prediction_distribution'][outcome] += 1
            
            # Collect confidence scores if available
            confidence = prediction.get('confidence', prediction.get('probability'))
            if confidence:
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
        print("=" * 50)
        
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
                'score': score,
                'rank': 0  # Will be set after sorting
            })
        
        # Sort by score (descending)
        ranked_games.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign ranks
        for i, game in enumerate(ranked_games):
            game['rank'] = i + 1
        
        # Apply limit
        top_limit = self.config.get('top_games_limit', 10)
        top_games = ranked_games[:top_limit]
        
        self.results['top_games'] = top_games
        
        print(f"📊 RANKING SUMMARY:")
        print(f"  Total games ranked: {len(ranked_games)}")
        print(f"  Top games selected: {len(top_games)}")
        
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
            recommendations.append("❌ No games with predictions found. Check API connectivity and data sources.")
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
        
        # Diverse miner recommendations
        diverse_miners = [g for g in top_games if g['analysis']['unique_miners'] > 5]
        if diverse_miners:
            recommendations.append(f"👥 {len(diverse_miners)} games have diverse miner participation (>5 unique miners)")
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def save_results(self, filename: str = None) -> str:
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integrated_results_{timestamp}.json"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"💾 Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return ""
    
    def print_summary(self, top_games: List[Dict], recommendations: List[str]):
        """Print a formatted summary of results"""
        print("\n" + "=" * 80)
        print("🎯 INTEGRATED BETTENSOR AUTOMATION SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"  Games discovered: {len(self.results['discovered_games'])}")
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
        
        print(f"\n⏰ Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    async def run_full_automation(self):
        """Run the complete automation workflow"""
        print("🚀 STARTING INTEGRATED BETTENSOR AUTOMATION")
        print("=" * 80)
        
        # Step 1: Initialize validator
        if not self.initialize_validator():
            print("❌ Failed to initialize validator, exiting")
            return
        
        # Step 2: Discover games
        discovered_games = await self.discover_games()
        
        if not discovered_games:
            print("❌ No games discovered, exiting")
            return
        
        # Step 3: Extract prediction data
        prediction_analysis = self.extract_prediction_data(discovered_games)
        
        if not prediction_analysis:
            print("❌ No prediction data extracted, exiting")
            return
        
        # Step 4: Rank games
        top_games = self.rank_games(prediction_analysis)
        
        # Step 5: Generate recommendations
        recommendations = self.generate_recommendations(top_games)
        
        # Step 6: Save results
        self.save_results()
        
        # Step 7: Print summary
        self.print_summary(top_games, recommendations)
        
        print("\n✅ Automation completed successfully!")
        return self.results


async def main():
    """Main execution function"""
    try:
        automation = IntegratedBettensorAutomation()
        await automation.run_full_automation()
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
