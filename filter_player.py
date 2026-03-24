# Filter output.txt for a specific player and team
import re

player_name = "10.\n            Lindqvist,\n            Johan"
team_name = "HÃ\n                            R"

with open("output.txt", encoding="utf-8") as f:
    lines = f.readlines()

pattern = re.compile(rf"Player: {player_name} \| Team: {team_name} \| Goals: \d+")

for line in lines:
    if pattern.search(line):
        print(line.strip())
