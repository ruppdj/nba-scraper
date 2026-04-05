import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

START_YEAR = 1980
END_YEAR = 2026
OUTPUT_FILE = "nba_totals_1980_2026.csv"
DELAY_SECONDS = 60  # be polite to basketball-reference

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_year(year: int) -> pd.DataFrame | None:
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR fetching {year}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "totals_stats"})
    if table is None:
        print(f"  WARNING: table not found for {year}")
        return None

    # Parse table into rows
    rows = []
    headers_row = [th.get_text() for th in table.find("thead").find_all("th")]
    # Remove the leading rank column header if present
    col_names = [h for h in headers_row if h]

    for tr in table.find("tbody").find_all("tr"):
        # Skip repeated header rows
        if tr.get("class") and "thead" in tr.get("class"):
            continue
        cells = [td.get_text() for td in tr.find_all(["td", "th"])]
        if not cells or cells[0] == "Rk":
            continue
        rows.append(cells)

    if not rows:
        print(f"  WARNING: no data rows for {year}")
        return None

    df = pd.DataFrame(rows, columns=col_names[: len(rows[0])])
    df.insert(0, "Year", year)
    return df


def load_completed_years() -> set[int]:
    if not os.path.exists(OUTPUT_FILE):
        return set()
    try:
        existing = pd.read_csv(OUTPUT_FILE, usecols=["Year"])
        completed = set(existing["Year"].unique())
        print(f"Resuming: {len(completed)} years already in {OUTPUT_FILE}, skipping them.")
        return completed
    except Exception as e:
        print(f"WARNING: could not read existing file ({e}), starting fresh.")
        return set()


def main():
    completed = load_completed_years()
    years_to_scrape = [y for y in range(START_YEAR, END_YEAR + 1) if y not in completed]

    if not years_to_scrape:
        print("All years already scraped. Nothing to do.")
        return

    total = len(years_to_scrape)
    for i, year in enumerate(years_to_scrape, 1):
        print(f"[{i}/{total}] Scraping {year}...")
        df = scrape_year(year)
        if df is not None:
            write_header = not os.path.exists(OUTPUT_FILE)
            df.to_csv(OUTPUT_FILE, mode="a", index=False, header=write_header)
            print(f"  {len(df)} rows saved.")
        if i < total:
            print(f"  Waiting {DELAY_SECONDS}s before next request...")
            time.sleep(DELAY_SECONDS)

    print(f"\nDone. Data saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
