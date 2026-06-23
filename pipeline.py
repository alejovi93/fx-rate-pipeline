import os
import requests
import pandas as pd
from datetime import date


def fetch_fx_rates(currencies: list[str], start_date: str) -> pd.DataFrame:
    """
    Fetches daily FX rates from frankfurter.dev v2 API (ECB provider).
    Returns a long-format DataFrame with columns: date, currency, rate_vs_eur.
    EUR is added as anchor row (rate = 1.0) for cross pair computation.
    """
    base     = "EUR"
    end_date = date.today().isoformat()
    quotes   = ",".join([c for c in currencies if c != base])

    url    = "https://api.frankfurter.dev/v2/rates"
    params = {
        "from":      start_date,
        "to":        end_date,
        "base":      base,
        "quotes":    quotes,
        "providers": "ECB"
    }

    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Errore API frankfurter: {e}")

    data = response.json()
    df   = pd.DataFrame(data)

    assert (df["base"] == base).all(), "Base currency not wanted"

    df = df.rename(columns={"quote": "currency", "rate": "rate_vs_eur"})
    df = df[["date", "currency", "rate_vs_eur"]]
    df["date"] = pd.to_datetime(df["date"])

    # Adding EUR to self join
    eur_rows = pd.DataFrame({
        "date":        df["date"].unique(),
        "currency":    "EUR",
        "rate_vs_eur": 1.0
    })
    df = pd.concat([df, eur_rows], ignore_index=True)
    df = df.sort_values(["currency", "date"]).reset_index(drop=True)

    return df


def compute_cross_pairs(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Generates all cross currency pairs via self-join on date.
    Rate is computed as: rate_quote_vs_eur / rate_base_vs_eur.
    For N currencies produces N*(N-1) pairs per day.
    """
    df = df_raw.merge(df_raw, on="date", suffixes=("_base", "_quote"))
    df = df[df["currency_base"] != df["currency_quote"]]

    df["rate"] = (df["rate_vs_eur_quote"] / df["rate_vs_eur_base"]).round(6)

    df = df[["date", "currency_base", "currency_quote", "rate"]] \
        .rename(columns={
            "currency_base":  "base_currency",
            "currency_quote": "quote_currency"
        }) \
        .sort_values(["base_currency", "quote_currency", "date"]) \
        .reset_index(drop=True)

    return df


def validate(df: pd.DataFrame, currencies: list[str]) -> None:
    """
    Basic sanity checks on the final DataFrame.
    """
    expected_pairs = len(currencies) * (len(currencies) - 1)
    actual_pairs   = df.groupby("date").size()
    assert (actual_pairs == expected_pairs).all(), \
        f"Wrong pairs count: expected {expected_pairs}, actual {actual_pairs.unique()}"

    date_range = pd.bdate_range(start=df["date"].min(), end=df["date"].max())
    missing    = set(date_range) - set(df["date"].unique())
    if missing:
        print(f"⚠ Missing Date (potential holidays): {sorted(missing)}")

    print("✓ OK")


# ── Main ──────────────────────────────────────────────────────────────────────

CURRENCIES = ["NOK", "EUR", "SEK", "PLN", "RON", "DKK", "CZK"]
START_DATE = f"{date.today().year}-01-01"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "fx_rates.csv")

df_raw   = fetch_fx_rates(CURRENCIES, START_DATE)
df_final = compute_cross_pairs(df_raw)

validate(df_final, CURRENCIES)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df_final.to_csv(OUTPUT_FILE, index=False)

print(f"✓ file saved: {OUTPUT_FILE}")
print(f"✓ row count:  {len(df_final)}")
print(f"✓ unique pairs:   {df_final.groupby(['base_currency', 'quote_currency']).ngroups}")
print(f"✓ dates:  {df_final['date'].nunique()}")
print(df_final.head(10))