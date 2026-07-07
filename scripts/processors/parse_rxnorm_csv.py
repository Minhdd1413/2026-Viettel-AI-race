#!/usr/bin/env python3
"""
Parse RXnorm CSV files (from Kaggle) to JSONL
"""
import csv
import json
from pathlib import Path

INPUT_FILE = "data/raw/rxnorm_rxnconso.csv"
OUTPUT_FILE = "data/processed/rxnorm_drugs_full.jsonl"

def parse_csv():
    print(f"📖 Parsing {INPUT_FILE}...")

    drugs = {}
    line_count = 0

    try:
        with open(INPUT_FILE, encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header

            print(f"Columns: {header}")

            for row in reader:
                if len(row) < 15:
                    continue

                # CSV format (similar to RRF)
                rxcui = row[0].strip()
                language = row[1].strip() if len(row) > 1 else ""
                tty = row[12].strip() if len(row) > 12 else ""
                name = row[14].strip() if len(row) > 14 else ""

                # Filter English only, unique RXCUI
                if language == 'ENG' and rxcui not in drugs and name:
                    drugs[rxcui] = {
                        'rxcui': rxcui,
                        'name': name,
                        'tty': tty,
                        'language': 'EN',
                    }

                line_count += 1
                if line_count % 100000 == 0:
                    print(f"  ✓ Processed {line_count:,} lines, {len(drugs):,} unique drugs")

        print(f"\n✓ Total lines: {line_count:,}")
        print(f"✓ Unique drugs: {len(drugs):,}")

        return drugs

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_jsonl(drugs):
    if not drugs:
        print("❌ No drugs to save")
        return False

    print(f"\n💾 Saving to {OUTPUT_FILE}...")

    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for drug in drugs.values():
            f.write(json.dumps(drug, ensure_ascii=False) + '\n')

    # Verify
    with open(OUTPUT_FILE) as f:
        count = sum(1 for _ in f)

    print(f"✓ Saved {count:,} drugs")
    return True

def main():
    print("=" * 70)
    print("Parse RXnorm CSV → JSONL")
    print("=" * 70)

    drugs = parse_csv()
    if not drugs:
        return False

    if not save_jsonl(drugs):
        return False

    print("\n" + "=" * 70)
    print(f"✅ SUCCESS!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print(f"📊 Drugs: {len(drugs):,}")
    print(f"📈 Coverage: {len(drugs) / 37000 * 100:.1f}% of ~37,000 RXnorm")
    print("=" * 70)

    return True

if __name__ == '__main__':
    main()
