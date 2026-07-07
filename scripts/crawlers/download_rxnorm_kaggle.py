#!/usr/bin/env python3
"""
Download & parse RXnorm dataset from Kaggle
Requires: kaggle API credentials (~/.kaggle/kaggle.json)

Setup:
1. Install: pip install kaggle
2. Get API key from https://www.kaggle.com/settings/account
3. Save to ~/.kaggle/kaggle.json
4. Run: python3 download_rxnorm_kaggle.py
"""
import os
import json
import subprocess
import zipfile
from pathlib import Path

KAGGLE_DATASET = "nlm-nih/nlm-rxnorm"
DOWNLOAD_PATH = "data/raw"
OUTPUT_FILE = "data/processed/rxnorm_drugs_full.jsonl"

def check_kaggle_setup():
    """Check if kaggle API is installed & configured"""
    kaggle_config = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_config.exists():
        print("❌ Kaggle API not configured")
        print("\nSetup steps:")
        print("1. pip install kaggle")
        print("2. Go to https://www.kaggle.com/settings/account")
        print("3. Click 'Create New API Token' → saves kaggle.json")
        print("4. Move to ~/.kaggle/kaggle.json")
        print("5. chmod 600 ~/.kaggle/kaggle.json")
        return False

    print("✓ Kaggle API configured")
    return True

def download_dataset():
    """Download RXnorm dataset from Kaggle"""
    print(f"\n📥 Downloading {KAGGLE_DATASET}...")

    try:
        subprocess.run([
            "kaggle", "datasets", "download",
            "-d", KAGGLE_DATASET,
            "-p", DOWNLOAD_PATH,
            "--unzip"
        ], check=True)
        print("✓ Download complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ kaggle CLI not found. Install: pip install kaggle")
        return False

def parse_rrf_to_jsonl():
    """Parse RXnorm RRF files to JSONL"""
    print("\n⚙️  Parsing RRF files...")

    rxnconso_file = Path(DOWNLOAD_PATH) / "rrf" / "RXNCONSO.RRF"

    if not rxnconso_file.exists():
        print(f"❌ RXNCONSO.RRF not found at {rxnconso_file}")
        print(f"📂 Contents of {DOWNLOAD_PATH}:")
        for item in Path(DOWNLOAD_PATH).rglob("*"):
            print(f"   {item}")
        return False

    print(f"📖 Reading {rxnconso_file}...")

    drugs = {}
    line_count = 0

    try:
        with open(rxnconso_file, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_count += 1

                # RRF format: RXCUI|LAT|TS|LUI|STT|SUI|ISPREF|RXAUI|SAUI|SCUI|SDUI|SAB|TTY|CODE|STR|SRL|SUPPRESS|CVF
                parts = line.strip().split('|')

                if len(parts) < 15:
                    continue

                rxcui = parts[0]
                language = parts[1]
                tty = parts[12]  # Term type
                name = parts[14]  # String (drug name)

                # Filter: English only, unique RXCUI
                if language == 'ENG' and rxcui not in drugs:
                    drugs[rxcui] = {
                        'rxcui': rxcui,
                        'name': name,
                        'tty': tty,
                        'language': 'EN',
                    }

                if line_count % 50000 == 0:
                    print(f"  ✓ Processed {line_count:,} lines, {len(drugs):,} unique drugs")

        print(f"✓ Total lines: {line_count:,}")
        print(f"✓ Unique drugs: {len(drugs):,}")

    except Exception as e:
        print(f"❌ Parse error: {e}")
        return False

    # Save to JSONL
    print(f"\n💾 Saving to {OUTPUT_FILE}...")

    try:
        os.makedirs(Path(OUTPUT_FILE).parent, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for rxcui, drug in drugs.items():
                f.write(json.dumps(drug, ensure_ascii=False) + '\n')

        print(f"✓ Saved {len(drugs):,} drugs")

        # Verify
        with open(OUTPUT_FILE) as f:
            final_count = sum(1 for _ in f)

        print(f"✓ Verified: {final_count:,} records in {OUTPUT_FILE}")

        return len(drugs)

    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

def main():
    print("=" * 70)
    print("RXnorm Dataset Downloader - Kaggle Edition")
    print("=" * 70)

    # Check setup
    if not check_kaggle_setup():
        print("\n⚠️  Kaggle not configured. Configure and try again.")
        return False

    # Download
    if not download_dataset():
        print("\n⚠️  Download failed")
        return False

    # Parse
    result = parse_rrf_to_jsonl()

    if result:
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Got {result:,} RXnorm drugs")
        print(f"📁 Output: {OUTPUT_FILE}")
        print("=" * 70)
        return True
    else:
        print("\n⚠️  Parse failed")
        return False

if __name__ == '__main__':
    main()
