
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
    if not data:
        print("No table found or no data.")
    else:
        # Print as table with improved readability
        print(f"{'Round':<6} {'Date':<20} {'Game':<40} {'Result':<8} {'Spectators':<10} {'Venue':<20}")
        def clean(cell):
            return ' '.join(cell.split()).strip()
        for row in data:
            print(f"{clean(row['Round']):<6} {clean(row['Date']):<20} {clean(row['Game']):<40} {clean(row['Result']):<8} {clean(row['Spectators']):<10} {clean(row['Venue']):<20}")

        # Calculate points table for round 1 only (with stats)
        import re
        points_r1 = {}
        stats_r1 = {}
        teams_r1 = set()
        in_round_1 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_round_1 = True
            elif round_val != '' and in_round_1:
                break
            if in_round_1:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r1.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r1:
                        stats_r1[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r1[team1]['GP'] += 1
                stats_r1[team2]['GP'] += 1
                stats_r1[team1]['GF'] += score1
                stats_r1[team1]['GA'] += score2
                stats_r1[team2]['GF'] += score2
                stats_r1[team2]['GA'] += score1
                if score1 > score2:
                    points_r1[team1] = points_r1.get(team1, 0) + 2
                    points_r1[team2] = points_r1.get(team2, 0) + 0
                    stats_r1[team1]['W'] += 1
                    stats_r1[team2]['L'] += 1
                elif score1 < score2:
                    points_r1[team1] = points_r1.get(team1, 0) + 0
                    points_r1[team2] = points_r1.get(team2, 0) + 2
                    stats_r1[team1]['L'] += 1
                    stats_r1[team2]['W'] += 1
                else:
                    points_r1[team1] = points_r1.get(team1, 0) + 1
                    points_r1[team2] = points_r1.get(team2, 0) + 1
                    stats_r1[team1]['T'] += 1
                    stats_r1[team2]['T'] += 1

        print("\nPoints Table After Round 1:")
        # Sort by points, then goal diff
        sorted_r1 = sorted(points_r1.items(), key=lambda x: (x[1], stats_r1[x[0]]['GF'] - stats_r1[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r1:
            s = stats_r1[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1 and 2 (with stats)
        points_r2 = {}
        stats_r2 = {}
        teams_r2 = set()
        in_rounds_1_2 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_2 = True
            elif round_val == '2' and in_rounds_1_2:
                in_rounds_1_2 = True
            elif round_val not in ('', '1', '2') and in_rounds_1_2:
                break
            if in_rounds_1_2:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r2.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r2:
                        stats_r2[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r2[team1]['GP'] += 1
                stats_r2[team2]['GP'] += 1
                stats_r2[team1]['GF'] += score1
                stats_r2[team1]['GA'] += score2
                stats_r2[team2]['GF'] += score2
                stats_r2[team2]['GA'] += score1
                if score1 > score2:
                    points_r2[team1] = points_r2.get(team1, 0) + 2
                    points_r2[team2] = points_r2.get(team2, 0) + 0
                    stats_r2[team1]['W'] += 1
                    stats_r2[team2]['L'] += 1
                elif score1 < score2:
                    points_r2[team1] = points_r2.get(team1, 0) + 0
                    points_r2[team2] = points_r2.get(team2, 0) + 2
                    stats_r2[team1]['L'] += 1
                    stats_r2[team2]['W'] += 1
                else:
                    points_r2[team1] = points_r2.get(team1, 0) + 1
                    points_r2[team2] = points_r2.get(team2, 0) + 1
                    stats_r2[team1]['T'] += 1
                    stats_r2[team2]['T'] += 1

        print("\nPoints Table After Round 2:")
        sorted_r2 = sorted(points_r2.items(), key=lambda x: (x[1], stats_r2[x[0]]['GF'] - stats_r2[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r2:
            s = stats_r2[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-3 (with stats)
        points_r3 = {}
        stats_r3 = {}
        teams_r3 = set()
        in_rounds_1_3 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_3 = True
            elif round_val == '3' and in_rounds_1_3:
                in_rounds_1_3 = True
            elif round_val not in ('', '1', '2', '3') and in_rounds_1_3:
                break
            if in_rounds_1_3:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r3.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r3:
                        stats_r3[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r3[team1]['GP'] += 1
                stats_r3[team2]['GP'] += 1
                stats_r3[team1]['GF'] += score1
                stats_r3[team1]['GA'] += score2
                stats_r3[team2]['GF'] += score2
                stats_r3[team2]['GA'] += score1
                if score1 > score2:
                    points_r3[team1] = points_r3.get(team1, 0) + 2
                    points_r3[team2] = points_r3.get(team2, 0) + 0
                    stats_r3[team1]['W'] += 1
                    stats_r3[team2]['L'] += 1
                elif score1 < score2:
                    points_r3[team1] = points_r3.get(team1, 0) + 0
                    points_r3[team2] = points_r3.get(team2, 0) + 2
                    stats_r3[team1]['L'] += 1
                    stats_r3[team2]['W'] += 1
                else:
                    points_r3[team1] = points_r3.get(team1, 0) + 1
                    points_r3[team2] = points_r3.get(team2, 0) + 1
                    stats_r3[team1]['T'] += 1
                    stats_r3[team2]['T'] += 1

        print("\nPoints Table After Round 3:")
        sorted_r3 = sorted(points_r3.items(), key=lambda x: (x[1], stats_r3[x[0]]['GF'] - stats_r3[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r3:
            s = stats_r3[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-4 (with stats)
        points_r4 = {}
        stats_r4 = {}
        teams_r4 = set()
        in_rounds_1_4 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_4 = True
            elif round_val == '4' and in_rounds_1_4:
                in_rounds_1_4 = True
            elif round_val not in ('', '1', '2', '3', '4') and in_rounds_1_4:
                break
            if in_rounds_1_4:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r4.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r4:
                        stats_r4[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r4[team1]['GP'] += 1
                stats_r4[team2]['GP'] += 1
                stats_r4[team1]['GF'] += score1
                stats_r4[team1]['GA'] += score2
                stats_r4[team2]['GF'] += score2
                stats_r4[team2]['GA'] += score1
                if score1 > score2:
                    points_r4[team1] = points_r4.get(team1, 0) + 2
                    points_r4[team2] = points_r4.get(team2, 0) + 0
                    stats_r4[team1]['W'] += 1
                    stats_r4[team2]['L'] += 1
                elif score1 < score2:
                    points_r4[team1] = points_r4.get(team1, 0) + 0
                    points_r4[team2] = points_r4.get(team2, 0) + 2
                    stats_r4[team1]['L'] += 1
                    stats_r4[team2]['W'] += 1
                else:
                    points_r4[team1] = points_r4.get(team1, 0) + 1
                    points_r4[team2] = points_r4.get(team2, 0) + 1
                    stats_r4[team1]['T'] += 1
                    stats_r4[team2]['T'] += 1

        print("\nPoints Table After Round 4:")
        sorted_r4 = sorted(points_r4.items(), key=lambda x: (x[1], stats_r4[x[0]]['GF'] - stats_r4[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r4:
            s = stats_r4[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-5 (with stats)
        points_r5 = {}
        stats_r5 = {}
        teams_r5 = set()
        in_rounds_1_5 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_5 = True
            elif round_val == '5' and in_rounds_1_5:
                in_rounds_1_5 = True
            elif round_val not in ('', '1', '2', '3', '4', '5') and in_rounds_1_5:
                break
            if in_rounds_1_5:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r5.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r5:
                        stats_r5[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r5[team1]['GP'] += 1
                stats_r5[team2]['GP'] += 1
                stats_r5[team1]['GF'] += score1
                stats_r5[team1]['GA'] += score2
                stats_r5[team2]['GF'] += score2
                stats_r5[team2]['GA'] += score1
                if score1 > score2:
                    points_r5[team1] = points_r5.get(team1, 0) + 2
                    points_r5[team2] = points_r5.get(team2, 0) + 0
                    stats_r5[team1]['W'] += 1
                    stats_r5[team2]['L'] += 1
                elif score1 < score2:
                    points_r5[team1] = points_r5.get(team1, 0) + 0
                    points_r5[team2] = points_r5.get(team2, 0) + 2
                    stats_r5[team1]['L'] += 1
                    stats_r5[team2]['W'] += 1
                else:
                    points_r5[team1] = points_r5.get(team1, 0) + 1
                    points_r5[team2] = points_r5.get(team2, 0) + 1
                    stats_r5[team1]['T'] += 1
                    stats_r5[team2]['T'] += 1

        print("\nPoints Table After Round 5:")
        sorted_r5 = sorted(points_r5.items(), key=lambda x: (x[1], stats_r5[x[0]]['GF'] - stats_r5[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r5:
            s = stats_r5[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-6 (with stats)
        points_r6 = {}
        stats_r6 = {}
        teams_r6 = set()
        in_rounds_1_6 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_6 = True
            elif round_val == '6' and in_rounds_1_6:
                in_rounds_1_6 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6') and in_rounds_1_6:
                break
            if in_rounds_1_6:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r6.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r6:
                        stats_r6[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r6[team1]['GP'] += 1
                stats_r6[team2]['GP'] += 1
                stats_r6[team1]['GF'] += score1
                stats_r6[team1]['GA'] += score2
                stats_r6[team2]['GF'] += score2
                stats_r6[team2]['GA'] += score1
                if score1 > score2:
                    points_r6[team1] = points_r6.get(team1, 0) + 2
                    points_r6[team2] = points_r6.get(team2, 0) + 0
                    stats_r6[team1]['W'] += 1
                    stats_r6[team2]['L'] += 1
                elif score1 < score2:
                    points_r6[team1] = points_r6.get(team1, 0) + 0
                    points_r6[team2] = points_r6.get(team2, 0) + 2
                    stats_r6[team1]['L'] += 1
                    stats_r6[team2]['W'] += 1
                else:
                    points_r6[team1] = points_r6.get(team1, 0) + 1
                    points_r6[team2] = points_r6.get(team2, 0) + 1
                    stats_r6[team1]['T'] += 1
                    stats_r6[team2]['T'] += 1

        print("\nPoints Table After Round 6:")
        sorted_r6 = sorted(points_r6.items(), key=lambda x: (x[1], stats_r6[x[0]]['GF'] - stats_r6[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r6:
            s = stats_r6[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-7 (with stats)
        points_r7 = {}
        stats_r7 = {}
        teams_r7 = set()
        in_rounds_1_7 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_7 = True
            elif round_val == '7' and in_rounds_1_7:
                in_rounds_1_7 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7') and in_rounds_1_7:
                break
            if in_rounds_1_7:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r7.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r7:
                        stats_r7[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r7[team1]['GP'] += 1
                stats_r7[team2]['GP'] += 1
                stats_r7[team1]['GF'] += score1
                stats_r7[team1]['GA'] += score2
                stats_r7[team2]['GF'] += score2
                stats_r7[team2]['GA'] += score1
                if score1 > score2:
                    points_r7[team1] = points_r7.get(team1, 0) + 2
                    points_r7[team2] = points_r7.get(team2, 0) + 0
                    stats_r7[team1]['W'] += 1
                    stats_r7[team2]['L'] += 1
                elif score1 < score2:
                    points_r7[team1] = points_r7.get(team1, 0) + 0
                    points_r7[team2] = points_r7.get(team2, 0) + 2
                    stats_r7[team1]['L'] += 1
                    stats_r7[team2]['W'] += 1
                else:
                    points_r7[team1] = points_r7.get(team1, 0) + 1
                    points_r7[team2] = points_r7.get(team2, 0) + 1
                    stats_r7[team1]['T'] += 1
                    stats_r7[team2]['T'] += 1

        print("\nPoints Table After Round 7:")
        sorted_r7 = sorted(points_r7.items(), key=lambda x: (x[1], stats_r7[x[0]]['GF'] - stats_r7[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r7:
            s = stats_r7[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-8 (with stats)
        points_r8 = {}
        stats_r8 = {}
        teams_r8 = set()
        in_rounds_1_8 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_8 = True
            elif round_val == '8' and in_rounds_1_8:
                in_rounds_1_8 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7', '8') and in_rounds_1_8:
                break
            if in_rounds_1_8:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r8.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r8:
                        stats_r8[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r8[team1]['GP'] += 1
                stats_r8[team2]['GP'] += 1
                stats_r8[team1]['GF'] += score1
                stats_r8[team1]['GA'] += score2
                stats_r8[team2]['GF'] += score2
                stats_r8[team2]['GA'] += score1
                if score1 > score2:
                    points_r8[team1] = points_r8.get(team1, 0) + 2
                    points_r8[team2] = points_r8.get(team2, 0) + 0
                    stats_r8[team1]['W'] += 1
                    stats_r8[team2]['L'] += 1
                elif score1 < score2:
                    points_r8[team1] = points_r8.get(team1, 0) + 0
                    points_r8[team2] = points_r8.get(team2, 0) + 2
                    stats_r8[team1]['L'] += 1
                    stats_r8[team2]['W'] += 1
                else:
                    points_r8[team1] = points_r8.get(team1, 0) + 1
                    points_r8[team2] = points_r8.get(team2, 0) + 1
                    stats_r8[team1]['T'] += 1
                    stats_r8[team2]['T'] += 1

        print("\nPoints Table After Round 8:")
        sorted_r8 = sorted(points_r8.items(), key=lambda x: (x[1], stats_r8[x[0]]['GF'] - stats_r8[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r8:
            s = stats_r8[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-9 (with stats)
        points_r9 = {}
        stats_r9 = {}
        teams_r9 = set()
        in_rounds_1_9 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_9 = True
            elif round_val == '9' and in_rounds_1_9:
                in_rounds_1_9 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7', '8', '9') and in_rounds_1_9:
                break
            if in_rounds_1_9:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r9.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r9:
                        stats_r9[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r9[team1]['GP'] += 1
                stats_r9[team2]['GP'] += 1
                stats_r9[team1]['GF'] += score1
                stats_r9[team1]['GA'] += score2
                stats_r9[team2]['GF'] += score2
                stats_r9[team2]['GA'] += score1
                if score1 > score2:
                    points_r9[team1] = points_r9.get(team1, 0) + 2
                    points_r9[team2] = points_r9.get(team2, 0) + 0
                    stats_r9[team1]['W'] += 1
                    stats_r9[team2]['L'] += 1
                elif score1 < score2:
                    points_r9[team1] = points_r9.get(team1, 0) + 0
                    points_r9[team2] = points_r9.get(team2, 0) + 2
                    stats_r9[team1]['L'] += 1
                    stats_r9[team2]['W'] += 1
                else:
                    points_r9[team1] = points_r9.get(team1, 0) + 1
                    points_r9[team2] = points_r9.get(team2, 0) + 1
                    stats_r9[team1]['T'] += 1
                    stats_r9[team2]['T'] += 1

        print("\nPoints Table After Round 9:")
        sorted_r9 = sorted(points_r9.items(), key=lambda x: (x[1], stats_r9[x[0]]['GF'] - stats_r9[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r9:
            s = stats_r9[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-10 (with stats)
        points_r10 = {}
        stats_r10 = {}
        teams_r10 = set()
        in_rounds_1_10 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_10 = True
            elif round_val == '10' and in_rounds_1_10:
                in_rounds_1_10 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10') and in_rounds_1_10:
                break
            if in_rounds_1_10:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r10.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r10:
                        stats_r10[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r10[team1]['GP'] += 1
                stats_r10[team2]['GP'] += 1
                stats_r10[team1]['GF'] += score1
                stats_r10[team1]['GA'] += score2
                stats_r10[team2]['GF'] += score2
                stats_r10[team2]['GA'] += score1
                if score1 > score2:
                    points_r10[team1] = points_r10.get(team1, 0) + 2
                    points_r10[team2] = points_r10.get(team2, 0) + 0
                    stats_r10[team1]['W'] += 1
                    stats_r10[team2]['L'] += 1
                elif score1 < score2:
                    points_r10[team1] = points_r10.get(team1, 0) + 0
                    points_r10[team2] = points_r10.get(team2, 0) + 2
                    stats_r10[team1]['L'] += 1
                    stats_r10[team2]['W'] += 1
                else:
                    points_r10[team1] = points_r10.get(team1, 0) + 1
                    points_r10[team2] = points_r10.get(team2, 0) + 1
                    stats_r10[team1]['T'] += 1
                    stats_r10[team2]['T'] += 1

        print("\nPoints Table After Round 10:")
        sorted_r10 = sorted(points_r10.items(), key=lambda x: (x[1], stats_r10[x[0]]['GF'] - stats_r10[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r10:
            s = stats_r10[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-11 (with stats)
        points_r11 = {}
        stats_r11 = {}
        teams_r11 = set()
        in_rounds_1_11 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_11 = True
            elif round_val == '11' and in_rounds_1_11:
                in_rounds_1_11 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11') and in_rounds_1_11:
                break
            if in_rounds_1_11:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r11.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r11:
                        stats_r11[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r11[team1]['GP'] += 1
                stats_r11[team2]['GP'] += 1
                stats_r11[team1]['GF'] += score1
                stats_r11[team1]['GA'] += score2
                stats_r11[team2]['GF'] += score2
                stats_r11[team2]['GA'] += score1
                if score1 > score2:
                    points_r11[team1] = points_r11.get(team1, 0) + 2
                    points_r11[team2] = points_r11.get(team2, 0) + 0
                    stats_r11[team1]['W'] += 1
                    stats_r11[team2]['L'] += 1
                elif score1 < score2:
                    points_r11[team1] = points_r11.get(team1, 0) + 0
                    points_r11[team2] = points_r11.get(team2, 0) + 2
                    stats_r11[team1]['L'] += 1
                    stats_r11[team2]['W'] += 1
                else:
                    points_r11[team1] = points_r11.get(team1, 0) + 1
                    points_r11[team2] = points_r11.get(team2, 0) + 1
                    stats_r11[team1]['T'] += 1
                    stats_r11[team2]['T'] += 1

        print("\nPoints Table After Round 11:")
        sorted_r11 = sorted(points_r11.items(), key=lambda x: (x[1], stats_r11[x[0]]['GF'] - stats_r11[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r11:
            s = stats_r11[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-12 (with stats)
        points_r12 = {}
        stats_r12 = {}
        teams_r12 = set()
        in_rounds_1_12 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_12 = True
            elif round_val == '12' and in_rounds_1_12:
                in_rounds_1_12 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12') and in_rounds_1_12:
                break
            if in_rounds_1_12:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r12.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r12:
                        stats_r12[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r12[team1]['GP'] += 1
                stats_r12[team2]['GP'] += 1
                stats_r12[team1]['GF'] += score1
                stats_r12[team1]['GA'] += score2
                stats_r12[team2]['GF'] += score2
                stats_r12[team2]['GA'] += score1
                if score1 > score2:
                    points_r12[team1] = points_r12.get(team1, 0) + 2
                    points_r12[team2] = points_r12.get(team2, 0) + 0
                    stats_r12[team1]['W'] += 1
                    stats_r12[team2]['L'] += 1
                elif score1 < score2:
                    points_r12[team1] = points_r12.get(team1, 0) + 0
                    points_r12[team2] = points_r12.get(team2, 0) + 2
                    stats_r12[team1]['L'] += 1
                    stats_r12[team2]['W'] += 1
                else:
                    points_r12[team1] = points_r12.get(team1, 0) + 1
                    points_r12[team2] = points_r12.get(team2, 0) + 1
                    stats_r12[team1]['T'] += 1
                    stats_r12[team2]['T'] += 1

        print("\nPoints Table After Round 12:")
        sorted_r12 = sorted(points_r12.items(), key=lambda x: (x[1], stats_r12[x[0]]['GF'] - stats_r12[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r12:
            s = stats_r12[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table for rounds 1-13 (with stats)
        points_r13 = {}
        stats_r13 = {}
        teams_r13 = set()
        in_rounds_1_13 = False
        for row in data:
            round_val = clean(row['Round'])
            if round_val == '1':
                in_rounds_1_13 = True
            elif round_val == '13' and in_rounds_1_13:
                in_rounds_1_13 = True
            elif round_val not in ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13') and in_rounds_1_13:
                break
            if in_rounds_1_13:
                game = clean(row['Game'])
                result = clean(row['Result'])
                match = re.match(r'(.*?) - (.*)', game)
                if not match:
                    continue
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                teams_r13.update([team1, team2])
                score_match = re.match(r'(\d+)\s*-\s*(\d+)', result)
                if not score_match:
                    continue
                score1 = int(score_match.group(1))
                score2 = int(score_match.group(2))
                # Initialize stats
                for t in [team1, team2]:
                    if t not in stats_r13:
                        stats_r13[t] = {'GP': 0, 'W': 0, 'T': 0, 'L': 0, 'GF': 0, 'GA': 0}
                stats_r13[team1]['GP'] += 1
                stats_r13[team2]['GP'] += 1
                stats_r13[team1]['GF'] += score1
                stats_r13[team1]['GA'] += score2
                stats_r13[team2]['GF'] += score2
                stats_r13[team2]['GA'] += score1
                if score1 > score2:
                    points_r13[team1] = points_r13.get(team1, 0) + 2
                    points_r13[team2] = points_r13.get(team2, 0) + 0
                    stats_r13[team1]['W'] += 1
                    stats_r13[team2]['L'] += 1
                elif score1 < score2:
                    points_r13[team1] = points_r13.get(team1, 0) + 0
                    points_r13[team2] = points_r13.get(team2, 0) + 2
                    stats_r13[team1]['L'] += 1
                    stats_r13[team2]['W'] += 1
                else:
                    points_r13[team1] = points_r13.get(team1, 0) + 1
                    points_r13[team2] = points_r13.get(team2, 0) + 1
                    stats_r13[team1]['T'] += 1
                    stats_r13[team2]['T'] += 1

        print("\nPoints Table After Round 13:")
        sorted_r13 = sorted(points_r13.items(), key=lambda x: (x[1], stats_r13[x[0]]['GF'] - stats_r13[x[0]]['GA']), reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_r13:
            s = stats_r13[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")

        # Calculate points table with stats
        points = {}
        teams = set()
        stats = {}
        for row in data:
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

        # Print points table with stats
        print("\nPoints Table:")
        sorted_teams = sorted(points.items(), key=lambda x: x[1], reverse=True)
        print(f"{'Team':<25} {'GP':<4} {'W':<4} {'T':<4} {'L':<4} {'GF:GA (diff)':<14} {'Points':<6}")
        for team, pts in sorted_teams:
            s = stats[team]
            diff = s['GF'] - s['GA']
            gfga = f"{s['GF']}:{s['GA']} ({diff:+d})"
            print(f"{team:<25} {s['GP']:<4} {s['W']:<4} {s['T']:<4} {s['L']:<4} {gfga:<14} {pts:<6}")