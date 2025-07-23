
import bittensor as bt
import json
import time
import os
import argparse

class MyMiner:
    def __init__(self):
        self.config = self.get_config()
        self.setup_bittensor()
        self.load_picks()

    def get_config(self):
        # Set up the configuration, using command-line arguments
        # You can override these with command-line arguments
        parser = argparse.ArgumentParser()
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        bt.logging.add_args(parser)
        bt.axon.add_args(parser)
        config = bt.config(parser)

        config.wallet.name = "default"
        config.wallet.hotkey = "default"
        config.netuid = 30  # Bettensor subnet
        config.subtensor.network = "finney" # or "test" for testnet
        config.subtensor.chain_endpoint = "wss://bittensor-finney.api.onfinality.io/public-ws"
        config.logging.debug = True # Enable debug logging
        return config

    def setup_bittensor(self):
        # Set up Bittensor objects
        bt.logging(config=self.config)
        self.wallet = bt.wallet(config=self.config)
        self.subtensor = bt.subtensor(config=self.config)
        self.metagraph = self.subtensor.metagraph(self.config.netuid)
        self.axon = bt.axon(wallet=self.wallet, config=self.config)

    def load_picks(self):
        # Load picks from the JSON file
        picks_file = os.path.join(os.path.dirname(__file__), 'my_picks.json')
        try:
            with open(picks_file, 'r') as f:
                self.picks = json.load(f)
            bt.logging.info(f"✅ Loaded {len(self.picks)} picks from {picks_file}")
        except FileNotFoundError:
            bt.logging.error(f"❌ Picks file not found at {picks_file}")
            self.picks = []
        except json.JSONDecodeError:
            bt.logging.error(f"❌ Error decoding JSON from {picks_file}")
            self.picks = []

    def forward_fn(self, synapse: bt.Synapse) -> bt.Synapse:
        # This function is called when a validator queries the miner.
        # For now, we'll just return the first pick.
        if self.picks:
            pick = self.picks[0]
            synapse.prediction = pick
            bt.logging.info(f"📬 Responding with pick: {pick}")
        else:
            synapse.prediction = {"error": "No picks available"}
            bt.logging.warning("⚠️ No picks loaded, responding with an error.")

        return synapse

    def run(self):
        # Attach the forward function to the axon
        self.axon.attach(forward_fn=self.forward_fn)

        # Serve the axon
        self.axon.serve(netuid=self.config.netuid, subtensor=self.subtensor)

        # Start the axon
        self.axon.start()

        bt.logging.info(f"🔥 Miner started on UID {self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)}")
        bt.logging.info("Serving predictions... (Press CTRL+C to stop)")

        # Keep the miner running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            bt.logging.info("🛑 Stopping miner...")
            self.axon.stop()

if __name__ == "__main__":
    miner = MyMiner()
    miner.run()
