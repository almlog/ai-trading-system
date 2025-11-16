#!/usr/bin/env python3
"""
Phase 0: Download Kaggle datasets for pattern discovery

This script downloads financial news and stock price datasets from Kaggle.
Requires: kaggle API credentials in ~/.kaggle/kaggle.json
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")


def download_datasets():
    """Download datasets from Kaggle"""

    # Check Kaggle credentials
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("ERROR: Kaggle API credentials not found!")
        print("Please place kaggle.json in ~/.kaggle/")
        print("Get your API key from: https://www.kaggle.com/account")
        sys.exit(1)

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("=== Downloading Kaggle Datasets ===\n")

    # Dataset candidates (from DESIGN_DOC_FINAL.md)
    datasets = [
        {
            "name": "Financial News Headlines",
            "kaggle_id": "miguelaenlle/massive-stock-news-analysis-db-for-nlpbacktests",
            "description": "Large-scale stock news database"
        },
        {
            "name": "Daily Financial News",
            "kaggle_id": "aaron7sun/stocknews",
            "description": "Daily financial news for major stocks"
        },
        {
            "name": "Stock Market Dataset",
            "kaggle_id": "borismarjanovic/price-volume-data-for-all-us-stocks-etfs",
            "description": "Historical stock prices"
        }
    ]

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()

        for idx, dataset in enumerate(datasets, 1):
            print(f"[{idx}/{len(datasets)}] {dataset['name']}")
            print(f"  Kaggle ID: {dataset['kaggle_id']}")
            print(f"  Description: {dataset['description']}")

            try:
                api.dataset_download_files(
                    dataset['kaggle_id'],
                    path=data_dir,
                    unzip=True
                )
                print(f"  ✓ Downloaded successfully\n")
            except Exception as e:
                print(f"  ✗ Failed: {str(e)}\n")
                continue

        print("\n=== Download Complete ===")
        print(f"Data saved to: {data_dir}")
        print("\nNext steps:")
        print("  1. Inspect downloaded files: ls phase0_data_analysis/data/")
        print("  2. Run analysis: make phase0-analyze")

    except ImportError:
        print("ERROR: Kaggle package not installed!")
        print("Run: pip install kaggle")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    download_datasets()
