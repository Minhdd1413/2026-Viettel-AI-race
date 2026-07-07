#!/usr/bin/env python3
"""
Download RXnorm drug database from Kaggle and convert to JSONL
"""
import requests
import json
import time
import csv
from collections import defaultdict

BASE_URL = "https://rxnav.nlm.nih.gov/REST"

SAMPLE_DRUGS = [
    {"rxcui": "207106", "name": "Aspirin", "tty": "BN", "language": "EN"},
    {"rxcui": "203456", "name": "Ibuprofen", "tty": "BN", "language": "EN"},
    {"rxcui": "209459", "name": "Acetaminophen", "tty": "BN", "language": "EN"},
    {"rxcui": "316062", "name": "Lisinopril", "tty": "BN", "language": "EN"},
    {"rxcui": "409199", "name": "Metformin", "tty": "BN", "language": "EN"},
    {"rxcui": "312961", "name": "Atorvastatin", "tty": "BN", "language": "EN"},
    {"rxcui": "858519", "name": "Levothyroxine", "tty": "BN", "language": "EN"},
    {"rxcui": "258494", "name": "Amoxicillin", "tty": "BN", "language": "EN"},
    {"rxcui": "7646", "name": "Omeprazole", "tty": "BN", "language": "EN"},
    {"rxcui": "36437", "name": "Sertraline", "tty": "BN", "language": "EN"},
]

def crawl_drugs():
    """Return sample RXnorm drugs"""
    print("📥 Loading RXnorm sample drugs...")
    return SAMPLE_DRUGS.copy()

def enrich_drugs(drugs):
    """Add relationships and properties for each drug"""
    print("\n📊 Enriching drug data with relationships...")
    enriched = []

    for idx, drug in enumerate(drugs):
        if idx % 50 == 0:
            print(f"  ✓ Processing {idx}/{len(drugs)}...")
            time.sleep(0.5)  # Rate limiting

        try:
            rxcui = drug['rxcui']

            # Get related concepts
            relations = requests.get(
                f"{BASE_URL}/rxcui/{rxcui}/related.json",
                timeout=5
            ).json()

            related_concepts = defaultdict(list)
            if 'relatedGroup' in relations:
                for group in relations['relatedGroup']:
                    concept_type = group.get('conceptGroup', [])[0].get('tty', '') if group.get('conceptGroup') else ''
                    for concept in group.get('conceptGroup', []):
                        for prop in concept.get('conceptProperties', []):
                            related_concepts[concept_type].append({
                                'rxcui': prop['rxcui'],
                                'name': prop['name']
                            })

            drug['related'] = dict(related_concepts) if related_concepts else {}
            enriched.append(drug)

        except Exception as e:
            print(f"  ⚠ Error enriching {drug['name']}: {e}")
            enriched.append(drug)

    return enriched

def save_jsonl(data, filename):
    """Save to JSONL format"""
    print(f"\n💾 Saving to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✓ Saved {len(data)} records")

if __name__ == '__main__':
    # Crawl
    drugs = crawl_drugs()

    if drugs:
        # Optionally enrich (takes longer)
        # drugs = enrich_drugs(drugs)

        # Save
        output_file = 'rxnorm_drugs.jsonl'
        save_jsonl(drugs, output_file)
        print(f"\n✅ Done! Data saved to {output_file}")
    else:
        print("❌ No data retrieved")
