
from bs4 import BeautifulSoup
import json


def fetch_results():
    with open("html.html", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    expected = ["Round", "Date", "Game", "Result", "Spectators", "Venue"]
    for table_idx, table in enumerate(tables):
        rows = table.find_all("tr")
        for r in rows:
            ths = r.find_all("th")
            if ths:
                header = [th.get_text(strip=True) for th in ths]
                # Look for exact match (ignore empty columns)
                filtered_header = [h for h in header if h.strip()]
                if filtered_header == expected:
                    col_map = {name: i for i, name in enumerate(header)}
                    wanted = expected
                    start_idx = rows.index(r) + 1
                    results = []
                    for row in rows[start_idx:]:
                        cells = row.find_all("td")
                        if not cells:
                            continue
                        entry = {}
                        for col in wanted:
                            idx2 = col_map.get(col)
                            if idx2 is not None and idx2 < len(cells):
                                entry[col] = cells[idx2].get_text(strip=True)
                            else:
                                entry[col] = ""
                        results.append(entry)
                    return results
    return []

if __name__ == "__main__":
    data = fetch_results()
    import re
    import json
    if not data:
        print("No table found or no data.")
    else:
        def clean(cell):
            return ' '.join(cell.split()).strip()

        # Output schedule/results
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # --- Generate points_tables.json for all rounds ---
        def calculate_points_table(data, rounds, label):
            points = {}
            stats = {}
            teams = set()
            in_rounds = False
            for row in data:
                round_val = clean(row['Round'])
                if round_val == '1':
                    in_rounds = True
                elif round_val == str(rounds[-1]) and in_rounds:
                    in_rounds = True
                elif round_val not in tuple([''] + [str(r) for r in rounds]) and in_rounds:
                    break
                if in_rounds:
                    game = clean(row['Game'])
                    result = clean(row['Result'])
                    match = re.match(r'(.*?) - (.*)', game)
                    if not match:
                        continue
                    team1 = match.group(1).strip()
                    team2 = match.group(2).strip()
                    teams.update([team1, team2])
                    score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                    if not score_match:
                        continue
                    score1 = int(score_match.group(1))
                    score2 = int(score_match.group(2))
                    # Initialize stats
                    for t in [team1, team2]:
                        if t not in stats:
                            stats[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                    stats[team1]['GP'] += 1
                    stats[team2]['GP'] += 1
                    stats[team1]['GF'] += score1
                    stats[team1]['GA'] += score2
                    stats[team2]['GF'] += score2
                    stats[team2]['GA'] += score1
                    if score1 > score2:
                        points[team1] = points.get(team1, 0) + 2
                        points[team2] = points.get(team2, 0) + 0
                        stats[team1]['W'] += 1
                        stats[team2]['L'] += 1
                    elif score1 < score2:
                        points[team1] = points.get(team1, 0) + 0
                        points[team2] = points.get(team2, 0) + 2
                        stats[team1]['L'] += 1
                        stats[team2]['W'] += 1
                    else:
                        points[team1] = points.get(team1, 0) + 1
                        points[team2] = points.get(team2, 0) + 1
                        stats[team1]['T'] += 1
                        stats[team2]['T'] += 1
            # Prepare table for JSON output
            sorted_pts = sorted(points.items(), key=lambda x: (x[1], stats[x[0]]['GF'] - stats[x[0]]['GA']), reverse=True)
            table = {
                "title": f"Points Table After {label}",
                "rows": []
            }
            for team, pts in sorted_pts:
                s = stats[team]
                diff = s['GF'] - s['GA']
                gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
                table["rows"].append({
                    "Team": team,
                    "GP": s['GP'],
                    "W": s['W'],
                    "T": s['T'],
                    "L": s['L'],
                    "GFGA": gfga,
                    "Points": pts
                })
            return table

        # Generate all points tables for rounds 1-14
        all_tables = []
        for i in range(1, 15):
            rounds = list(range(1, i+1))
            label = f"Round {i}"
            table = calculate_points_table(data, rounds, label)
            all_tables.append(table)

        # Write points_tables.json
        with open("points_tables.json", "w", encoding="utf-8") as f:
            json.dump(all_tables, f, ensure_ascii=False, indent=2)
