#!/usr/bin/env python3
"""
Parse RXnorm RRF (Rich Release Format) files to JSONL

Usage:
  1. Download from Kaggle: https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm
  2. Extract to: data/raw/RxNorm_full_YYYYMMDD/
  3. Run: python3 scripts/processors/parse_rxnorm_rrf.py

Output: data/processed/rxnorm_drugs_full.jsonl (37,000+ drugs)
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# Paths
RAW_DATA_DIR = Path("data/raw")
RRF_FILE = None
OUTPUT_FILE = Path("data/processed/rxnorm_drugs_full.jsonl")

def find_rrf_file():
    """Find RXNCONSO.RRF in data/raw"""
    global RRF_FILE

    # Search for RXNCONSO.RRF in any subdirectory
    for rrf_path in RAW_DATA_DIR.rglob("RXNCONSO.RRF"):
        RRF_FILE = rrf_path
        print(f"✓ Found: {rrf_path}")
        return True

    print(f"❌ RXNCONSO.RRF not found in {RAW_DATA_DIR}")
    print("\nExpected structure:")
    print(f"  {RAW_DATA_DIR}/")
    print(f"    rrf/")
    print(f"      RXNCONSO.RRF")
    print(f"      RXNREL.RRF")
    print(f"      RXNSAT.RRF")
    print("\nDownload from: https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm")
    return False

def parse_rrf():
    """Parse RXNCONSO.RRF to extract drugs"""
    print(f"\n📖 Parsing {RRF_FILE}...")
    print("   (RRF = Rich Release Format, pipe-delimited)")

    drugs = {}
    line_count = 0
    skipped = 0

    try:
        with open(RRF_FILE, encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')
                if not line:
                    continue

                # RRF format (pipe-delimited):
                # RXCUI|LAT|TS|LUI|STT|SUI|ISPREF|RXAUI|SAUI|SCUI|SDUI|SAB|TTY|CODE|STR|SRL|SUPPRESS|CVF
                #   0    1   2   3   4   5    6      7    8    9   10   11  12  13  14  15   16    17

                parts = line.split('|')

                if len(parts) < 15:
                    skipped += 1
                    continue

                try:
                    rxcui = parts[0].strip()      # Concept ID
                    language = parts[1].strip()    # Language
                    tty = parts[12].strip()        # Term type (BN, IN, SBD, etc)
                    name = parts[14].strip()       # String (drug name)
                    cvf = parts[17].strip() if len(parts) > 17 else ""  # CVF (Current Prescribable subset flag)

                    # Filter 1: English only
                    if language != 'ENG':
                        skipped += 1
                        continue

                    # Filter 2: Unique RXCUI (first occurrence)
                    if rxcui in drugs:
                        skipped += 1
                        continue

                    # Filter 3: Skip if name is empty
                    if not name:
                        skipped += 1
                        continue

                    # Store drug
                    drugs[rxcui] = {
                        'rxcui': rxcui,
                        'name': name,
                        'tty': tty,
                        'language': 'EN',
                        'is_prescribable': '4096' in cvf,  # CVF=4096 = Current Prescribable
                    }

                    line_count += 1

                    # Progress
                    if line_count % 50000 == 0:
                        print(f"  ✓ Processed {line_count:,} drugs, {skipped:,} skipped")

                except (IndexError, ValueError) as e:
                    skipped += 1
                    continue

    except FileNotFoundError:
        print(f"❌ File not found: {RRF_FILE}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

    print(f"\n📊 Parse Summary:")
    print(f"  Total lines: {line_num:,}")
    print(f"  Unique drugs: {len(drugs):,}")
    print(f"  Skipped: {skipped:,}")

    return drugs

def save_jsonl(drugs):
    """Save drugs to JSONL format"""
    if not drugs:
        print("❌ No drugs to save")
        return False

    print(f"\n💾 Saving to {OUTPUT_FILE}...")

    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for rxcui, drug in drugs.items():
                f.write(json.dumps(drug, ensure_ascii=False) + '\n')

        print(f"✓ Saved {len(drugs):,} drugs")

        # Verify
        with open(OUTPUT_FILE) as f:
            verified = sum(1 for _ in f)

        print(f"✓ Verified: {verified:,} records")

        return True

    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

def analyze_drugs(drugs):
    """Analyze and display drug statistics"""
    if not drugs:
        return

    print(f"\n📈 Drug Analysis:")

    # By term type
    tty_counts = defaultdict(int)
    prescribable_count = 0

    for drug in drugs.values():
        tty_counts[drug['tty']] += 1
        if drug.get('is_prescribable'):
            prescribable_count += 1

    print(f"  Term Types (Top 10):")
    for tty, count in sorted(tty_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {tty}: {count:,}")

    print(f"  Prescribable drugs: {prescribable_count:,}")

    # Sample drugs
    print(f"\n  Sample drugs:")
    for i, (rxcui, drug) in enumerate(list(drugs.items())[:5]):
        print(f"    {drug['name']} (RxCUI: {rxcui}, TTY: {drug['tty']})")

def main():
    print("=" * 70)
    print("RXnorm RRF Parser - Convert to JSONL")
    print("=" * 70)

    # Find RRF file
    if not find_rrf_file():
        return False

    # Parse
    drugs = parse_rrf()
    if not drugs:
        return False

    # Save
    if not save_jsonl(drugs):
        return False

    # Analyze
    analyze_drugs(drugs)

    print("\n" + "=" * 70)
    print(f"✅ SUCCESS!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print(f"📊 Drugs: {len(drugs):,}")
    print(f"📈 Coverage: {len(drugs) / 37000 * 100:.1f}% of ~37,000 expected")
    print("=" * 70)

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
