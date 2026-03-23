




# Import required libraries
import re  # For regular expressions
import requests  # For HTTP requests
from bs4 import BeautifulSoup  # For HTML parsing
import json  # For potential JSON operations (not used in this script)



# Read the local HTML file and extract all URLs containing the pattern '10829'
with open("html.html", encoding="utf-8") as f:
    html = f.read()

# Parse the HTML content
soup = BeautifulSoup(html, "html.parser")
urls = set()
# Find all anchor tags with href attributes
for a in soup.find_all("a", href=True):
    href = a['href']
    # Look for URLs matching the specific pattern for game events
    m = re.search(r"openonlinewindow\('(\/Game\/Events\/10829\d{2})", href)
    if m:
        # Construct the full URL and add to the set
        urls.add("https://stats.swehockey.se" + m.group(1))

# Sort URLs for consistent processing order
urls = sorted(urls)

print(f"Found {len(urls)} game URLs.")


# Function to extract even-strength (EQ) and power-play (PP1) goals from a game's HTML
def extract_eq_goals(game_html, source_url):
    player_data = {}
    soup = BeautifulSoup(game_html, "html.parser")
    # Find all tables containing game actions
    actions_tables = soup.find_all("table", class_="tblContent")
    for table in actions_tables:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                goal_text = tds[1].get_text(strip=True)
                # Only process rows that represent EQ or PP1 goals
                if re.match(r"\d+-\d+ \((EQ|PP1)\)", goal_text):
                    # Extract and clean up the team name
                    team_fragments = tds[2].stripped_strings
                    team = ' '.join(team_fragments)
                    team = re.sub(r'[\n\r]+', ' ', team)
                    team = re.sub(r'\s+', ' ', team).strip()
                    player_cell = tds[3]
                    players = []
                    roles = []  # 'G' for goal, 'A' for assist
                    # Main player (goal scorer): check if bold or strong tag
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
                    # Process assists (in <div> tags), check if bold (should not happen for assists)
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
                    # Store player data with cleaned names and roles
                    for p, role in zip(players, roles):
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






# Main loop: process each game URL and extract player goal/assist data
all_tables = []
for url in urls:
    print(f"Scanning {url}")
    try:
        # Download the game page
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = 'utf-8'  # Force UTF-8 encoding
        # Extract player data for EQ and PP1 goals
        player_data = extract_eq_goals(resp.text, url)

        # Prepare a formatted table of players with most points for this game
        table_lines = []
        url_line = f"Source: {url}"
        print(url_line)
        table_lines.append(url_line)
        header = "\n{:<30} {:<16} {:<6} {:<6} {:<6} {:<40}".format("Player", "Team(s)", "Goal", "Assist", "Points", "Goals/Assists")
        sep = "-"*110
        table_lines.append(header)
        table_lines.append(sep)
        # Sort players by number of events (goals+assists)
        sorted_players = sorted(player_data.items(), key=lambda x: len(x[1]), reverse=True)
        for player, events in sorted_players:
            # Combine and clean up team names
            teams_raw = ', '.join(sorted(set(g['team'] for g in events)))
            teams = re.sub(r'[\n\r]+', ' ', teams_raw)
            teams = re.sub(r'\s+', ' ', teams).strip()
            # Count goals and assists
            goal_count = sum(1 for g in events if g['role'] == 'G')
            assist_count = sum(1 for g in events if g['role'] == 'A')
            # Replace (EQ) or (PP1) with (G) or (A) in the goal text for display
            ga_list = []
            for g in events:
                label = re.sub(r' \((EQ|PP1)\)', f" ({g['role']})", g['goal'])
                ga_list.append(label)
            ga_str = ', '.join(ga_list)
            # Format the output line for this player
            line = "{:<30} {:<16} {:<6} {:<6} {:<6} {:<40}".format(player, teams, goal_count, assist_count, len(events), ga_str)
            table_lines.append(line)
            print(line)
        # Add this game's table to the overall output
        all_tables.extend(table_lines)
        all_tables.append("")  # Blank line between tables
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        # Do not write errors to all_tables/output.txt

# Write all tables to output.txt for later review
with open("output.txt", "w", encoding="utf-8") as f:
    for line in all_tables:
        f.write(line + "\n")