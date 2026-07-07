#!/usr/bin/env python3
"""
Complete RXnorm data processing & enrichment
Merge all CSV files → Beautiful JSONL format

Files processed:
- rxnorm_rxnconso.csv: Concepts (drug names)
- rxnorm_rxncui.csv: Concept info
- rxnorm_rxnrel.csv: Relationships between concepts
- rxnorm_rxnsat.csv: Semantic attributes
- rxnorm_rxnsty.csv: Semantic types
- rxnorm_rxnatomarchive.csv: Atom archives
"""
import csv
import json
from pathlib import Path
from collections import defaultdict

# Paths
RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/rxnorm_drugs_full.jsonl")

class RXnormProcessor:
    def __init__(self):
        self.drugs = {}  # rxcui -> drug data
        self.relationships = defaultdict(list)
        self.attributes = defaultdict(dict)
        self.semantic_types = {}

    def load_concepts(self):
        """Load RXNCONSO - drug concepts"""
        print("📖 Loading RXNCONSO (concepts)...")

        file_path = RAW_DIR / "rxnorm_rxnconso.csv"
        if not file_path.exists():
            print(f"❌ {file_path} not found")
            return False

        count = 0
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    rxcui = row.get('rxcui', '').strip()
                    language = row.get('lat', '').strip()
                    name = row.get('str', '').strip()
                    tty = row.get('tty', '').strip()

                    # Keep first occurrence per RXCUI
                    if language == 'ENG' and rxcui and name and rxcui not in self.drugs:
                        self.drugs[rxcui] = {
                            'rxcui': rxcui,
                            'name': name,
                            'tty': tty,
                            'language': 'EN',
                            'term_types': set([tty]),
                            'preferred_name': name if tty == 'BN' else '',
                            'related_drugs': [],
                            'attributes': {},
                            'semantic_types': []
                        }
                        count += 1
                    elif language == 'ENG' and rxcui in self.drugs:
                        # Track term types
                        self.drugs[rxcui]['term_types'].add(tty)
                        # Track preferred name
                        if tty == 'BN' and not self.drugs[rxcui]['preferred_name']:
                            self.drugs[rxcui]['preferred_name'] = name

                    if count % 50000 == 0:
                        print(f"  ✓ {count:,} concepts loaded")

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

        print(f"✓ Loaded {count:,} concepts")
        return True

    def load_semantic_types(self):
        """Load RXNSTY - semantic types"""
        print("\n📖 Loading RXNSTY (semantic types)...")

        file_path = RAW_DIR / "rxnorm_rxnsty.csv"
        if not file_path.exists():
            print(f"⚠️  {file_path} not found, skipping")
            return True

        count = 0
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    rxcui = row.get('rxcui', '').strip()
                    sty = row.get('sty', '').strip()

                    if rxcui in self.drugs and sty:
                        if sty not in self.drugs[rxcui]['semantic_types']:
                            self.drugs[rxcui]['semantic_types'].append(sty)
                        count += 1

                    if count % 50000 == 0:
                        print(f"  ✓ {count:,} semantic types loaded")

        except Exception as e:
            print(f"⚠️  Error: {e}")

        print(f"✓ Added semantic types to {count:,} drugs")
        return True

    def load_attributes(self):
        """Load RXNSAT - semantic attributes"""
        print("\n📖 Loading RXNSAT (attributes)...")

        file_path = RAW_DIR / "rxnorm_rxnsat.csv"
        if not file_path.exists():
            print(f"⚠️  {file_path} not found, skipping")
            return True

        count = 0
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    rxcui = row.get('rxcui', '').strip()
                    atn = row.get('atn', '').strip()  # Attribute name
                    atv = row.get('atv', '').strip()  # Attribute value

                    if rxcui in self.drugs and atn and atv:
                        if atn not in self.drugs[rxcui]['attributes']:
                            self.drugs[rxcui]['attributes'][atn] = []
                        self.drugs[rxcui]['attributes'][atn].append(atv)
                        count += 1

                    if count % 100000 == 0:
                        print(f"  ✓ {count:,} attributes loaded")

        except Exception as e:
            print(f"⚠️  Error: {e}")

        print(f"✓ Added attributes to {count:,} entries")
        return True

    def load_relationships(self):
        """Load RXNREL - relationships between concepts"""
        print("\n📖 Loading RXNREL (relationships)...")

        file_path = RAW_DIR / "rxnorm_rxnrel.csv"
        if not file_path.exists():
            print(f"⚠️  {file_path} not found, skipping")
            return True

        count = 0
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    rxcui1 = row.get('rxcui1', '').strip()
                    rxcui2 = row.get('rxcui2', '').strip()
                    rel = row.get('rel', '').strip()

                    if rxcui1 in self.drugs and rxcui2:
                        self.relationships[rxcui1].append({
                            'related_rxcui': rxcui2,
                            'relationship_type': rel
                        })
                        count += 1

                    if count % 100000 == 0:
                        print(f"  ✓ {count:,} relationships loaded")

        except Exception as e:
            print(f"⚠️  Error: {e}")

        print(f"✓ Loaded {count:,} relationships")
        return True

    def enrich_drugs(self):
        """Merge all data into final drug objects"""
        print("\n⚙️  Enriching drugs...")

        for rxcui in self.drugs:
            # Add relationships
            if rxcui in self.relationships:
                self.drugs[rxcui]['related_drugs'] = self.relationships[rxcui][:10]  # Top 10

        print(f"✓ Enriched {len(self.drugs):,} drugs")

    def save_jsonl(self):
        """Save to JSONL with clean format"""
        print(f"\n💾 Saving to {OUTPUT_FILE}...")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for drug in self.drugs.values():
                # Convert sets to lists
                drug_data = {
                    'rxcui': drug['rxcui'],
                    'name': drug['name'],
                    'preferred_name': drug['preferred_name'] or drug['name'],
                    'tty': drug['tty'],
                    'language': drug['language'],
                    'term_types': sorted(list(drug['term_types'])),
                    'semantic_types': drug['semantic_types'] if drug['semantic_types'] else [],
                    'attributes': drug['attributes'] if drug['attributes'] else {},
                    'related_drugs': drug['related_drugs'][:5] if drug['related_drugs'] else [],
                }
                f.write(json.dumps(drug_data, ensure_ascii=False) + '\n')

        # Verify
        with open(OUTPUT_FILE) as f:
            count = sum(1 for _ in f)

        print(f"✓ Saved {count:,} drugs to {OUTPUT_FILE}")
        return count

    def process(self):
        """Main processing pipeline"""
        print("=" * 70)
        print("RXnorm Complete Processing Pipeline")
        print("=" * 70)

        if not self.load_concepts():
            return False

        self.load_semantic_types()
        self.load_attributes()
        self.load_relationships()
        self.enrich_drugs()

        count = self.save_jsonl()

        if count:
            print("\n" + "=" * 70)
            print(f"✅ COMPLETE!")
            print(f"📁 Output: {OUTPUT_FILE}")
            print(f"📊 Drugs: {count:,}")
            print(f"📈 Coverage: {count / 37000 * 100:.1f}% of ~37,000 RXnorm")
            print("=" * 70)
            return True

        return False

def main():
    processor = RXnormProcessor()
    return processor.process()

if __name__ == '__main__':
    main()
