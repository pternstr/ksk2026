

# SHLApp Hockey Stats Workflow

## Workflow

1. **Scrape and process game data**
	```
	python3 scan_goals.py
	```
2. **Generate summary tables**
	```
	python3 summarize_players.py
	```
3. **(Optional) Process penalties**
	```
	python3 scan_pen.py
	python3 summarize_penalties.py
	```
4. **View results**
	- Start a local web server:
	  ```
	  python3 -m http.server 8000
	  ```
	- Open [http://localhost:8000/output.html](http://localhost:8000/output.html) in your browser.

## Files to keep in the repo

- All `.py` scripts (including: scan_goals.py, summarize_players.py, scan_pen.py, summarize_penalties.py, scrape.py, filter_player.py)
- All `.html` files (output.html, results.html, html.html, example_goal.html)
- All `.json` and `.txt` data files (output.txt, penalties.txt, penalty_minutes_summary.txt, results.txt, results.json, points_tables.json)
- `readme.md`

*Do NOT include `__pycache__/` or other temporary files.*

## File Descriptions

- `scan_goals.py`: Scrapes and processes per-game hockey stats, outputs to `output.txt`.
- `summarize_players.py`: Aggregates player stats and appends summary tables to `output.txt`.
- `scan_pen.py`: Scans for penalty events in games.
- `summarize_penalties.py`: Summarizes penalty minutes per player.
- `scrape.py`: Utility for extracting results from `html.html` (not part of main workflow).
- `output.txt`: Contains all per-game tables and summary tables in plain text.
- `output.html`: Renders the summary and per-game tables for browser viewing.
- `results.html`: Main dashboard for additional results and navigation.

## Notes

- The summary table is titled "Poängliga U14P" and appears at the top of the HTML output, followed by the KÅL-only summary, then all per-game tables.
- Per-game tables are rendered as preformatted text to match the layout of `output.txt`.

## Open in browser
https://pternstr.github.io/ksk2026/results.html