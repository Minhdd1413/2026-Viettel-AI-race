#!/usr/bin/env python3
"""
Crawl full RXnorm database using NLM API
Generates rxnorm_drugs_full.jsonl with all drug concepts
"""
import requests
import json
import time
from typing import Set
import sys

BASE_URL = "https://rxnav.nlm.nih.gov/REST"

def get_all_rxcuis():
    """Get list of all RxCUI IDs from RXnorm"""
    print("📥 Fetching all RxCUI identifiers...")

    try:
        # Get all drugs - returns drug concepts
        resp = requests.get(
            f"{BASE_URL}/allconcepts.json",
            params={"searchBy": "words"},
            timeout=30
        )
        data = resp.json()

        if 'allConceptInfo' in data:
            return data['allConceptInfo']
        return []
    except Exception as e:
        print(f"⚠️  allconcepts endpoint failed: {e}")
        return []

def crawl_by_search(search_terms):
    """Crawl by searching common drug names - more reliable"""
    print("📥 Crawling by search terms...")
    drugs = {}
    seen_rxcui = set()

    # Expand search terms
    all_terms = search_terms + [
        # Common drug prefixes
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        # Common suffixes
        "-ine", "-ol", "-am", "-ate", "-ide", "-ine", "-one"
    ]

    for idx, term in enumerate(all_terms):
        try:
            resp = requests.get(
                f"{BASE_URL}/approximateMatch.json",
                params={'term': term, 'maxEntries': 100},
                timeout=10
            )
            data = resp.json()

            if 'approximateGroup' in data:
                for group in data['approximateGroup'].get('conceptGroup', []):
                    for concept in group.get('conceptProperties', []):
                        rxcui = concept['rxcui']
                        if rxcui not in seen_rxcui:
                            drugs[rxcui] = {
                                'rxcui': rxcui,
                                'name': concept['name'],
                                'tty': concept.get('tty', ''),
                                'language': concept.get('language', 'EN')
                            }
                            seen_rxcui.add(rxcui)

            if (idx + 1) % 5 == 0:
                print(f"  ✓ Progress: {idx+1}/{len(all_terms)} - {len(drugs)} drugs found")

            time.sleep(0.2)  # Rate limit

        except Exception as e:
            print(f"  ⚠️  Error on '{term}': {e}")
            continue

    return list(drugs.values())

def enrich_drug_info(drugs):
    """Add additional info for each drug"""
    print("\n📊 Enriching drug information...")
    enriched = []

    for idx, drug in enumerate(drugs):
        if idx % 50 == 0 and idx > 0:
            print(f"  ✓ Enriched {idx}/{len(drugs)}")

        try:
            rxcui = drug['rxcui']

            # Get drug properties
            props_resp = requests.get(
                f"{BASE_URL}/rxcui/{rxcui}/properties.json",
                timeout=5
            )
            props_data = props_resp.json()

            if 'properties' in props_data:
                drug['doseform'] = props_data['properties'].get('doseForm', '')
                drug['status'] = props_data['properties'].get('rxcuiStatusHistory', '')

            # Get related names (brand names, etc)
            names_resp = requests.get(
                f"{BASE_URL}/rxcui/{rxcui}/allrelated.json",
                timeout=5
            )
            names_data = names_resp.json()

            related = {}
            if 'allRelatedGroup' in names_data:
                for group in names_data['allRelatedGroup']:
                    concept_type = group.get('conceptGroup', [{}])[0].get('tty', 'OTHER')
                    items = []
                    for concept in group.get('conceptGroup', []):
                        for prop in concept.get('conceptProperties', []):
                            items.append(prop.get('name', ''))
                    if items:
                        related[concept_type] = items

            drug['related_names'] = related

            enriched.append(drug)
            time.sleep(0.1)

        except Exception as e:
            # If enrichment fails, keep basic info
            drug['related_names'] = {}
            enriched.append(drug)
            continue

    return enriched

def save_jsonl(data, filename):
    """Save to JSONL format"""
    print(f"\n💾 Saving to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✓ Saved {len(data)} records to {filename}")
    return len(data)

if __name__ == '__main__':
    search_terms = [
        # Top drugs by prescription
        "aspirin", "ibuprofen", "paracetamol", "acetaminophen", "naproxen",
        "lisinopril", "metoprolol", "amlodipine", "atenolol", "hydrochlorothiazide",
        "metformin", "glipizide", "glyburide", "insulin", "pioglitazone",
        "atorvastatin", "simvastatin", "pravastatin", "rosuvastatin", "lovastatin",
        "levothyroxine", "synthroid", "thyroid",
        "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline", "penicillin",
        "omeprazole", "ranitidine", "famotidine", "pantoprazole", "lansoprazole",
        "sertraline", "fluoxetine", "paroxetine", "citalopram", "escitalopram",
        "lorazepam", "alprazolam", "diazepam", "clonazepam",
        "warfarin", "enoxaparin", "heparin", "apixaban", "dabigatran",
        "methotrexate", "prednisone", "dexamethasone", "prednisolone",
        "salbutamol", "albuterol", "ipratropium", "budesonide", "fluticasone",
        "dopamine", "epinephrine", "norepinephrine",
        "vitamin", "calcium", "iron", "magnesium", "potassium"
    ]

    # Crawl drugs
    print("=" * 60)
    print("RXnorm Full Database Crawler")
    print("=" * 60)

    drugs = crawl_by_search(search_terms)
    print(f"\n✅ Crawled {len(drugs)} unique drugs")

    # Optional: enrich (takes longer, uncomment if needed)
    # print("\nEnriching data...")
    # drugs = enrich_drug_info(drugs)

    # Save
    output_file = 'rxnorm_drugs_full.jsonl'
    count = save_jsonl(drugs, output_file)

    print("\n" + "=" * 60)
    print(f"✅ Done! Generated {count} drug records")
    print(f"📁 File: {output_file}")
    print("=" * 60)
