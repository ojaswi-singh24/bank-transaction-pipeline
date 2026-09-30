"""
extract_load.py

Purpose: Read the raw transactions CSV and load it into a DuckDB database,
as an UNTOUCHED raw table. No cleaning happens here on purpose -- that's
dbt's job later. This script's only responsibility is: get the data into
the database, reliably.

Run this from the project root folder with:
    python scripts/extract_load.py
"""

import duckdb
import pandas as pd
from pathlib import Path

# ---- Paths -----------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
RAW_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "transactions.csv"
DB_PATH = PROJECT_ROOT / "scripts" / "bank_transactions.duckdb"


def extract_and_load():
    print(f"Reading raw CSV from: {RAW_CSV_PATH}")
    df = pd.read_csv(RAW_CSV_PATH)
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns into memory.")

    print(f"Connecting to DuckDB at: {DB_PATH}")
    con = duckdb.connect(str(DB_PATH))

    # Create a schema (a "folder" inside the database) called raw,
    # so raw data is clearly separated from cleaned/transformed data later.
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # Register the pandas dataframe as a DuckDB table.
    # "CREATE OR REPLACE" means re-running this script is safe --
    # it always resets the raw table to match the current CSV.
    con.execute("CREATE OR REPLACE TABLE raw.transactions AS SELECT * FROM df;")

    # Quick sanity check: count rows in the table we just created.
    row_count = con.execute("SELECT COUNT(*) FROM raw.transactions;").fetchone()[0]
    print(f"Success: raw.transactions now has {row_count} rows.")

    con.close()


if __name__ == "__main__":
    extract_and_load()