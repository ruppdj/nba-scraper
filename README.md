# NBA Scraper

Scrapes NBA season totals from [Basketball Reference](https://www.basketball-reference.com/) for every season from 1980 to 2026 and saves the results to a CSV file.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the scraper:

```bash
python scraper.py
```

Output is saved to `nba_totals_1980_2026.csv`. If the file already exists, the scraper resumes from where it left off and skips completed years.

## Notes

- Requests are spaced 60 seconds apart to be respectful of Basketball Reference's servers.
- Data is sourced from the `totals_stats` table on each season's page.
