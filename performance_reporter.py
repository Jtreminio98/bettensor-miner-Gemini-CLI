
import json
from datetime import datetime, timedelta
import argparse

PICKS_FILE = 'my_picks.json'

def get_picks():
    """Loads picks from the JSON file."""
    try:
        with open(PICKS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def generate_report(period):
    """
    Generates a performance report for a given period.

    Args:
        period (str): 'daily', 'weekly', 'monthly', or 'all'.
    """
    picks = get_picks()
    if not picks:
        print("No picks found.")
        return

    today = datetime.now().date()
    
    if period == 'daily':
        start_of_period = today
        period_name = f"Today ({today.strftime('%Y-%m-%d')})"
    elif period == 'weekly':
        start_of_period = today - timedelta(days=today.weekday())
        period_name = f"This Week ({start_of_period.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')})"
    elif period == 'monthly':
        start_of_period = today.replace(day=1)
        period_name = f"This Month ({start_of_period.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')})"
    elif period == 'all':
        start_of_period = datetime.min.date()
        period_name = "All Time"
    else:
        print(f"Invalid period: {period}")
        return

    total_staked = 0
    total_profit_loss = 0
    wins = 0
    losses = 0
    pending = 0

    for pick in picks:
        pick_date_str = pick.get('event_details', {}).get('date')
        if not pick_date_str:
            continue

        pick_date = datetime.strptime(pick_date_str, '%Y-%m-%d').date()

        if pick_date < start_of_period:
            continue
        
        if pick.get('status') in ['win', 'loss']:
            total_staked += pick.get('stake', 0)
            total_profit_loss += pick.get('profit_loss', 0)

        if pick.get('status') == 'win':
            wins += 1
        elif pick.get('status') == 'loss':
            losses += 1
        elif pick.get('status') == 'pending':
            pending += 1

    roi = (total_profit_loss / total_staked) * 100 if total_staked > 0 else 0

    print(f"--- Performance Report: {period_name} ---")
    print("-" * 40)
    print(f"Record (W-L-P):      {wins}-{losses}-{pending}")
    print(f"Total Amount Staked: ${total_staked:,.2f}")
    print(f"Total Profit/Loss:   ${total_profit_loss:,.2f}")
    print(f"Return on Investment: {roi:.2f}%")
    print("-" * 40)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a performance report for your picks.')
    parser.add_argument('period', type=str, nargs='?', default='all', choices=['daily', 'weekly', 'monthly', 'all'],
                        help="The reporting period: 'daily', 'weekly', 'monthly', or 'all' (default).")
    args = parser.parse_args()
    generate_report(args.period)
