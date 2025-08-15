import sys
import datetime
import json
from collections import defaultdict

sys.path.append('../mlb-team-comparator/src')
from TodaysGames import get_games_for_date
from mlb_sim_engine import simulate_game

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def main(date=None, sim_count=10):
    if not date:
        date = datetime.date.today().strftime('%Y-%m-%d')
    games = get_games_for_date(date)
    if not games:
        print(f"No games found for {date}")
        return
    # Load caches (adjust path as needed)
    base_path = '../mlb-team-comparator/src'
    hitter_stats_cache = load_json(base_path + '/hitter_stats_cache.json')
    pitcher_stats_2025andcareer = load_json(base_path + '/pitcher_stats_2025_and_career.json')
    hvp_stats_cache = load_json(base_path + '/hvp_stats_cache.json')
    projected_starters_cache = load_json(base_path + '/projected_starters_cache.json')
    if not (hitter_stats_cache and pitcher_stats_2025andcareer and hvp_stats_cache):
        print("Missing one or more stat caches.")
        return
    all_team_stats = defaultdict(lambda: defaultdict(list))
    for g in games:
        away = g.get('away') or g.get('away_team')
        home = g.get('home') or g.get('home_team')
        if not away or not home:
            continue
        # Try to get real starter names if available
        def get_real_starter(team, side, date_key, starters_cache):
            if not starters_cache or date_key not in starters_cache:
                return None
            entries = starters_cache[date_key]
            for entry in entries:
                if side == 'away':
                    if team == entry.get('away_team') or team == entry.get('away_team_normalized'):
                        return entry.get('away_starter')
                elif side == 'home':
                    if team == entry.get('home_team') or team == entry.get('home_team_normalized'):
                        return entry.get('home_starter')
            return None
        away_starter_name = get_real_starter(away, 'away', date, projected_starters_cache)
        home_starter_name = get_real_starter(home, 'home', date, projected_starters_cache)
        for i in range(sim_count):
            try:
                sim = simulate_game(
                    away,
                    home,
                    date=date,
                    away_starter_name=away_starter_name,
                    home_starter_name=home_starter_name,
                    pitcher_stats_2025andcareer=pitcher_stats_2025andcareer
                )
                if isinstance(sim, list) and sim:
                    sim = sim[0]
                # Aggregate stats for both teams
                for team, prefix in [(away, 'away'), (home, 'home')]:
                    all_team_stats[team]['runs'].append(sim.get(f'{prefix}_score', 0))
                    all_team_stats[team]['hits'].append(sum(v.get('H', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                    all_team_stats[team]['strikeouts'].append(sum(v.get('SO', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                    all_team_stats[team]['walks'].append(sum(v.get('BB', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                    all_team_stats[team]['hr'].append(sum(v.get('HR', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
            except Exception as e:
                continue
    # Compute averages
    team_averages = []
    for team, stats in all_team_stats.items():
        entry = {'team': team}
        for k, v in stats.items():
            entry[k] = round(sum(v)/len(v), 2) if v else 0.0
        team_averages.append(entry)
    # Sort by runs scored, descending
    team_averages.sort(key=lambda x: x['runs'], reverse=True)
    # Print top 30
    print(f"Top 30 Team Simulation Averages for {date} (over {sim_count} sims per game):")
    print("Team      Runs   Hits   SO   BB   HR")
    for entry in team_averages[:30]:
        print(f"{entry['team']:<10} {entry['runs']:<6} {entry['hits']:<6} {entry['strikeouts']:<6} {entry['walks']:<6} {entry['hr']:<6}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simulate all MLB games for a date and show top 30 team averages.")
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--sims', type=int, default=10, help='Number of simulations per game (default: 10)')
    args = parser.parse_args()
    main(args.date, args.sims)
