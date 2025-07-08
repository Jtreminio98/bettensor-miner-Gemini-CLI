# data_extractor.py

"""
This script directly initializes the ScoringSystem to extract aggregated miner weights,
bypassing the full validator initialization to avoid hanging issues.
"""

import sys
import os
import asyncio
import traceback
from datetime import datetime, timezone, timedelta
from sqlalchemy import text

# Manually add the project root to the Python path to fix module import issues.
# This is a robust workaround for environment configuration problems.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def inspect_db_state(db_manager):
    """Connects to the database and prints the row counts of key tables."""
    print("\n--- Inspecting Database State ---")
    try:
        async with db_manager.get_session() as session:
            # Count rows in game_data
            game_data_count_result = await session.execute(text("SELECT COUNT(*) FROM game_data"))
            game_data_count = game_data_count_result.scalar_one()
            print(f"Total rows in game_data: {game_data_count}")

            # Count rows in predictions
            predictions_count_result = await session.execute(text("SELECT COUNT(*) FROM predictions"))
            predictions_count = predictions_count_result.scalar_one()
            print(f"Total rows in predictions: {predictions_count}")
            print("---------------------------------")

    except Exception as e:
        print(f"An error occurred during database inspection: {e}")

async def show_live_predictions(scoring_system):
    """Fetches and displays the last 10 predictions in a human-readable format."""
    print("\nFetching the 10 most recent predictions with game details...")
    
    from bettensor.validator.utils.scoring.scoring_data import ScoringData
    scoring_data = ScoringData(scoring_system)

    try:
        predictions_with_details = await scoring_data.fetch_recent_predictions_with_details(limit=10)
        
        if not predictions_with_details:
            print("No predictions found in the database.")
            return

        print("\n--- Last 10 Miner Sports Picks ---")
        for i, pred in enumerate(predictions_with_details):
            # Determine the predicted outcome
            if pred['predicted_outcome'] == 0:
                pick = f"{pred['home_team']} (Home)"
            elif pred['predicted_outcome'] == 1:
                pick = f"{pred['away_team']} (Away)"
            else:
                pick = "Tie"

            # Format the output
            print(
                f"{i+1}. Miner UID {pred['miner_uid']} predicts in {pred['sport']}:\n"
                f"   Game: {pred['home_team']} vs. {pred['away_team']}\n"
                f"   Pick: {pick}\n"
                f"   Odds: {pred['predicted_odds']:.2f}\n"
                f"   Wager: {pred['wager']:.2f}\n"
                f"   Date: {pred['prediction_date']}\n"
            )
        print("----------------------------------")

    except Exception as e:
        print(f"An error occurred while fetching predictions with details: {e}")

async def main():
    """Main function to initialize and run the data extractor."""
    import sys
    print("--- Script execution started from __main__ block. ---"); sys.stdout.flush()
    validator = None
    try:
        print("--- Script entered main function. About to import libraries. ---"); sys.stdout.flush()
        from bettensor.validator.bettensor_validator import BettensorValidator
        from bettensor.validator.utils.scoring.scoring import ScoringSystem

        print("--- Libraries imported successfully. ---"); sys.stdout.flush()

        print("--- Starting Data Extractor ---"); sys.stdout.flush()

        # 1. Initialize Validator with correct subnet
        print("--- Initializing Validator for data extraction... ---"); sys.stdout.flush()
        validator = BettensorValidator()
        
        # Override the default netuid to use subnet 3 (sports betting)
        validator.config.netuid = 3
        print(f"Using subnet {validator.config.netuid} (sports betting)")
        
        await validator.init_for_data_extraction()
        print("--- Validator initialized. ---"); sys.stdout.flush()

        # 2. Get scoring system from validator (already initialized)
        print("--- Getting scoring system from validator... ---"); sys.stdout.flush()
        scoring_system = validator.scoring_system
        print("--- Scoring system ready. ---"); sys.stdout.flush()

        # 3. Fetch live game data to populate the database
        print("\n--- Fetching live game data from the network... ---")
        try:
            from neurons.validator import update_game_data
            from datetime import datetime, timezone

            current_time = datetime.now(timezone.utc)
            print(f"Current time: {current_time}")
            print(f"Validator sports_data available: {hasattr(validator, 'sports_data')}")
            if hasattr(validator, 'sports_data'):
                print(f"Sports data type: {type(validator.sports_data)}")
            
            await update_game_data(validator, current_time, deep_query=True)
            print("--- Live game data fetched successfully. ---")
            
            # Check if any game data was actually inserted
            async with validator.db_manager.get_session() as session:
                from sqlalchemy import text
                game_count_result = await session.execute(text("SELECT COUNT(*) FROM game_data"))
                game_count = game_count_result.scalar_one()
                print(f"Game data rows after fetch: {game_count}")
                
                if game_count > 0:
                    # Show sample game data
                    sample_games_result = await session.execute(text("SELECT game_id, team_a, team_b, sport, event_start_date FROM game_data LIMIT 3"))
                    sample_games = sample_games_result.fetchall()
                    print("Sample games:")
                    for game in sample_games:
                        print(f"  - {game.sport}: {game.team_a} vs {game.team_b} on {game.event_start_date}")
                        
        except Exception as e:
            print(f"An error occurred while fetching game data: {e}")
            import traceback
            traceback.print_exc()

        # 4. Query miners for predictions
        print("\n--- Querying miners for predictions... ---")
        try:
            # The forward pass queries miners for predictions on the latest game data.
            # This is the step that populates the 'predictions' table.
            await validator.forward()
            print("--- Miner predictions queried successfully. ---")
        except Exception as e:
            print(f"An error occurred while querying miners for predictions: {e}")
            import traceback
            traceback.print_exc()

        # 5. Inspect database state to see if predictions were written
        await inspect_db_state(validator.db_manager)

        # 6. Show live predictions (which should now exist in the database)
        await show_live_predictions(scoring_system)
        print("\n--- Script finished after fetching predictions ---")
        return

    except Exception as e:
        print(f"An error occurred in the main execution block: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if validator:
            try:
                await validator.cleanup()
                print("\nValidator cleaned up and database connection closed."); sys.stdout.flush()
            except Exception as e:
                # This can happen if cleanup is called on a partially initialized validator
                print(f"\nIgnoring cleanup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
