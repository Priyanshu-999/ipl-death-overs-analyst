"""Download the Cricsheet IPL ball-by-ball dataset and combine it into one CSV.

Source (public, no login needed):
    https://cricsheet.org/downloads/ipl_csv2.zip

The zip contains one CSV file per match (plus a matching *_info.csv file
per match, which we ignore here). This script downloads the zip, extracts
only the delivery files, and stacks them into data/deliveries.csv.

Run it from the project root:
    python fetch_data.py
"""

import glob
import os
import urllib.request
import zipfile

import pandas as pd

DATA_URL = "https://cricsheet.org/downloads/ipl_csv2.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ZIP_PATH = os.path.join(DATA_DIR, "ipl_csv2.zip")
RAW_DIR = os.path.join(DATA_DIR, "raw")
OUTPUT_PATH = os.path.join(DATA_DIR, "deliveries.csv")


def download_zip(url=DATA_URL, dest=ZIP_PATH):
    """Download the zip file, reusing it if it is already on disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"Zip already present, reusing it: {dest}")
        return dest
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"Saved {os.path.getsize(dest):,} bytes to {dest}")
    return dest


def combine_matches(raw_dir=RAW_DIR, output=OUTPUT_PATH):
    """Stack every per-match delivery CSV into a single deliveries file.

    Files ending in ``_info.csv`` are match metadata, not deliveries,
    so they are skipped.
    """
    files = sorted(
        f for f in glob.glob(os.path.join(raw_dir, "[0-9]*.csv"))
        if not f.endswith("_info.csv")
    )
    print(f"Found {len(files)} match delivery files.")
    frames = [pd.read_csv(f) for f in files]
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(output, index=False)
    # Season labels are not all plain years (some span two calendar years,
    # e.g. "2020/21"), so sort them as text instead of numbers.
    seasons = sorted(str(s) for s in combined["season"].dropna().unique().tolist())
    print(f"Wrote {len(combined):,} delivery rows to {output}")
    print(f"Seasons covered: {seasons[0]}-{seasons[-1]} ({len(seasons)} seasons)")
    print(f"Matches (distinct match_id): {combined['match_id'].nunique():,}")
    return combined


def main():
    download_zip()
    os.makedirs(RAW_DIR, exist_ok=True)
    print(f"Extracting to {RAW_DIR} ...")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(RAW_DIR)
    combine_matches()


if __name__ == "__main__":
    main()
