#!/usr/bin/env python3
"""
Script to inspect active miners on the Bittensor network and their current state.
This helps debug why we might not be getting predictions.
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

async def inspect_network():
    """Inspect the current network state and active miners."""
    try:
        print("=== Bittensor Network Inspection ===")
        
        import bittensor as bt
        from bettensor.validator.bettensor_validator import BettensorValidator
        
        # Create a minimal validator instance
        validator = BettensorValidator()
        
        # Override default netuid to use subnet 3 (sports betting)
        validator.config.netuid = 3
        print(f"Targeting subnet {validator.config.netuid} (sports betting)")
        
        # Create temporary wallet
        temp_dir = tempfile.mkdtemp()
        validator.wallet = bt.wallet(
            name="temp_inspector",
            hotkey="temp_hotkey",
            path=temp_dir
        )
        validator.wallet.create_new_coldkey(use_password=False, overwrite=False)
        validator.wallet.create_new_hotkey(use_password=False, overwrite=False)
        
        # Connect to network
        validator.subtensor = bt.subtensor(config=validator.config)
        validator.metagraph = validator.subtensor.metagraph(validator.config.netuid)
        validator.metagraph.sync(subtensor=validator.subtensor, lite=True)
        
        print(f"Connected to subnet {validator.config.netuid}")
        print(f"Total neurons in network: {len(validator.metagraph.uids)}")
        
        # Analyze active miners
        active_miners = []
        total_miners = 0
        
        for i, axon in enumerate(validator.metagraph.axons):
            total_miners += 1
            if axon.ip != "0.0.0.0":
                hotkey = validator.metagraph.hotkeys[i]
                stake = validator.metagraph.S[i] if i < len(validator.metagraph.S) else 0
                active_miners.append({
                    'uid': i,
                    'hotkey': hotkey[:10] + "...",
                    'ip': axon.ip,
                    'port': axon.port,
                    'stake': float(stake),
                })
        
        print(f"Active miners (non-0.0.0.0 IP): {len(active_miners)}")
        print(f"Total network size: {total_miners}")
        
        # Show top 10 active miners by stake
        active_miners_sorted = sorted(active_miners, key=lambda x: x['stake'], reverse=True)
        print("\nTop 10 Active Miners by Stake:")
        print("UID | Hotkey     | IP            | Port | Stake")
        print("-" * 50)
        for miner in active_miners_sorted[:10]:
            print(f"{miner['uid']:3d} | {miner['hotkey']} | {miner['ip']:13s} | {miner['port']:4d} | {miner['stake']:.2f}")
        
        # Check network parameters
        print(f"\nNetwork Parameters:")
        print(f"- Subnet UID: {validator.config.netuid}")
        print(f"- Network: {validator.config.subtensor.network}")
        print(f"- Chain endpoint: {validator.subtensor.chain_endpoint}")
        
        # Test a simple query to one miner
        if active_miners:
            print(f"\n=== Testing Simple Query ===")
            test_miner = active_miners_sorted[0]
            print(f"Testing query to miner UID {test_miner['uid']} at {test_miner['ip']}:{test_miner['port']}")
            
            try:
                from bettensor.protocol import GameData
                validator.dendrite = bt.dendrite(wallet=validator.wallet)
                
                # Create a simple query
                synapse = GameData.create(
                    db_path="./temp_db.db",
                    wallet=validator.wallet,
                    subnet_version="1.0.0",
                    neuron_uid=0,
                    synapse_type="game_data"
                )
                
                # Query just one miner
                test_axon = validator.metagraph.axons[test_miner['uid']]
                response = await validator.dendrite(
                    axons=[test_axon],
                    synapse=synapse,
                    deserialize=True,
                    timeout=10
                )
                
                if response and len(response) > 0 and response[0] is not None:
                    print(f"✅ Received response from miner {test_miner['uid']}")
                    print(f"Response type: {type(response[0])}")
                    if hasattr(response[0], '__dict__'):
                        print(f"Response content: {response[0].__dict__}")
                else:
                    print(f"❌ No response from miner {test_miner['uid']}")
                    
            except Exception as e:
                print(f"❌ Error testing miner query: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n=== Network Inspection Complete ===")
        
    except Exception as e:
        print(f"Error during network inspection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(inspect_network())
