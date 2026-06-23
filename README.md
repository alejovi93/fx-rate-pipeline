# FX Rate Pipeline

Daily foreign exchange rate pipeline for NOK, EUR, SEK, PLN, RON, DKK, CZK.
Fetches data from the ECB via frankfurter.dev and generates a CSV ready for Power BI.

## Requirements

Python 3.10+

Install dependencies:
pip install requests pandas

## How to run

python pipeline.py

The script will:
1. Fetch YTD daily rates from frankfurter.dev (ECB provider)
2. Compute all 42 cross currency pairs
3. Validate the output
4. Save the result to output/fx_rates.csv

## Output

File: output/fx_rates.csv

| Column         | Type     | Description                          |
|----------------|----------|--------------------------------------|
| date           | date     | Trading date (weekdays only)         |
| base_currency  | string   | Base currency (e.g. EUR)             |
| quote_currency | string   | Quote currency (e.g. NOK)            |
| rate           | float    | Units of quote per 1 unit of base    |

## Validate outputs

After running, the script prints:
- ✓ Number of rows generated (~5,000 for a full YTD)
- ✓ Number of unique pairs (always 42)
- ✓ Number of dates in range
- ⚠ Any missing business days (public holidays)

## Notes

- Data source: frankfurter.dev v2, filtered on ECB provider
- Historical window: YTD from January 1st of current year
- Weekend and holiday dates are not included (ECB does not publish rates)
- Re-running the script overwrites the existing CSV with fresh data