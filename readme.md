
# SHLApp Hockey Stats Workflow

## Workflow

1. **Scrape and process game data**
	 - Run the following command to extract and process all relevant hockey game data:
     
		 python3 scan_goals.py

2. **Generate summary tables**
	 - After scraping, generate the summary and KÅL-only summary tables:
     
		 python3 summarize_players.py

3. **View the results in your browser**
	 - Start a local web server in the project directory:
     
		 python3 -m http.server 8000
	 - Open your browser and go to:
     
		 http://localhost:8000/output.html

## File Descriptions

- `scan_goals.py`: Scrapes and processes per-game hockey stats, outputs to `output.txt`.
- `summarize_players.py`: Aggregates player stats and appends summary tables to `output.txt`.
- `output.txt`: Contains all per-game tables and summary tables in plain text.
- `output.html`: Renders the summary and per-game tables for browser viewing.
- `results.html`: Main dashboard for additional results and navigation.

## Notes

- The summary table is titled "Poängliga U14P" and appears at the top of the HTML output, followed by the KÅL-only summary, then all per-game tables.
- Per-game tables are rendered as preformatted text to match the layout of `output.txt`.

## Open in browser
https://pternstr.github.io/ksk2026/results.html