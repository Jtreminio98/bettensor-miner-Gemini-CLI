
import json
import requests
from datetime import datetime
from config import API_KEY

PICKS_FILE = 'my_picks.json'
BASE_URLS = {
    'MLB': 'https://v1.baseball.api-sports.io',
    'Tennis': 'https://v1.tennis.api-sports.io'
}
HEADERS = {
    'x-rapidapi-key': API_KEY
}

def get_picks():
    """Loads picks from the JSON file."""
    try:
        with open(PICKS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_picks(picks):
    """Saves picks to the JSON file."""
    with open(PICKS_FILE, 'w') as f:
        json.dump(picks, f, indent=2)

def get_game_id(sport, team_name, game_date):
    """Gets the API-Sports game ID for a given game."""
    if sport not in BASE_URLS:
        return None

    url = f"{BASE_URLS[sport]}/games"
    
    if sport == 'MLB':
        # Corrected parameter for MLB
        params = {'date': game_date, 'team': team_name}
    else: # Tennis
        params = {'date': game_date, 'search': team_name}

    print(f"  - Searching for game ID with URL: {url} and params: {params}")
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"  - API Response for game ID: {data}")

        if data['response']:
            # Find the specific game if multiple are returned
            for game in data['response']:
                if team_name in game['teams']['home']['name'] or team_name in game['teams']['away']['name']:
                    return game['id']
    except requests.exceptions.RequestException as e:
        print(f"  - API Error while getting game ID: {e}")
    return None


def get_game_results(sport, game_id):
    """Gets the results for a specific game ID."""
    if sport not in BASE_URLS:
        return None

    url = f"{BASE_URLS[sport]}/games"
    params = {'id': game_id}

    print(f"  - Getting results with URL: {url} and params: {params}")
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"  - API Response for game results: {data}")
        return data['response'][0] if data['response'] else None
    except requests.exceptions.RequestException as e:
        print(f"  - API Error while getting game results: {e}")
    return None


def did_pick_win(pick, game_result):
    """Determines if a pick was a winner."""
    bet_type = pick.get('bet_type')
    prediction = pick.get('prediction')
    sport = pick.get('sport')

    if not game_result:
        return False

    if sport == 'MLB' and bet_type == 'Spread':
        team_name, spread_str = prediction.rsplit(' ', 1)
        spread = float(spread_str)
        
        home_team_name = game_result['teams']['home']['name']
        away_team_name = game_result['teams']['away']['name']
        
        home_score = game_result['scores']['home']['total']
        away_score = game_result['scores']['away']['total']

        if team_name in home_team_name:
            return (home_score + spread) > away_score
        else:
            return (away_score + spread) > home_score
            
    if sport == 'Tennis':
        player_name = prediction.split(' ')[0]
        winner = game_result.get('winner')
        if bet_type == 'Moneyline':
            return winner and player_name in winner.get('name', '')
        if bet_type == 'Set Betting':
            player_name, set_score_str = prediction.rsplit(' ', 1)
            home_sets = game_result['scores']['home'].get('sets', 0)
            away_sets = game_result['scores']['away'].get('sets', 0)
            actual_score_str = f"{home_sets}-{away_sets}"
            if player_name in game_result['teams']['home']['name']:
                return actual_score_str == set_score_str
            elif player_name in game_result['teams']['away']['name']:
                return f"{away_sets}-{home_sets}" == set_score_str


    return False


def update_results():
    """
    Updates the results of pending picks using the API.
    """
    picks = get_picks()
    if not picks:
        print("No picks found.")
        return

    for pick in picks:
        if pick.get('status') == 'pending':
            game_date = pick['event_details']['date']
            game_name = pick['event_details']['game']
            sport = pick['sport']
            
            print(f"\nUpdating results for: {game_name} ({sport}) on {game_date}")

            if datetime.strptime(game_date, '%Y-%m-%d').date() > datetime.now().date():
                print("  - Game is in the future, skipping.")
                continue

            team_to_search = game_name.split(' vs ')[0]
            
            game_id = get_game_id(sport, team_to_search, game_date)

            if game_id:
                game_result = get_game_results(sport, game_id)
                
                if game_result and game_result.get('status', {}).get('long') == 'Finished':
                    if did_pick_win(pick, game_result):
                        pick['status'] = 'win'
                        if pick['odds']:
                            pick['profit_loss'] = pick['stake'] * (pick['odds'] - 1)
                        else:
                            pick['profit_loss'] = pick['stake']
                    else:
                        pick['status'] = 'loss'
                        pick['profit_loss'] = -pick['stake']
                    
                    print(f"  - Status updated to: {pick['status']}")
                else:
                    print("  - Game has not finished yet or result is not available.")
            else:
                print("  - Could not find a matching game ID.")

    save_picks(picks)
    print("\nFinished updating results.")


if __name__ == '__main__':
    update_results()
