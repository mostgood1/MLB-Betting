import os
import sys
import datetime
from flask import Flask, render_template_string, request
import json
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


# Dynamically resolve the path to the src directory for imports
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mlb-team-comparator', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
try:
    from TodaysGames import get_games_for_date
    from mlb_sim_engine import simulate_game
except ImportError:
    # Fallback: try importlib for dynamic import
    import importlib.util
    import types
    def import_from_path(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    src_dir = SRC_PATH
    TodaysGames_mod = import_from_path('TodaysGames', os.path.join(src_dir, 'TodaysGames.py'))
    mlb_sim_engine_mod = import_from_path('mlb_sim_engine', os.path.join(src_dir, 'mlb_sim_engine.py'))
    get_games_for_date = TodaysGames_mod.get_games_for_date
    simulate_game = mlb_sim_engine_mod.simulate_game

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MLB Batch Simulation Results</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 0; }
        .container { max-width: 1200px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 32px; }
        h1 { text-align: center; }
        form { display: flex; justify-content: center; gap: 16px; margin-bottom: 32px; }
        label { font-weight: bold; }
        input[type="date"], input[type="number"] { padding: 4px 8px; border-radius: 4px; border: 1px solid #ccc; }
        button { padding: 6px 18px; border-radius: 4px; border: none; background: #1976d2; color: #fff; font-weight: bold; cursor: pointer; }
        button:hover { background: #125ea2; }
        table { width: 100%; border-collapse: collapse; margin-top: 24px; }
        th, td { padding: 8px 10px; text-align: center; border-bottom: 1px solid #eee; }
        th { background: #1976d2; color: #fff; }
        tr:nth-child(even) { background: #f2f6fa; }
        .error { color: #b71c1c; text-align: center; margin-bottom: 16px; }
        .chart-img { max-width: 100%; height: 320px; display: block; margin: 0 auto 24px auto; background: #f7f7f7; border-radius: 8px; }
        .stat-section { margin-bottom: 48px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MLB Batch Simulation Results</h1>
        <form method="post">
            <label for="date">Date:</label>
            <input type="date" id="date" name="date" value="{{ date }}" required>
            <label for="sims">Simulations per Game:</label>
            <input type="number" id="sims" name="sims" min="1" max="1000" value="{{ sims }}" required>
            <button type="submit">Run Simulation</button>
        </form>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if results %}
        <h2>Top 30 Team Simulation Averages for {{ date }} ({{ sims }} sims/game)</h2>
        <table>
            <tr>
                <th>Team</th>
                <th>Runs</th>
                <th>Hits</th>
                <th>SO</th>
                <th>BB</th>
                <th>HR</th>
            </tr>
            {% for entry in results %}
            <tr>
                <td>{{ entry.team }}</td>
                <td>{{ "%.2f"|format(entry.runs) }}</td>
                <td>{{ "%.2f"|format(entry.hits) }}</td>
                <td>{{ "%.2f"|format(entry.strikeouts) }}</td>
                <td>{{ "%.2f"|format(entry.walks) }}</td>
                <td>{{ "%.2f"|format(entry.hr) }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        {% if top_players and charts %}
        <hr/>
        {% for stat, label in [('runs','Runs'),('hits','Hits'),('strikeouts','SO'),('walks','BB'),('hr','HR')] %}
        <div class="stat-section">
            <h2>Top 30 Players by {{ label }}</h2>
            {% if charts[stat] %}
            <img class="chart-img" src="data:image/png;base64,{{ charts[stat] }}" alt="Top 30 {{ label }} Chart" />
            {% endif %}
            <table>
                <tr>
                    <th>Player</th>
                    <th>{{ label }}</th>
                </tr>
                {% for entry in top_players[stat] %}
                <tr>
                    <td>{{ entry.name }}</td>
                    <td>{{ "%.2f"|format(entry[stat]) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        <hr/>
        {% if pitcher_charts and top_pitchers %}
        {% for stat, label in [('strikeouts','SO'),('walks','BB'),('hr','HR Allowed')] %}
        <div class="stat-section">
            <h2>Top 30 Pitchers by {{ label }}</h2>
            {% if pitcher_charts[stat] %}
            <img class="chart-img" src="data:image/png;base64,{{ pitcher_charts[stat] }}" alt="Top 30 Pitchers {{ label }} Chart" />
            {% endif %}
            <table>
                <tr>
                    <th>Pitcher</th>
                    <th>{{ label }}</th>
                </tr>
                {% for entry in top_pitchers[stat] %}
                <tr>
                    <td>{{ entry.name }}</td>
                    <td>{{ "%.2f"|format(entry[stat]) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        {% endif %}
        {% endif %}
    </div>
</body>
</html>
'''

def batch_simulate(date, sim_count):
    games = get_games_for_date(date)
    if not games:
        return None, None, None, f"No games found for {date}"
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../mlb-team-comparator/src'))
    hitter_stats_cache = load_json(os.path.join(base_path, 'hitter_stats_cache.json'))
    pitcher_stats_2025andcareer = load_json(os.path.join(base_path, 'pitcher_stats_2025_and_career.json'))
    hvp_stats_cache = load_json(os.path.join(base_path, 'hvp_stats_cache.json'))
    projected_starters_cache = load_json(os.path.join(base_path, 'projected_starters_cache.json'))
    if not (hitter_stats_cache and pitcher_stats_2025andcareer and hvp_stats_cache):
        return None, None, None, "Missing one or more stat caches."
    all_team_stats = defaultdict(lambda: defaultdict(list))
    all_player_stats = defaultdict(lambda: defaultdict(list))
    all_pitcher_stats = defaultdict(lambda: defaultdict(list))
    import concurrent.futures
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

    def sim_args(away, home, date, away_starter_name, home_starter_name, pitcher_stats_2025andcareer):
        return dict(
            away=away,
            home=home,
            date=date,
            away_starter_name=away_starter_name,
            home_starter_name=home_starter_name,
            pitcher_stats_2025andcareer=pitcher_stats_2025andcareer
        )

    for g in games:
        away = g.get('away') or g.get('away_team')
        home = g.get('home') or g.get('home_team')
        if not away or not home:
            continue
        away_starter_name = get_real_starter(away, 'away', date, projected_starters_cache)
        home_starter_name = get_real_starter(home, 'home', date, projected_starters_cache)
        sim_kwargs = sim_args(away, home, date, away_starter_name, home_starter_name, pitcher_stats_2025andcareer)
        sims_to_run = [sim_kwargs for _ in range(sim_count)]
        results = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_sim = [executor.submit(_simulate_game_worker, kwargs) for kwargs in sims_to_run]
            for future in concurrent.futures.as_completed(future_to_sim):
                try:
                    sim = future.result()
                    if isinstance(sim, list) and sim:
                        sim = sim[0]
                    results.append(sim)
                except Exception:
                    continue
        for sim in results:
            if not sim:
                continue
            # Team stats
            for team, prefix in [(away, 'away'), (home, 'home')]:
                all_team_stats[team]['runs'].append(sim.get(f'{prefix}_score', 0))
                all_team_stats[team]['hits'].append(sum(v.get('H', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                all_team_stats[team]['strikeouts'].append(sum(v.get('SO', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                all_team_stats[team]['walks'].append(sum(v.get('BB', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                all_team_stats[team]['hr'].append(sum(v.get('HR', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
            # Player stats
            for pid, v in sim.get('hitter_stats', {}).items():
                name = v.get('name', pid)
                all_player_stats[name]['runs'].append(v.get('R', 0))
                all_player_stats[name]['hits'].append(v.get('H', 0))
                all_player_stats[name]['strikeouts'].append(v.get('SO', 0))
                all_player_stats[name]['walks'].append(v.get('BB', 0))
                all_player_stats[name]['hr'].append(v.get('HR', 0))
            # Pitcher stats
            for pid, v in sim.get('pitcher_stats', {}).items():
                name = v.get('name', pid)
                all_pitcher_stats[name]['strikeouts'].append(v.get('SO', 0))
                all_pitcher_stats[name]['walks'].append(v.get('BB', 0))
                all_pitcher_stats[name]['hr'].append(v.get('HR', 0))

def _simulate_game_worker(kwargs):
    # This function must be at module level for ProcessPoolExecutor
    import sys, os
    import importlib.util
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mlb-team-comparator', 'src'))
    if not os.path.isdir(src_path):
        # Try fallback: if running from MLBCompare, drop one '..'
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mlb-team-comparator', 'src'))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    def import_from_path(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    # Import TodaysGames robustly (even if not used, for consistency)
    todays_games_path_py = os.path.join(src_path, 'TodaysGames.py')
    todays_games_path_noext = os.path.join(src_path, 'TodaysGames')
    if os.path.isfile(todays_games_path_py):
        TodaysGames_mod = import_from_path('TodaysGames', todays_games_path_py)
    elif os.path.isfile(todays_games_path_noext):
        TodaysGames_mod = import_from_path('TodaysGames', todays_games_path_noext)
    # Import mlb_sim_engine
    mlb_sim_engine_path = os.path.join(src_path, 'mlb_sim_engine.py')
    mlb_sim_engine_mod = import_from_path('mlb_sim_engine', mlb_sim_engine_path)
    simulate_game = getattr(mlb_sim_engine_mod, 'simulate_game', None)
    return simulate_game(**kwargs)
    # Team averages
    team_averages = []
    for team, stats in all_team_stats.items():
        entry = {'team': team}
        for k, v in stats.items():
            entry[k] = round(sum(v)/len(v), 2) if v else 0.0
        team_averages.append(entry)
    team_averages.sort(key=lambda x: x['runs'], reverse=True)
    # Player averages
    player_averages = defaultdict(list)
    for name, stats in all_player_stats.items():
        for k, v in stats.items():
            avg = round(sum(v)/len(v), 2) if v else 0.0
            player_averages[k].append({'name': name, k: avg})
    pitcher_averages = defaultdict(list)
    for name, stats in all_pitcher_stats.items():
        for k, v in stats.items():
            avg = round(sum(v)/len(v), 2) if v else 0.0
            pitcher_averages[k].append({'name': name, k: avg})
    # For each stat, get top 30 players
    top_players = {}
    for stat in ['runs', 'hits', 'strikeouts', 'walks', 'hr']:
        arr = player_averages[stat]
        arr.sort(key=lambda x: x[stat], reverse=True)
        top_players[stat] = arr[:30]
    top_pitchers = {}
    # For pitcher strikeouts, sort descending (higher is better), for walks and HR allowed, sort ascending (lower is better)
    arr = pitcher_averages['strikeouts']
    arr.sort(key=lambda x: x['strikeouts'], reverse=True)
    top_pitchers['strikeouts'] = arr[:30]
    arr = pitcher_averages['walks']
    arr.sort(key=lambda x: x['walks'])
    top_pitchers['walks'] = arr[:30]
    arr = pitcher_averages['hr']
    arr.sort(key=lambda x: x['hr'])
    top_pitchers['hr'] = arr[:30]
    # Generate charts for each stat
    charts = {}
    for stat, label in zip(['runs', 'hits', 'strikeouts', 'walks', 'hr'], ['Runs', 'Hits', 'SO', 'BB', 'HR']):
        arr = top_players[stat]
        if not arr:
            charts[stat] = None
            continue
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar([x['name'] for x in arr], [x[stat] for x in arr], color='#1976d2')
        ax.set_title(f'Top 30 Players by {label}')
        ax.set_ylabel(label)
        ax.set_xlabel('Player')
        ax.set_xticks(range(len(arr)))
        ax.set_xticklabels([x['name'] for x in arr], rotation=90, fontsize=8)
        fig.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        charts[stat] = base64.b64encode(buf.read()).decode('utf-8')
    pitcher_charts = {}
    for stat, label in zip(['strikeouts', 'walks', 'hr'], ['SO', 'BB', 'HR Allowed']):
        arr = top_pitchers[stat]
        if not arr:
            pitcher_charts[stat] = None
            continue
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar([x['name'] for x in arr], [x[stat] for x in arr], color='#b71c1c')
        ax.set_title(f'Top 30 Pitchers by {label}')
        ax.set_ylabel(label)
        ax.set_xlabel('Pitcher')
        ax.set_xticks(range(len(arr)))
        ax.set_xticklabels([x['name'] for x in arr], rotation=90, fontsize=8)
        fig.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        pitcher_charts[stat] = base64.b64encode(buf.read()).decode('utf-8')
    return team_averages[:30], top_players, charts, top_pitchers, pitcher_charts, None

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    results = None
    top_players = None
    charts = None
    top_pitchers = None
    pitcher_charts = None
    today = datetime.date.today().strftime('%Y-%m-%d')
    date = today
    sims = 10
    if request.method == 'POST':
        date = request.form.get('date', today)
        try:
            sims = int(request.form.get('sims', 10))
            if sims < 1 or sims > 1000:
                raise ValueError
        except Exception:
            error = 'Invalid number of simulations.'
            sims = 10
        if not error:
            results, top_players, charts, top_pitchers, pitcher_charts, error = batch_simulate(date, sims)
    # On GET, do not run batch_simulate; only show the form with default values
    return render_template_string(HTML_TEMPLATE, date=date, sims=sims, results=results, top_players=top_players, charts=charts, top_pitchers=top_pitchers, pitcher_charts=pitcher_charts, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5002)
