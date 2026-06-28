# Chromatic Cup Stats

Scrapes and analyzes tournament data from [Challonge](https://challonge.com) for the Chromatic Cup series (CC1–CC55).

## Files

- `scrape_data.py` — Fetches bracket data from Challonge and saves to `tournament_data.json`. Run once to cache the data.
- `analyze.py` — Reads `tournament_data.json` and prints stats: tournament winners, match win ratio, tournament win ratio, and points rankings.

## Usage

```bash
# Fetch data (first time only)
python3 scrape_data.py

# Analyze (re-run anytime without re-fetching)
python3 analyze.py
```

## Points Formula

| Place | Base Points |
|-------|------------|
| 1st | 100 |
| 2nd | 60 |
| 3rd | 40 |
| 4th | 25 |
| 5–8 | 15 |
| 9–16 | 8 |
| 17+ | 5 |

Scaled by `1 + log₂(players / 4)`.
