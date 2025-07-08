#!/usr/bin/env python3
"""
Direct Miner Query Test Script
Tests direct connectivity to miners via the validator, bypassing external APIs
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bettensor.validator.bettensor_validator import BettensorValidator
from bettensor.protocol import GameData
import bittensor as bt

class DirectMinerTester:
    def __init__(self):
        self.validator = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'miners_queried': 0,
            'miners_responded': 0,
            'total_predictions': 0,
            'predictions_by_game': {},
            'active_miners': [],
            'errors': []
        }
        
        # Test game IDs - let's try some common formats
        self.test_game_ids = [
            # Format 1: UUID style
            "d5c8f2e1-3b9a-4567-8901-234567890123",
            "a1b2c3d4-e5f6-7890-1234-567890123456",
            
            # Format 2: Simple numeric
            "12345",
            "67890",
            
            # Format 3: Sport-specific IDs (NFL, NBA, etc)
            "NFL_2024_W1_LAR_vs_DET",
            "NBA_2024_LAL_vs_BOS",
            
            # Format 4: Date-based
            f"GAME_{datetime.now().strftime('%Y%m%d')}_001",
            f"GAME_{datetime.now().strftime('%Y%m%d')}_002",
        ]
        
        print("🔬 Direct Miner Tester initialized")
    
    async def run_test(self):
        """Run the direct miner connectivity test"""
        print("\n🚀 STARTING DIRECT MINER CONNECTIVITY TEST")
        print("=" * 60)
        
        try:
            # Step 1: Initialize validator
            await self.initialize_validator()
            
            # Step 2: Check validator status
            await self.check_validator_status()
            
            # Step 3: Query miners directly
            await self.query_miners_directly()
            
            # Step 4: Check database for any existing predictions
            await self.check_database_predictions()
            
            # Step 5: Try specific game queries
            await self.test_specific_game_queries()
            
            # Step 6: Display results
            self.print_results()
            
            return self.results
            
        except Exception as e:
            error_msg = f"❌ Test failed: {e}"
            print(error_msg)
            self.results['errors'].append(error_msg)
            return self.results
    
    async def initialize_validator(self):
        """Initialize the Bettensor validator"""
        print("\n🔧 Initializing Bettensor Validator...")
        
        try:
            self.validator = BettensorValidator()
            
            # Initialize the validator for data extraction
            print("  🔧 Calling init_for_data_extraction()...")
            await self.validator.init_for_data_extraction()
            
            # Check if validator has required attributes
            print("  📋 Validator attributes:")
            print(f"    - Has metagraph: {hasattr(self.validator, 'metagraph')}")
            print(f"    - Has dendrite: {hasattr(self.validator, 'dendrite')}")
            print(f"    - Has db_manager: {hasattr(self.validator, 'db_manager')}")
            print(f"    - Has subtensor: {hasattr(self.validator, 'subtensor')}")
            
            print("✅ Validator initialized successfully")
            
        except Exception as e:
            error_msg = f"❌ Failed to initialize validator: {e}"
            print(error_msg)
            self.results['errors'].append(error_msg)
            raise
    
    async def check_validator_status(self):
        """Check the validator's network status"""
        print("\n🔍 Checking validator network status...")
        
        try:
            if hasattr(self.validator, 'metagraph') and self.validator.metagraph:
                print(f"  📡 Network: {self.validator.metagraph.network if hasattr(self.validator.metagraph, 'network') else 'Unknown'}")
                print(f"  🔢 Total neurons: {len(self.validator.metagraph.neurons) if hasattr(self.validator.metagraph, 'neurons') else 0}")
                
                # Count active miners
                active_count = 0
                if hasattr(self.validator.metagraph, 'neurons'):
                    for neuron in self.validator.metagraph.neurons:
                        if hasattr(neuron, 'is_active') and neuron.is_active:
                            active_count += 1
                
                print(f"  ✅ Active miners: {active_count}")
                self.results['miners_queried'] = active_count
            else:
                print("  ⚠️ Metagraph not available")
                
        except Exception as e:
            print(f"  ❌ Error checking validator status: {e}")
            self.results['errors'].append(f"Status check error: {e}")
    
    async def query_miners_directly(self):
        """Query miners directly using the validator's forward method"""
        print("\n🔮 Querying miners directly...")
        
        try:
            # Use the validator's forward method
            print("  📡 Calling validator.forward()...")
            
            # The forward method queries all miners
            await self.validator.forward()
            
            print("  ✅ Forward pass completed")
            
            # Check how many responses we got
            if hasattr(self.validator, 'responses'):
                self.results['miners_responded'] = len([r for r in self.validator.responses if r is not None])
                print(f"  📊 Miners responded: {self.results['miners_responded']}")
            
        except Exception as e:
            error_msg = f"❌ Error querying miners: {e}"
            print(f"  {error_msg}")
            self.results['errors'].append(error_msg)
    
    async def check_database_predictions(self):
        """Check the database for any existing predictions"""
        print("\n🗄️ Checking database for predictions...")
        
        try:
            db_path = os.path.join(os.path.dirname(__file__), "validator.db")
            
            if not os.path.exists(db_path):
                print(f"  ⚠️ Database not found at {db_path}")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Count total predictions
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total_count = cursor.fetchone()[0]
            print(f"  📊 Total predictions in database: {total_count}")
            self.results['total_predictions'] = total_count
            
            # Get recent predictions
            cursor.execute("""
                SELECT game_id, COUNT(*) as count 
                FROM predictions 
                WHERE prediction_date >= datetime('now', '-7 days')
                GROUP BY game_id 
                ORDER BY count DESC 
                LIMIT 10
            """)
            
            recent_games = cursor.fetchall()
            if recent_games:
                print("\n  📈 Recent games with predictions:")
                for game_id, count in recent_games:
                    print(f"    - Game {game_id}: {count} predictions")
                    self.results['predictions_by_game'][game_id] = count
            else:
                print("  ⚠️ No recent predictions found")
            
            # Get active miners
            cursor.execute("""
                SELECT DISTINCT miner_hotkey 
                FROM predictions 
                WHERE prediction_date >= datetime('now', '-1 day')
            """)
            
            active_miners = [row[0] for row in cursor.fetchall()]
            if active_miners:
                print(f"\n  🔥 Active miners (last 24h): {len(active_miners)}")
                self.results['active_miners'] = active_miners[:10]  # Store first 10
            
            conn.close()
            
        except Exception as e:
            error_msg = f"Database check error: {e}"
            print(f"  ❌ {error_msg}")
            self.results['errors'].append(error_msg)
    
    async def test_specific_game_queries(self):
        """Test querying for specific game IDs"""
        print("\n🎮 Testing specific game queries...")
        
        try:
            # Create a test synapse with game data
            for game_id in self.test_game_ids[:3]:  # Test first 3 game IDs
                print(f"\n  🔍 Testing game ID: {game_id}")
                
                # Create a GameData synapse
                synapse = GameData(
                    game_id=game_id,
                    team_a=f"Team A {game_id[:5]}",
                    team_b=f"Team B {game_id[:5]}",
                    sport="unknown",
                    league="unknown",
                    external_id=game_id,
                    start_time=datetime.now() + timedelta(days=1),
                    last_update_time=datetime.now()
                )
                
                # Try to query miners with this specific game
                if hasattr(self.validator, 'dendrite') and self.validator.dendrite:
                    try:
                        # Query a subset of miners
                        miner_uids = list(range(min(5, len(self.validator.metagraph.neurons))))
                        
                        responses = await self.validator.dendrite(
                            axons=[self.validator.metagraph.axons[uid] for uid in miner_uids],
                            synapse=synapse,
                            deserialize=True,
                            timeout=10
                        )
                        
                        valid_responses = [r for r in responses if r is not None]
                        print(f"    ✅ Got {len(valid_responses)} responses for game {game_id}")
                        
                    except Exception as e:
                        print(f"    ❌ Error querying game {game_id}: {e}")
                
        except Exception as e:
            error_msg = f"Specific game query error: {e}"
            print(f"  ❌ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 DIRECT MINER TEST RESULTS")
        print("=" * 60)
        
        print(f"\n🔍 Network Status:")
        print(f"  - Miners in network: {self.results['miners_queried']}")
        print(f"  - Miners responded: {self.results['miners_responded']}")
        
        print(f"\n📈 Database Status:")
        print(f"  - Total predictions: {self.results['total_predictions']}")
        print(f"  - Games with predictions: {len(self.results['predictions_by_game'])}")
        print(f"  - Active miners: {len(self.results['active_miners'])}")
        
        if self.results['predictions_by_game']:
            print(f"\n🎮 Top Games by Predictions:")
            for game_id, count in list(self.results['predictions_by_game'].items())[:5]:
                print(f"  - {game_id}: {count} predictions")
        
        if self.results['errors']:
            print(f"\n❌ Errors Encountered:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if self.results['total_predictions'] == 0:
            print("  ❌ No predictions found in database")
            print("  🔧 Check if miners are running and submitting predictions")
            print("  🔧 Verify network connectivity to Bittensor")
            print("  🔧 Ensure validator is properly configured")
        elif self.results['miners_responded'] == 0:
            print("  ⚠️ No miners responded to queries")
            print("  🔧 Check if validator is registered on the network")
            print("  🔧 Verify firewall/port settings")
        else:
            print("  ✅ System appears to be working")
            print("  📊 Use game IDs from database for queries")
        
        # Save results
        self.save_results()
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"miner_test_results_{timestamp}.json"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")


async def main():
    """Main execution function"""
    tester = DirectMinerTester()
    results = await tester.run_test()
    
    print("\n🎉 Direct miner test completed!")
    return results


if __name__ == "__main__":
    # Run the test
    results = asyncio.run(main())
