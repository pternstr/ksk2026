import re
from collections import defaultdict

summary = defaultdict(lambda: {'G': 0, 'A': 0, 'team': None})

with open("output.txt", encoding="utf-8") as f:
    for line in f:
        # Each table line: Player, Team(s), Goal, Assist, Points, Goals/Assists
        m = re.match(r"^(.*?)\s{2,}(.*?)\s{2,}(\d+)\s{2,}(\d+)\s{2,}(\d+)\s{2,}(.*)$", line)
        if m:
            player = m.group(1).strip()
            team = m.group(2).strip()
            # Count G and A from the Goals/Assists column
            ga_col = m.group(6)
            g_count = ga_col.count('(G)')
            a_count = ga_col.count('(A)')
            summary[player]['G'] += g_count
            summary[player]['A'] += a_count
            if not summary[player]['team']:
                summary[player]['team'] = team

# Write summary table
with open("output.txt", "a", encoding="utf-8") as f:
    # Full summary
    f.write("\nSUMMARY: Total Goals (G), Assists (A), and Points per player\n")
    f.write("{:<30} {:<8} {:<6} {:<6} {:<6}\n".format("Player", "Team", "G", "A", "Points"))
    f.write("-"*60 + "\n")
    for player, stats in sorted(summary.items(), key=lambda x: (-(x[1]['G']+x[1]['A']), -x[1]['G'], x[0])):
        points = stats['G'] + stats['A']
        f.write("{:<30} {:<8} {:<6} {:<6} {:<6}\n".format(player, stats['team'] or '', stats['G'], stats['A'], points))

    # KÅL-only summary
    f.write("\nSUMMARY: Total Goals (G), Assists (A), and Points per player (KÅL only)\n")
    f.write("{:<30} {:<8} {:<6} {:<6} {:<6}\n".format("Player", "Team", "G", "A", "Points"))
    f.write("-"*60 + "\n")
    for player, stats in sorted(
        ((p, s) for p, s in summary.items() if (s['team'] or '').upper() == 'KÅL'),
        key=lambda x: (-(x[1]['G']+x[1]['A']), -x[1]['G'], x[0])
    ):
        points = stats['G'] + stats['A']
        f.write("{:<30} {:<8} {:<6} {:<6} {:<6}\n".format(player, stats['team'] or '', stats['G'], stats['A'], points))
