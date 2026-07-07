#!/usr/bin/env python3
"""
Enrich RXnorm data by merging all CSV files → beautiful JSON format
Similar to ICD-10 structure with comprehensive drug information
"""
import csv
import json
from pathlib import Path
from collections import defaultdict

RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/rxnorm_drugs_full.jsonl")

class RXnormEnricher:
    def __init__(self):
        self.drugs = {}
        self.relationships = defaultdict(list)
        self.attributes = defaultdict(dict)

    def load_concepts(self):
        """Load drug concepts from RXNCONSO"""
        print("📖 Loading concepts...")
        file_path = RAW_DIR / "rxnorm_rxnconso.csv"

        count = 0
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rxcui = row.get('rxcui', '').strip()
                language = row.get('lat', '').strip()
                name = row.get('str', '').strip()
                tty = row.get('tty', '').strip()
                code = row.get('code', '').strip()

                if language == 'ENG' and rxcui and name:
                    if rxcui not in self.drugs:
                        self.drugs[rxcui] = {
                            'id': rxcui,
                            'rxcui': rxcui,
                            'name': name,
                            'code': code,
                            'term_type': tty,
                            'term_types': [tty],
                            'language': 'EN',
                            'brand_names': [],
                            'ingredients': [],
                            'dosage_forms': [],
                            'strength': '',
                            'dose': '',
                            'unit': '',
                            'related': [],
                            'attributes': {},
                            'semantic_types': [],
                            'ndc_codes': [],
                            'include': '',
                            'exclude': '',
                            'note': ''
                        }
                        count += 1
                    else:
                        if tty not in self.drugs[rxcui]['term_types']:
                            self.drugs[rxcui]['term_types'].append(tty)

        print(f"✓ Loaded {count:,} concepts")
        return True

    def load_attributes(self):
        """Load attributes from RXNSAT"""
        print("📖 Loading attributes...")
        file_path = RAW_DIR / "rxnorm_rxnsat.csv"

        if not file_path.exists():
            print("⚠️  RXNSAT not found")
            return True

        count = 0
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rxcui = row.get('rxcui', '').strip()
                atn = row.get('atn', '').strip()
                atv = row.get('atv', '').strip()

                if rxcui in self.drugs and atn and atv:
                    if atn == 'DF':  # Dosage Form
                        if atv not in self.drugs[rxcui]['dosage_forms']:
                            self.drugs[rxcui]['dosage_forms'].append(atv)
                    elif atn == 'STR':  # Strength
                        self.drugs[rxcui]['strength'] = atv
                    elif atn == 'DOSE':  # Dose
                        self.drugs[rxcui]['dose'] = atv
                    elif atn == 'RXN_QUANTITY':  # Unit
                        self.drugs[rxcui]['unit'] = atv
                    elif atn == 'NDC':  # NDC code
                        if atv not in self.drugs[rxcui]['ndc_codes']:
                            self.drugs[rxcui]['ndc_codes'].append(atv)

                    if atn not in self.drugs[rxcui]['attributes']:
                        self.drugs[rxcui]['attributes'][atn] = []
                    self.drugs[rxcui]['attributes'][atn].append(atv)
                    count += 1

                if count % 100000 == 0:
                    print(f"  ✓ {count:,} attributes")

        print(f"✓ Added attributes to {count:,} entries")
        return True

    def load_relationships(self):
        """Load relationships from RXNREL"""
        print("📖 Loading relationships...")
        file_path = RAW_DIR / "rxnorm_rxnrel.csv"

        if not file_path.exists():
            print("⚠️  RXNREL not found")
            return True

        count = 0
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rxcui1 = row.get('rxcui1', '').strip()
                rxcui2 = row.get('rxcui2', '').strip()
                rel = row.get('rel', '').strip()

                if rxcui1 in self.drugs and rxcui2:
                    self.relationships[rxcui1].append({
                        'related_rxcui': rxcui2,
                        'type': rel
                    })
                    count += 1

                if count % 100000 == 0:
                    print(f"  ✓ {count:,} relationships")

        print(f"✓ Loaded {count:,} relationships")
        return True

    def load_semantic_types(self):
        """Load semantic types from RXNSTY"""
        print("📖 Loading semantic types...")
        file_path = RAW_DIR / "rxnorm_rxnsty.csv"

        if not file_path.exists():
            print("⚠️  RXNSTY not found")
            return True

        count = 0
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rxcui = row.get('rxcui', '').strip()
                sty = row.get('sty', '').strip()

                if rxcui in self.drugs and sty:
                    if sty not in self.drugs[rxcui]['semantic_types']:
                        self.drugs[rxcui]['semantic_types'].append(sty)
                    count += 1

        print(f"✓ Added semantic types to {count:,} entries")
        return True

    def enrich_drugs(self):
        """Merge relationships into drugs"""
        print("⚙️  Enriching...")
        for rxcui in self.drugs:
            if rxcui in self.relationships:
                self.drugs[rxcui]['related'] = self.relationships[rxcui][:10]

        print(f"✓ Enriched {len(self.drugs):,} drugs")

    def save_jsonl(self):
        """Save enriched data to JSONL"""
        print(f"\n💾 Saving to {OUTPUT_FILE}...")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for drug in self.drugs.values():
                # Clean up data for JSON
                clean_drug = {
                    'id': drug['id'],
                    'rxcui': drug['rxcui'],
                    'name': drug['name'],
                    'code': drug['code'],
                    'term_type': drug['term_type'],
                    'term_types': drug['term_types'],
                    'language': drug['language'],
                    'strength': drug['strength'],
                    'dose': drug['dose'],
                    'dosage_forms': drug['dosage_forms'],
                    'ndc_codes': drug['ndc_codes'][:5] if drug['ndc_codes'] else [],
                    'semantic_types': drug['semantic_types'],
                    'related': drug['related'][:5] if drug['related'] else [],
                    'attributes': drug['attributes'] if drug['attributes'] else {},
                    'note': drug['note']
                }
                f.write(json.dumps(clean_drug, ensure_ascii=False) + '\n')

        # Verify
        with open(OUTPUT_FILE) as f:
            count = sum(1 for _ in f)

        print(f"✓ Saved {count:,} drugs")
        return count

    def process(self):
        """Main pipeline"""
        print("=" * 70)
        print("RXnorm Data Enrichment Pipeline")
        print("=" * 70 + "\n")

        self.load_concepts()
        self.load_attributes()
        self.load_relationships()
        self.load_semantic_types()
        self.enrich_drugs()

        count = self.save_jsonl()

        print("\n" + "=" * 70)
        print(f"✅ COMPLETE - Enriched RXnorm Dataset")
        print(f"📁 File: {OUTPUT_FILE}")
        print(f"📊 Records: {count:,}")
        print(f"📈 Coverage: {count/37000*100:.1f}% of ~37,000")
        print("=" * 70)

        return True

if __name__ == '__main__':
    processor = RXnormEnricher()
    processor.process()
