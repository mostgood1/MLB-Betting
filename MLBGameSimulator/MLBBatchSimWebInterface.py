import os
import sys
import datetime
from flask import Flask, render_template_string, request
import json
from collections import defaultdict

# Adjust path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../mlb-team-comparator/src')))
from TodaysGames import get_games_for_date
from mlb_sim_engine import simulate_game

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
        .container { max-width: 900px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 32px; }
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
    </div>
</body>
</html>
'''

def batch_simulate(date, sim_count):
    games = get_games_for_date(date)
    if not games:
        return None, f"No games found for {date}"
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../mlb-team-comparator/src'))
    hitter_stats_cache = load_json(os.path.join(base_path, 'hitter_stats_cache.json'))
    pitcher_stats_2025andcareer = load_json(os.path.join(base_path, 'pitcher_stats_2025_and_career.json'))
    hvp_stats_cache = load_json(os.path.join(base_path, 'hvp_stats_cache.json'))
    projected_starters_cache = load_json(os.path.join(base_path, 'projected_starters_cache.json'))
    if not (hitter_stats_cache and pitcher_stats_2025andcareer and hvp_stats_cache):
        return None, "Missing one or more stat caches."
    all_team_stats = defaultdict(lambda: defaultdict(list))
    for g in games:
        away = g.get('away') or g.get('away_team')
        home = g.get('home') or g.get('home_team')
        if not away or not home:
            continue
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
                for team, prefix in [(away, 'away'), (home, 'home')]:
                    all_team_stats[team]['runs'].append(sim.get(f'{prefix}_score', 0))
                    all_team_stats[team]['hits'].append(sum(v.get('H', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                    all_team_stats[team]['strikeouts'].append(sum(v.get('SO', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                    all_team_stats[team]['walks'].append(sum(v.get('BB', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
                    all_team_stats[team]['hr'].append(sum(v.get('HR', 0) for v in sim.get('hitter_stats', {}).values() if v.get('team') == team))
            except Exception as e:
                continue
    team_averages = []
    for team, stats in all_team_stats.items():
        entry = {'team': team}
        for k, v in stats.items():
            entry[k] = round(sum(v)/len(v), 2) if v else 0.0
        team_averages.append(entry)
    team_averages.sort(key=lambda x: x['runs'], reverse=True)
    return team_averages[:30], None

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    results = None
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
            results, error = batch_simulate(date, sims)
    return render_template_string(HTML_TEMPLATE, date=date, sims=sims, results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
