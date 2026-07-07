#!/usr/bin/env python3
"""
Comprehensive RXnorm crawler - Fetch ALL 37,000+ drugs from NLM API
Uses multiple search strategies + persistence to handle failures
"""
import requests
import json
import time
import sys
from typing import Set, Dict, List
from pathlib import Path

BASE_URL = "https://rxnav.nlm.nih.gov/REST"
OUTPUT_FILE = "rxnorm_drugs_full.jsonl"
CHECKPOINT_FILE = "rxnorm_crawl_checkpoint.json"

# Track progress
seen_rxcui: Set[str] = set()
drugs_data: Dict[str, dict] = {}

def load_checkpoint():
    """Load previous crawl progress"""
    global seen_rxcui, drugs_data
    if Path(CHECKPOINT_FILE).exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                checkpoint = json.load(f)
                seen_rxcui = set(checkpoint.get('seen_rxcui', []))
                drugs_data = checkpoint.get('drugs_data', {})
            print(f"✓ Loaded checkpoint: {len(seen_rxcui)} drugs already crawled")
            return True
        except:
            return False
    return False

def save_checkpoint():
    """Save progress periodically"""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'seen_rxcui': list(seen_rxcui),
            'drugs_data': drugs_data,
            'timestamp': time.time()
        }, f)

