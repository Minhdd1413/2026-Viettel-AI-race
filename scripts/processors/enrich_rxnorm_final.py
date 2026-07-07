#!/usr/bin/env python3
"""
Enrich RXnorm data to match ICD-10 format standard
Input: Simple JSONL (4 fields)
Output: Rich JSONL (10+ fields like ICD-10)
"""
import json
import csv
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path("data/processed/rxnorm_drugs_full.jsonl")
OUTPUT_FILE = Path("data/processed/rxnorm_drugs_full.jsonl")
RAW_DIR = Path("data/raw")

class RXnormEnricher:
    def __init__(self):
        self.drugs = {}
        self.attributes = defaultdict(dict)
        self.relationships = defaultdict(list)
        self.semantic_types = defaultdict(list)

    def load_current_drugs(self):
        """Load existing JSONL"""
        print("📖 Loading current RXnorm data...")
        count = 0
        with open(INPUT_FILE) as f:
            for line in f:
                drug = json.loads(line)
                self.drugs[drug['rxcui']] = drug
                count += 1
        print(f"✓ Loaded {count:,} drugs")
        return True

    def load_attributes_from_csv(self):
        """Load detailed attributes from RXNSAT.csv"""
        print("📖 Loading attributes from RXNSAT...")
        file_path = RAW_DIR / "rxnorm_rxnsat.csv"

        if not file_path.exists():
            print("⚠️  RXNSAT not found")
            return True

        count = 0
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rxcui = row.get('rxcui', '').strip()
                    atn = row.get('atn', '').strip()
                    atv = row.get('atv', '').strip()

                    if rxcui in self.drugs and atn and atv:
                        if atn not in self.attributes[rxcui]:
                            self.attributes[rxcui][atn] = []
                        self.attributes[rxcui][atn].append(atv)
                        count += 1

                    if count % 100000 == 0:
                        print(f"  ✓ {count:,}")

        except Exception as e:
            print(f"⚠️  Error: {e}")

        print(f"✓ Loaded {count:,} attributes")
        return True

    def load_relationships_from_csv(self):
        """Load relationships from RXNREL.csv"""
        print("📖 Loading relationships from RXNREL...")
        file_path = RAW_DIR / "rxnorm_rxnrel.csv"

        if not file_path.exists():
            print("⚠️  RXNREL not found")
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
                            'relationship': rel
                        })
                        count += 1

                    if count % 100000 == 0:
                        print(f"  ✓ {count:,}")

        except Exception as e:
            print(f"⚠️  Error: {e}")

        print(f"✓ Loaded {count:,} relationships")
        return True

    def load_semantic_types_from_csv(self):
        """Load semantic types from RXNSTY.csv"""
        print("📖 Loading semantic types from RXNSTY...")
        file_path = RAW_DIR / "rxnorm_rxnsty.csv"

        if not file_path.exists():
            print("⚠️  RXNSTY not found")
            return True

        count = 0
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rxcui = row.get('rxcui', '').strip()
                    sty = row.get('sty', '').strip()

                    if rxcui in self.drugs and sty:
                        if sty not in self.semantic_types[rxcui]:
                            self.semantic_types[rxcui].append(sty)
                        count += 1

        except Exception as e:
            print(f"⚠️  Error: {e}")

        print(f"✓ Loaded semantic types for {len(self.semantic_types):,} drugs")
        return True

    def enrich_drugs(self):
        """Merge all data into enriched drug objects"""
        print("\n⚙️  Enriching drugs...")

        for rxcui in self.drugs:
            # Add enriched fields
            drug = self.drugs[rxcui]

            # Add ID (same as rxcui for consistency)
            drug['id'] = drug['rxcui']

            # Add code field
            drug['code'] = drug['rxcui']

            # Extract attributes and set as dedicated fields
            attrs = self.attributes.get(rxcui, {})
            drug['strength'] = '; '.join(attrs.get('STR', []))
            drug['dose_form'] = '; '.join(attrs.get('DF', []))
            drug['route'] = '; '.join(attrs.get('RTE', []))
            drug['unit'] = '; '.join(attrs.get('RXNC', []))

            # Add comprehensive attributes
            drug['all_attributes'] = attrs if attrs else {}

            # Add semantic info
            drug['semantic_types'] = self.semantic_types.get(rxcui, [])

            # Add related drugs
            drug['related_drugs'] = self.relationships.get(rxcui, [])[:10]

            # Add medical notes (can be populated from attributes)
            medical_notes = []
            if attrs.get('FREQ'):
                medical_notes.append(f"Frequency: {'; '.join(attrs['FREQ'])}")
            if attrs.get('ROUTE'):
                medical_notes.append(f"Route: {'; '.join(attrs['ROUTE'])}")
            drug['note'] = '; '.join(medical_notes) if medical_notes else ''

            # Add include/exclude (mapped from relationships if available)
            inclusions = [r.get('related_rxcui') for r in self.relationships.get(rxcui, [])
                         if r.get('relationship') == 'has_ingredient']
            drug['include'] = '; '.join(inclusions[:5]) if inclusions else ''
            drug['exclude'] = ''  # Can be populated if needed

        print(f"✓ Enriched {len(self.drugs):,} drugs")

    def save_jsonl(self):
        """Save enriched data"""
        print(f"\n💾 Saving to {OUTPUT_FILE}...")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for drug in self.drugs.values():
                # Reorder fields for consistency
                clean_drug = {
                    'id': drug.get('id'),
                    'rxcui': drug.get('rxcui'),
                    'code': drug.get('code'),
                    'name': drug.get('name'),
                    'tty': drug.get('tty'),
                    'language': drug.get('language'),
                    'strength': drug.get('strength', ''),
                    'dose_form': drug.get('dose_form', ''),
                    'route': drug.get('route', ''),
                    'semantic_types': drug.get('semantic_types', []),
                    'related_drugs': drug.get('related_drugs', []),
                    'include': drug.get('include', ''),
                    'exclude': drug.get('exclude', ''),
                    'note': drug.get('note', ''),
                    'attributes': drug.get('all_attributes', {})
                }
                f.write(json.dumps(clean_drug, ensure_ascii=False) + '\n')

        # Verify
        with open(OUTPUT_FILE) as f:
            count = sum(1 for _ in f)

        print(f"✓ Saved {count:,} enriched drugs")
        return count

    def process(self):
        """Main pipeline"""
        print("=" * 70)
        print("RXnorm Data Enrichment - Match ICD-10 Standard")
        print("=" * 70 + "\n")

        self.load_current_drugs()
        self.load_attributes_from_csv()
        self.load_relationships_from_csv()
        self.load_semantic_types_from_csv()
        self.enrich_drugs()

        count = self.save_jsonl()

        print("\n" + "=" * 70)
        print(f"✅ ENRICHED - RXnorm Now Matches ICD-10 Format")
        print(f"📁 File: {OUTPUT_FILE}")
        print(f"📊 Records: {count:,}")
        print(f"📋 Fields: id, rxcui, code, name, tty, language,")
        print(f"          strength, dose_form, route, semantic_types,")
        print(f"          related_drugs, include, exclude, note, attributes")
        print("=" * 70)

        return True

if __name__ == '__main__':
    processor = RXnormEnricher()
    processor.process()
