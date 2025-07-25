### **Development Status & Data Extraction**

This repository also contains a suite of tools for extracting and analyzing sports betting predictions from the Bettensor network.

**Goal:** Programmatically extract and aggregate miner predictions to identify consensus betting signals, and provide a robust system for tracking the performance of manual picks.

**Current Status:**
- **Performance Tracking System:** A new system has been implemented to track the performance of manual picks. This includes scripts to automatically update results from a Sports Data API and generate detailed performance reports.
- **Core Validator is Functional:** The validator codebase has been debugged and is operational for network interaction.
- **Local Database is Initialized:** The `validator.db` SQLite database is successfully initialized with the correct schema.
- **Architecture Understood:** The correct data extraction pattern has been identified.

**Next Steps:**
The immediate focus is on continuing to improve the reliability of the `results_updater.py` script and expanding the features of the performance reporting tools.


---

<div align="center">

![Bettensor Logo](./docs/assets/bettensor-twitter-header.jpg) 






A sports prediction subnet on the Bittensor network

[Installation](#installation-and-setup) • [Validators](#guide-for-validators) • [Miners](#guide-for-miners) • [Release Details](#details-for-current-release-version-v001-beta) • [Website](https://bettensor.com) • [Official Discord Server](https://discord.gg/YVyVHHEd) 

</div>

## What Is Bettensor?

Bettensor is a sports prediction subnet. The goal of Bettensor is to provide a platform for sports fans to predict the outcomes of their favorite sporting events, and ML/AI researchers to develop new models and strategies to benchmark against good, old fashioned human intelligence and intuition. 

Mining on this subnet is simple. In this Beta release, miners receive upcoming games and odds, submit predictions as a simulated wager, and are rewarded for correct predictions upon game conclusion. Compute requirements are minimal for those choosing the human intelligence method - all you need is to consistently submit predictions for upcoming games.



> [!IMPORTANT]
> **Before you begin using our services, please read this legal disclaimer carefully:**

>- **Nature of Service:** Bettensor is a software application developed on the Bittensor network, which operates independently of our control. We are not a financial institution, nor do we facilitate any monetary transactions directly. Bettensor does not distribute payments nor collects money, whether in the form of cryptocurrencies or fiat currencies.

>- **Rewards and Transactions:** Users of Bettensor engage directly with the Bittensor network. Rewards or payments are issued by the Bittensor network based on the protocols established within its framework. Bettensor's role is limited to providing software that suggests allocation of $TAO tokens based on the predictions made by users. We do not influence or control the decision-making process of the Bittensor network concerning the distribution of rewards.

>- **No Financial Advice:** The information provided by Bettensor is for informational purposes only and should not be considered financial advice. Users should conduct their own research or consult with a professional advisor before engaging in any betting activities.

>- **Assumption of Risk:** By using Bettensor, users acknowledge and accept the risks associated with online betting and digital transactions, including but not limited to the risk of financial loss. Users should engage with the platform responsibly and within the bounds of applicable laws and regulations.

>- **Compliance with Laws:** Users of Bettensor are solely responsible for ensuring that their actions comply with local, state, and federal laws applicable to sports betting and online gambling. Bettensor assumes no responsibility for illegal or unauthorized use of the service.

>- **Changes and Amendments:** We reserve the right to modify this disclaimer at any time. Users are encouraged to periodically review this document to stay informed of any changes.

>By using Bettensor, you acknowledge that you have read, understood, and agreed to the terms outlined in this legal disclaimer. If you do not agree with any part of this disclaimer, you should not use Bettensor.


## Installation and Setup

To mine or validate on this subnet, we recommend starting with a cheap VPS instance running Ubuntu 22.04. As with most Subnets, we also recommend running your own Lite Node. You can find a guide to running a Lite Node [here](https://docs.bittensor.com/subtensor-nodes/). 

>[!NOTE]
>In this current Beta version, we require Bittensor v6.9.3.

1. Clone the repository:
```bash
git clone https://github.com/bettensor/bettensor.git
```

2. Update apt-get:
```bash
sudo apt-get update
```

4. Run the setup script:
```bash
cd bettensor
chmod +x scripts/setup.sh
source ./scripts/setup.sh
```
   - if you want to set up a lite node (recommended), run the command with the flag `source ./scripts/setup.sh --lite-node`

   - additionally, the script takes `--subtensor.network` as an optional flag. if you want to run the lite node on testnet, run `source ./scripts/setup.sh --subtensor.network test` , or `main` for mainnet.

7. Set up a Bittensor wallet (guide [here](https://docs.bittensor.com/getting-started/wallets)).

8. Register on the subnet:

- Mainnet `(NETUID 30)`:

 ```bash
btcli subnet register --netuid 30 --wallet.name <YOUR_COLDKEY> --wallet.hotkey <YOUR_HOTKEY>
 ```
- Testnet `(NETUID: 181)`:

 ```bash
btcli subnet register --netuid 181 --wallet.name <YOUR_COLDKEY> --wallet.hotkey <YOUR_HOTKEY> --subtensor.network test
 ```




## Guide for Validators

For detailed instructions on setting up and running a Bettensor validator, please refer to our [Validator Guide](docs/validating.md). This document covers:

- Setting up the environment
- Running the validator
- Recommended logging settings

Whether you're new to Bettensor or an experienced validator, the Validator Guide provides all the information you need to participate in the network effectively.




## Guide for Miners

For detailed instructions on setting up and running a Bettensor miner, please refer to our [Miner Guide](docs/mining.md). This comprehensive document covers:

- Miner setup and configuration
- Choosing between Local and Central Server interfaces
- Submitting predictions
- Managing multiple miners
- Security considerations
- Troubleshooting and FAQs

Whether you're new to Bettensor or an experienced miner, the Miner Guide provides all the information you need to participate in the network effectively.




## Incentive Mechanism and Scoring
The incentive mechanism is intricate and rewards the best miners disproportionately. Details around the mechanism can be found [here](https://nickel5.substack.com/p/sports-prediction-and-betting-models).


## Minimum Staking Requirement

To ensure commitment to the network and prevent abuse, miners are required to meet a minimum staking threshold to receive weight from validators. This stake requirement helps maintain network quality and security.

### How to Add Stake to Your Hotkey

Miners can earn stake through incentive mechanisms or by manually adding it using the btcli command:

#### Adding stake to a single hotkey:
```bash
btcli stake add --amount .3 --netuid 30 --wallet.name <YOUR_COLDKEY> --wallet.hotkey <YOUR_HOTKEY>
```

#### Adding stake to multiple hotkeys simultaneously:
```bash
btcli stake add --amount .6 --netuid 30 --wallet.name <YOUR_COLDKEY> --wallet.hotkey hotkey1,hotkey2
```

>[!NOTE]
>The minimum stake amount is decided by validators. Miners without sufficient stake will not receive weight in the network, regardless of their performance or tier. Make sure to check your stake levels regularly.


## Details for Current Release Version (v2.0.0, Beta)

- Currently Supported Sports: Baseball, Football (Soccer), American Football
- Currently available base models: (Football (Soccer): UEFA Teams, NFL)
- Requires Bittensor==v6.9.4. Support for Bittensor v7.x is coming soon.





## License

This repository is licensed under the MIT License.

```text
The MIT License (MIT)
Copyright © 2024 Bettensor (oneandahalfcats, geardici, honeybadgerhavoc)

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
<div align="center">

![Bettensor Logo](./docs/assets/bettensor_spin_animation.gif) 
</div>

## Custom Miner for Manual Predictions

This repository includes a custom miner script, `my_miner.py`, designed for users who want to manually input their own predictions. This is ideal for those who prefer to use their own analysis rather than relying on the default prediction models.

### How It Works

The custom miner operates in a simple loop:

1.  **Reads Picks:** The miner reads a list of predictions from the `my_picks.json` file.
2.  **Listens for Requests:** It connects to the Bittensor network and listens for requests from validators.
3.  **Serves Predictions:** When a validator queries the miner, it responds with the first prediction from the `my_picks.json` file.

## Performance Tracking

To provide a robust way to evaluate betting performance, this repository now includes a comprehensive performance tracking system. This system automates the process of recording picks, fetching results, and generating performance reports.

### How It Works

1.  **Structured Data:** All picks are stored in `my_picks.json` with detailed information, including the sport, teams, bet type, odds, stake, and the final result (`win`, `loss`, `pending`).
2.  **Automated Results Updater:** The `results_updater.py` script uses a professional Sports Data API (**API-Sports**) to reliably fetch the final scores of completed games. It then automatically updates the status and profit/loss for each pick in `my_picks.json`.
3.  **Performance Reporter:** The `performance_reporter.py` script reads the updated data and generates detailed reports for weekly, monthly, or all-time performance. These reports include key metrics like win/loss record, total amount staked, net profit/loss, and return on investment (ROI).

This system provides an accurate and automated way to track and analyze betting performance over time.

### `my_picks.json` File

The `my_picks.json` file is where you store your predictions. It's a simple JSON array of objects, where each object represents a single pick. The structure is flexible to accommodate various types of bets.

**Example:**

```json
[
  {
    "sport": "Baseball",
    "league": "MLB",
    "event_details": {
      "game": "Philadelphia Phillies vs. Boston Red Sox",
      "date": "2025-07-23"
    },
    "bet_type": "Spread",
    "prediction": "Philadelphia Phillies -1.5",
    "odds": 2.36,
    "reasoning": "User provided pick.",
    "stake": 5.00,
    "status": "loss",
    "profit_loss": -5.00
  },
  {
    "sport": "Tennis",
    "league": "ATP",
    "event_details": {
      "game": "F. Tiafoe vs Flavio Cobolli",
      "date": "2025-07-25"
    },
    "bet_type": "Moneyline",
    "prediction": "F. Tiafoe",
    "odds": null,
    "reasoning": "User provided pick.",
    "stake": 5.0,
    "status": "pending",
    "profit_loss": 0.0
  }
]
```

### Running the Tools

You can run the performance tools using the following commands:

-   **Update Results:**
    ```bash
    python3 results_updater.py
    ```
-   **Generate Reports:**
    ```bash
    # For daily stats
    python3 performance_reporter.py daily

    # For weekly stats
    python3 performance_reporter.py weekly

    # For monthly stats
    python3 performance_reporter.py monthly

    # For all-time stats
    python3 performance_reporter.py all
    ```

### `my_picks.json` File

The `my_picks.json` file is where you store your predictions. It's a simple JSON array of objects, where each object represents a single pick. The structure is flexible to accommodate various types of bets.

**Example:**

```json
[
  {
    "sport": "Horse Racing",
    "event_details": {
      "track": "Roscommon",
      "time": "05:25",
      "selection": "Neo Smart & Gabriella Hill(10)"
    },
    "bet_type": "Win",
    "confidence": 0.624,
    "reasoning": "High win probability, consistent performance, favorable odds."
  },
  {
    "sport": "Baseball",
    "league": "MLB",
    "event_details": {
      "game": "Philadelphia Phillies vs Opponent"
    },
    "bet_type": "Spread",
    "prediction": "Philadelphia Phillies -1.5",
    "odds": 2.05,
    "reasoning": "Solid recent performance, strong pitching matchup, opponent's road struggles."
  }
]
```

You can add as many picks as you like to this file. The miner will currently only serve the first one, but this can be easily extended to support more advanced logic.

### Running the Custom Miner

To run the custom miner, use the following command:

```bash
python3 my_miner.py
```

The script is configured to use the `default` wallet and hotkey.

### Registration

> [!IMPORTANT]
> Before you can run the miner on the network, you must register your hotkey on the Bettensor subnet (netuid 30). This requires a small amount of TAO to cover the transaction fee.
>
> Use the following command to register your hotkey:
>
> ```bash
> btcli subnet register --netuid 30 --wallet.name default --wallet.hotkey default --subtensor.network finney
> ```

---