def save_final_jsonl():
    """Save all drugs to JSONL"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for rxcui, drug in drugs_data.items():
            f.write(json.dumps(drug, ensure_ascii=False) + '\n')
    print(f"✓ Saved {len(drugs_data)} drugs to {OUTPUT_FILE}")

def fetch_with_retry(url, params=None, max_retries=3):
    """Fetch with retry logic"""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:  # Rate limited
                time.sleep(2 ** attempt)
                continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                print(f"  ⚠️  Failed after {max_retries} retries: {e}")
    return None

def crawl_by_alphabet():
    """Strategy 1: Crawl by alphabetic characters"""
    print("\n📥 Strategy 1: Alphabetic Search...")
    found_this_round = 0

    # Single letters + common prefixes
    search_chars = list("abcdefghijklmnopqrstuvwxyz") + [
        "aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj",
    ]

    for idx, char in enumerate(search_chars):
        data = fetch_with_retry(
            f"{BASE_URL}/approximateMatch.json",
            params={'term': char, 'maxEntries': 200}
        )

        if data and 'approximateGroup' in data:
            for group in data['approximateGroup'].get('conceptGroup', []):
                for concept in group.get('conceptProperties', []):
                    rxcui = concept['rxcui']
                    if rxcui not in seen_rxcui:
                        drug = {
                            'rxcui': rxcui,
                            'name': concept['name'],
                            'tty': concept.get('tty', ''),
                            'language': concept.get('language', 'EN'),
                        }
                        drugs_data[rxcui] = drug
                        seen_rxcui.add(rxcui)
                        found_this_round += 1

        if (idx + 1) % 5 == 0:
            print(f"  ✓ Searched {idx + 1}/{len(search_chars)} - Found: {found_this_round} new")
        time.sleep(0.3)

    print(f"✓ Alphabet search: {found_this_round} new drugs, Total: {len(seen_rxcui)}")

def crawl_by_categories():
    """Strategy 2: Crawl by drug categories/keywords"""
    print("\n📥 Strategy 2: Category Search...")
    found_this_round = 0

    categories = [
        # Common disease/symptom keywords
        "pain", "fever", "cold", "cough", "allergy", "asthma", "diabetes", "heart",
        "blood", "infection", "antibiotic", "vitamin", "mineral", "hormone", "cancer",
        "depression", "anxiety", "sleep", "arthritis", "acid", "immune", "thyroid",
        "kidney", "liver", "stomach", "cholesterol", "pressure", "sugar", "calcium",
        "iron", "zinc", "magnesium", "potassium", "sodium", "chloride", "phosphate",
        "antihistamine", "decongestant", "bronchodilator", "corticosteroid", "anticoagulant",
        "anti-inflammatory", "analgesic", "anesthetic", "antifungal", "antiviral",
        "antiparasitic", "antimalarial", "antituberculosis", "antiretroviral", "immunosuppressant",
        "vaccine", "antitoxin", "antiseptic", "disinfectant", "laxative", "antidiarrheal",
        "antiemetic", "prokinetic", "acid-suppressing", "bile", "enzyme", "hormone",
        "growth", "metabolism", "diuretic", "vasodilator", "vasoconstrictor", "cardiotonic",
        "arrhythmia", "antianginal", "antihypertensive", "beta-blocker", "ace-inhibitor",
        "angiotensin", "calcium-channel", "statin", "fibrate", "bile-acid", "antidiabetic",
        "insulin", "sulfonylurea", "biguanide", "thiazolidinedione", "alpha-glucosidase",
        "glp-1", "dpp-4", "sglt2", "estrogen", "progestin", "androgen", "glucocorticoid",
        "mineralocorticoid", "thyroid", "antithyroid", "antacid", "h2-receptor", "proton-pump",
        "prostaglandin", "5-asa", "immunomodulator", "anthelmintic", "antimycotic", "antiprotozoal"
    ]

    for idx, cat in enumerate(categories):
        data = fetch_with_retry(
            f"{BASE_URL}/approximateMatch.json",
            params={'term': cat, 'maxEntries': 200}
        )

        if data and 'approximateGroup' in data:
            for group in data['approximateGroup'].get('conceptGroup', []):
                for concept in group.get('conceptProperties', []):
                    rxcui = concept['rxcui']
                    if rxcui not in seen_rxcui:
                        drug = {
                            'rxcui': rxcui,
                            'name': concept['name'],
                            'tty': concept.get('tty', ''),
                            'language': concept.get('language', 'EN'),
                        }
                        drugs_data[rxcui] = drug
                        seen_rxcui.add(rxcui)
                        found_this_round += 1

        if (idx + 1) % 10 == 0:
            print(f"  ✓ Searched {idx + 1}/{len(categories)} - Total: {len(seen_rxcui)}")
            save_checkpoint()  # Save every 10 categories
        time.sleep(0.2)

    print(f"✓ Category search: {found_this_round} new drugs, Total: {len(seen_rxcui)}")
    save_checkpoint()

def crawl_by_rxcui_range():
    """Strategy 3: Crawl by RxCUI ID ranges (100000-300000 typical range)"""
    print("\n📥 Strategy 3: RxCUI Range Search...")
    found_this_round = 0

    # Sample RxCUI ranges - try to cover distribution
    ranges = [
        (100, 1000, 50),      # Early range, step 50
        (1000, 10000, 100),   # Mid range, step 100
        (10000, 100000, 500), # High range, step 500
        (100000, 500000, 1000), # Very high range, step 1000
    ]

    total_to_check = sum((end - start) // step for start, end, step in ranges)
    checked = 0

    for start, end, step in ranges:
        for rxcui in range(start, end, step):
            rxcui_str = str(rxcui)

            if rxcui_str not in seen_rxcui:
                data = fetch_with_retry(f"{BASE_URL}/rxcui/{rxcui_str}/properties.json")
                if data and 'properties' in data:
                    props = data['properties']
                    drug = {
                        'rxcui': rxcui_str,
                        'name': props.get('name', f'Drug_{rxcui_str}'),
                        'language': 'EN',
                        'tty': 'IN',  # Ingredient
                    }
                    drugs_data[rxcui_str] = drug
                    seen_rxcui.add(rxcui_str)
                    found_this_round += 1

            checked += 1
            if checked % 100 == 0:
                print(f"  ✓ Checked {checked}/{total_to_check} - Found: {found_this_round}")

            time.sleep(0.05)  # Very light rate limit

    print(f"✓ RxCUI range search: {found_this_round} new drugs, Total: {len(seen_rxcui)}")
    save_checkpoint()

def crawl_related_concepts():
    """Strategy 4: Expand by fetching related concepts"""
    print("\n📥 Strategy 4: Related Concepts Expansion...")
    found_this_round = 0

    # Sample existing RxCUIs and get related ones
    sample_rxcui = list(seen_rxcui)[:100]  # Sample from what we have

    for idx, rxcui in enumerate(sample_rxcui):
        data = fetch_with_retry(f"{BASE_URL}/rxcui/{rxcui}/related.json")

        if data and 'relatedGroup' in data:
            for group in data['relatedGroup']:
                for concept_group in group.get('conceptGroup', []):
                    for concept in concept_group.get('conceptProperties', []):
                        new_rxcui = concept['rxcui']
                        if new_rxcui not in seen_rxcui:
                            drug = {
                                'rxcui': new_rxcui,
                                'name': concept['name'],
                                'tty': concept.get('tty', ''),
                                'language': concept.get('language', 'EN'),
                            }
                            drugs_data[new_rxcui] = drug
                            seen_rxcui.add(new_rxcui)
                            found_this_round += 1

        if (idx + 1) % 20 == 0:
            print(f"  ✓ Processed {idx + 1}/{len(sample_rxcui)} - Found: {found_this_round} related")
        time.sleep(0.2)

    print(f"✓ Related concepts: {found_this_round} new drugs, Total: {len(seen_rxcui)}")
    save_checkpoint()

def main():
    print("=" * 70)
    print("RXnorm COMPREHENSIVE CRAWLER - Fetch ALL 37,000+ Drugs")
    print("=" * 70)

    # Load checkpoint if exists
    load_checkpoint()

    try:
        # Run all strategies sequentially
        crawl_by_alphabet()
        crawl_by_categories()
        crawl_by_rxcui_range()
        crawl_related_concepts()

        # Final save
        save_final_jsonl()

        # Summary
        print("\n" + "=" * 70)
        print(f"✅ CRAWL COMPLETE!")
        print(f"📊 Total drugs collected: {len(seen_rxcui)}")
        print(f"📁 Output file: {OUTPUT_FILE}")
        print(f"📈 Coverage: {len(seen_rxcui)/37000*100:.1f}% of ~37,000 expected")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n⏸️  Interrupted. Saving progress...")
        save_final_jsonl()
        save_checkpoint()
        print(f"Progress saved: {len(seen_rxcui)} drugs")
        sys.exit(0)

if __name__ == '__main__':
    main()
