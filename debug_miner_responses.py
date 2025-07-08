#!/usr/bin/env python3
"""
Debug script to specifically examine what miners are returning when queried.
"""

import asyncio
import sys
import os
import tempfile
from datetime import datetime, timezone

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def debug_miner_responses():
    """Debug miner responses to understand what they're returning."""
    try:
        print("=== Debugging Miner Responses ===")
        
        import bittensor as bt
        from bettensor.validator.bettensor_validator import BettensorValidator
        from bettensor.protocol import GameData
        
        # Create a minimal validator instance
        validator = BettensorValidator()
        validator.config.netuid = 3  # Sports betting subnet
        
        # Create temporary wallet
        temp_dir = tempfile.mkdtemp()
        validator.wallet = bt.wallet(
            name="temp_debug",
            hotkey="temp_hotkey",
            path=temp_dir
        )
        validator.wallet.create_new_coldkey(use_password=False, overwrite=False)
        validator.wallet.create_new_hotkey(use_password=False, overwrite=False)
        
        # Connect to network
        validator.subtensor = bt.subtensor(config=validator.config)
        validator.metagraph = validator.subtensor.metagraph(validator.config.netuid)
        validator.metagraph.sync(subtensor=validator.subtensor, lite=True)
        validator.dendrite = bt.dendrite(wallet=validator.wallet)
        
        print(f"Connected to subnet {validator.config.netuid}")
        print(f"Total neurons in network: {len(validator.metagraph.uids)}")
        
        # Get active miners
        active_miners = []
        for i, axon in enumerate(validator.metagraph.axons):
            if axon.ip != "0.0.0.0":
                active_miners.append((i, axon))
        
        print(f"Found {len(active_miners)} active miners")
        
        if active_miners:
            # Test with first 3 active miners
            test_miners = active_miners[:3]
            print(f"Testing with first 3 miners...")
            
            for miner_idx, (uid, axon) in enumerate(test_miners):
                print(f"\n--- Testing Miner {uid} at {axon.ip}:{axon.port} ---")
                
                try:
                    # Create GameData synapse
                    synapse = GameData.create(
                        db_path="./temp_debug.db",
                        wallet=validator.wallet,
                        subnet_version="1.0.0",
                        neuron_uid=uid,
                        synapse_type="game_data"
                    )
                    
                    print(f"Created synapse: {type(synapse)}")
                    print(f"Synapse metadata: {synapse.metadata}")
                    
                    # Query this specific miner
                    responses = await validator.dendrite(
                        axons=[axon],
                        synapse=synapse,
                        deserialize=True,
                        timeout=15
                    )
                    
                    print(f"Received {len(responses)} responses")
                    
                    if responses and len(responses) > 0:
                        response = responses[0]
                        print(f"Response type: {type(response)}")
                        print(f"Response is None: {response is None}")
                        
                        if response is not None:
                            # If it's a tuple, examine its contents
                            if isinstance(response, tuple):
                                print(f"Tuple length: {len(response)}")
                                for i, item in enumerate(response):
                                    print(f"Tuple[{i}]: {type(item)} = {item}")
                                    if hasattr(item, '__dict__'):
                                        print(f"  Item dict: {item.__dict__}")
                            else:
                                print(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                                
                                # Check for different response attributes
                                if hasattr(response, '__dict__'):
                                    print(f"Response dict: {response.__dict__}")
                                
                                if hasattr(response, 'prediction_dict'):
                                    print(f"Has prediction_dict: {response.prediction_dict is not None}")
                                    if response.prediction_dict:
                                        print(f"Prediction dict keys: {list(response.prediction_dict.keys())}")
                                
                                if hasattr(response, 'gamedata_dict'):
                                    print(f"Has gamedata_dict: {response.gamedata_dict is not None}")
                                    if response.gamedata_dict:
                                        print(f"Gamedata dict keys: {list(response.gamedata_dict.keys())}")
                                
                                if hasattr(response, 'confirmation_dict'):
                                    print(f"Has confirmation_dict: {response.confirmation_dict is not None}")
                                
                                if hasattr(response, 'error'):
                                    print(f"Response error: {response.error}")
                    else:
                        print("No response received")
                    
                    # Also test with prediction synapse type
                    print(f"\n--- Testing Miner {uid} with prediction synapse ---")
                    try:
                        pred_synapse = GameData.create(
                            db_path="./temp_debug.db",
                            wallet=validator.wallet,
                            subnet_version="1.0.0",
                            neuron_uid=uid,
                            synapse_type="prediction"  # Different synapse type
                        )
                        
                        pred_responses = await validator.dendrite(
                            axons=[axon],
                            synapse=pred_synapse,
                            deserialize=True,
                            timeout=15
                        )
                        
                        if pred_responses and pred_responses[0] is not None:
                            pred_response = pred_responses[0]
                            print(f"Prediction synapse response type: {type(pred_response)}")
                            if isinstance(pred_response, tuple):
                                print(f"Prediction tuple length: {len(pred_response)}")
                                for i, item in enumerate(pred_response):
                                    print(f"Prediction tuple[{i}]: {type(item)}")
                                    if hasattr(item, '__dict__') and item.__dict__:
                                        print(f"  Prediction item dict: {item.__dict__}")
                        else:
                            print("No prediction response")
                    except Exception as e:
                        print(f"Error with prediction synapse: {e}")
                        
                except Exception as e:
                    print(f"Error querying miner {uid}: {e}")
                    import traceback
                    traceback.print_exc()
        
        print("\n=== Debug Complete ===")
        
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_miner_responses())
