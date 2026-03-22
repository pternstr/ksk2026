



import re
import requests
from bs4 import BeautifulSoup
import json
from game_info_helper import get_game_info


# Read html.html and extract all URLs containing 10829
with open("html.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
urls = set()
for a in soup.find_all("a", href=True):
    href = a['href']
    m = re.search(r"openonlinewindow\('(\/Game\/Events\/10829\d{2})", href)
    if m:
        urls.add("https://stats.swehockey.se" + m.group(1))

urls = sorted(urls)

print(f"Found {len(urls)} game URLs.")

def extract_eq_goals(game_html, source_url):
    player_data = {}
    soup = BeautifulSoup(game_html, "html.parser")
    actions_tables = soup.find_all("table", class_="tblContent")
    for table in actions_tables:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                goal_text = tds[1].get_text(strip=True)
                if re.match(r"\d+-\d+ \((EQ|PP1)\)", goal_text):
                    # Join all text fragments in the team cell, then clean up whitespace
                    team_fragments = tds[2].stripped_strings
                    team = ' '.join(team_fragments)
                    team = re.sub(r'[\n\r]+', ' ', team)
                    team = re.sub(r'\s+', ' ', team).strip()
                    player_cell = tds[3]
                    players = []
                    roles = []  # 'G' for goal, 'A' for assist
                    # Main player (goal scorer): check if bold
                    main = player_cell.contents[0]
                    if hasattr(main, 'name') and main.name in ['b', 'strong']:
                        main_player = main.get_text(strip=True)
                        players.append(main_player)
                        roles.append('G')
                    elif isinstance(main, str):
                        main_player = main.strip()
                        if main_player:
                            players.append(main_player)
                            roles.append('G')
                    # Assists (in <div>), check if bold
                    for div in player_cell.find_all("div"):
                        if div.find(['b', 'strong']):
                            assist_name = div.get_text(strip=True)
                            players.append(assist_name)
                            roles.append('G')  # Defensive: treat as goal if bold (should not happen for assists)
                        else:
                            assist_name = div.get_text(strip=True)
                            if assist_name:
                                players.append(assist_name)
                                roles.append('A')
                    for p, role in zip(players, roles):
                        # Clean up player name: remove newlines and excessive whitespace
                        p_clean = re.sub(r'\s+', ' ', p).strip()
                        if p_clean not in player_data:
                            player_data[p_clean] = []
                        player_data[p_clean].append({
                            'team': team,
                            'role': role,
                            'goal': goal_text,
                            'source': source_url
                        })
    return player_data





all_tables = []
for url in urls:
    print(f"Scanning {url}")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = 'utf-8'  # Force UTF-8 encoding
        player_data = extract_eq_goals(resp.text, url)

        # Print formatted table of players with most points
        table_lines = []
        url_line = f"Source: {url}"
        print(url_line)
        table_lines.append(url_line)
        header = "\n{:<30} {:<16} {:<6} {:<6} {:<6} {:<40}".format("Player", "Team(s)", "Goal", "Assist", "Points", "Goals/Assists")
        sep = "-"*110
        table_lines.append(header)
        table_lines.append(sep)
        sorted_players = sorted(player_data.items(), key=lambda x: len(x[1]), reverse=True)
        for player, events in sorted_players:
            teams_raw = ', '.join(sorted(set(g['team'] for g in events)))
            teams = re.sub(r'[\n\r]+', ' ', teams_raw)
            teams = re.sub(r'\s+', ' ', teams).strip()
            # Count goals and assists
            goal_count = sum(1 for g in events if g['role'] == 'G')
            assist_count = sum(1 for g in events if g['role'] == 'A')
            # Replace (EQ) or (PP1) with (G) or (A) in the goal text
            ga_list = []
            for g in events:
                label = re.sub(r' \((EQ|PP1)\)', f" ({g['role']})", g['goal'])
                ga_list.append(label)
            ga_str = ', '.join(ga_list)
            line = "{:<30} {:<16} {:<6} {:<6} {:<6} {:<40}".format(player, teams, goal_count, assist_count, len(events), ga_str)
            table_lines.append(line)
            print(line)
        all_tables.extend(table_lines)
        all_tables.append("")  # Blank line between tables
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        all_tables.append(f"Error fetching {url}: {e}")
        all_tables.append("")

# Write all tables to output.txt
with open("output.txt", "w", encoding="utf-8") as f:
    for line in all_tables:
        f.write(line + "\n")