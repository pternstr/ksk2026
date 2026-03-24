import re
from collections import defaultdict

# File to read
PENALTIES_FILE = "penalties.txt"

# Output file for summary table
SUMMARY_FILE = "penalty_minutes_summary.txt"


def extract_penalty_minutes(line, penalty_type="2 min"):
    # Match lines like: 2 min: 11. Gäärd, Viggo Tripping (30:16 - 32:16) (...)
    match = re.match(rf"{penalty_type}: (?:\\d+\\. )?([^,]+, [^ ]+) ", line)
    if not match:
        return None, 0
    name = match.group(1).strip()
    minutes = int(penalty_type.split()[0])
    return name, minutes



def summarize_penalties(penalty_type, file_handle):
    player_minutes = defaultdict(int)
    with open(PENALTIES_FILE, encoding="utf-8") as f:
        for line in f:
            name, minutes = extract_penalty_minutes(line, penalty_type)
            if name:
                player_minutes[name] += minutes
    summary = sorted(player_minutes.items(), key=lambda x: (-x[1], x[0]))
    if summary:
        file_handle.write(f"{penalty_type} penalties\n")
        file_handle.write(f"{'Player':40} Total Minutes\n")
        file_handle.write("-"*55 + "\n")
        for name, minutes in summary:
            file_handle.write(f"{name:40} {minutes}\n")
        file_handle.write("\n")

def main():
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        summarize_penalties("2 min", f)
        summarize_penalties("5 min", f)
    print(f"Summary written to {SUMMARY_FILE}")

if __name__ == "__main__":
    main()
