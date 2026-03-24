# --- Script to find all players with '2 min' penalties in 10829* games ---
import re
import requests
from bs4 import BeautifulSoup

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


import unicodedata
def normalize_name(name):
    # Lowercase, strip, remove accents, collapse spaces
    name = name.strip().lower()
    name = ''.join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
    name = re.sub(r'\s+', ' ', name)
    return name

def build_game_player_team_map():
    game_url = None
    game_player_team = {}
    import re as _re
    pat_source = _re.compile(r"^Source: (https://stats\\.swehockey\\.se/Game/Events/\\d+)")
    pat_player = _re.compile(r"^(\d+\. [^,]+, [^\s]+)\s+([A-ZÄÖÅa-zäöå]{2,4})\s+")
    with open("output.txt", encoding="utf-8") as f:
        for line in f:
            m_source = pat_source.match(line)
            if m_source:
                game_url = m_source.group(1)
            else:
                m_player = pat_player.match(line)
                if m_player and game_url:
                    name = normalize_name(m_player.group(1))
                    team = m_player.group(2).strip()
                    game_player_team[(game_url, name)] = team
    return game_player_team

def find_2min_penalties(game_html, url, game_player_team):
    soup = BeautifulSoup(game_html, "html.parser")
    found = []
    keywords = ["2 min", "5 min"]
    for table in soup.find_all("table", class_="tblContent"):
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                desc = tds[1].get_text(strip=True)
                if any(word in desc.lower() for word in keywords):
                    name = ' '.join(tds[3].stripped_strings)
                    name = re.sub(r'\s+', ' ', name).strip()
                    norm_name = normalize_name(name)
                    team = game_player_team.get((url, norm_name), "?")
                    if team == "?":
                        print(f"[DEBUG] Team not found for: url={url}, name='{name}', norm_name='{norm_name}'")
                    found.append((desc, name, team))
    return found


output_lines = []
game_player_team = build_game_player_team_map()
for url in urls:
    print(f"Scanning {url}")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        penalties = find_2min_penalties(resp.text, url, game_player_team)
        for desc, name, team in penalties:
            line = f"{desc}: {name} [{team}] ({url})"
            print(line)
            output_lines.append(line)
    except Exception as e:
        err = f"Error fetching {url}: {e}"
        print(err)
        output_lines.append(err)

with open("penalties.txt", "w", encoding="utf-8") as f:
    for line in output_lines:
        f.write(line + "\n")
