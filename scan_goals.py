


import re
import requests
from bs4 import BeautifulSoup


# Read html.html and extract URLs only once
with open("html.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
urls = set()

url = "https://stats.swehockey.se/Game/Events/1082926"
print(f"Scanning {url}")

def extract_eq_goals(game_html, source_url):
    player_data = {}
    soup = BeautifulSoup(game_html, "html.parser")
    actions_tables = soup.find_all("table", class_="tblContent")
    for table in actions_tables:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                goal_text = tds[1].get_text(strip=True)
                if re.match(r"\d+-\d+ \(EQ\)", goal_text):
                    # Join all text fragments in the team cell, then clean up whitespace
                    team_fragments = tds[2].stripped_strings
                    team = ' '.join(team_fragments)
                    team = re.sub(r'[\n\r]+', ' ', team)
                    team = re.sub(r'\s+', ' ', team).strip()
                    player_cell = tds[3]
                    players = []
                    main_player = player_cell.contents[0]
                    if isinstance(main_player, str):
                        main_player = main_player.strip()
                        if main_player:
                            players.append(main_player)
                    for div in player_cell.find_all("div"):
                        div_text = div.get_text(strip=True)
                        if div_text:
                            players.append(div_text)
                    for p in players:
                        # Clean up player name: remove newlines and excessive whitespace
                        p_clean = re.sub(r'\s+', ' ', p).strip()
                        if p_clean not in player_data:
                            player_data[p_clean] = []
                        player_data[p_clean].append({
                            'team': team,
                            'goal': goal_text,
                            'source': source_url
                        })
    return player_data




try:
    resp = requests.get(url)
    resp.raise_for_status()
    resp.encoding = 'utf-8'  # Force UTF-8 encoding
    player_data = extract_eq_goals(resp.text, url)
    for player, goals in player_data.items():
        teams = ', '.join(g['team'] for g in goals)
        goal_texts = ', '.join(g['goal'] for g in goals)
        sources = ', '.join(g['source'] for g in goals)
        print(f"Player: {player} | Teams: {teams} | Goals: {goal_texts} | Sources: {sources}")

    # Print formatted table of players with most points
    print("\n{:<30} {:<30} {:<6} {:<40}".format("Player", "Team(s)", "Points", "Goals"))
    print("-"*120)
    sorted_players = sorted(player_data.items(), key=lambda x: len(x[1]), reverse=True)
    for player, goals in sorted_players:
        # Clean up team names to remove newlines and excessive whitespace, and ensure single-line output
        teams_raw = ', '.join(sorted(set(g['team'] for g in goals)))
        teams = re.sub(r'[\n\r]+', ' ', teams_raw)
        teams = re.sub(r'\s+', ' ', teams).strip()
        goal_list = ', '.join(g['goal'] for g in goals)
        print("{:<30} {:<30} {:<20} {:<40}".format(player, teams, len(goals), goal_list))
except Exception as e:
    print(f"Error fetching {url}: {e}")