# Download & Parse Full RXnorm Dataset (37,000+ Drugs)

## Quick Start (5 minutes)

### Step 1: Download from Kaggle
```bash
# Option A: Web browser
1. Go: https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm/data
2. Click "Download" button
3. Extract the ZIP file

# Option B: Kaggle CLI
pip install kaggle
kaggle datasets download -d nlm-nih/nlm-rxnorm -p data/raw/ --unzip
```

### Step 2: Verify Files
```bash
# Check if RRF files exist
ls -la data/raw/rrf/RXNCONSO.RRF

# Expected output:
# -rw-r--r-- ... RXNCONSO.RRF (500+ MB)
```

### Step 3: Parse to JSONL
```bash
cd /home/mink/Outsource/viettel-race-2026
python3 scripts/processors/parse_rxnorm_rrf.py
```

### Step 4: Verify Output
```bash
# Check result
wc -l data/processed/rxnorm_drugs_full.jsonl
head -1 data/processed/rxnorm_drugs_full.jsonl | python3 -m json.tool
```

---

## File Structure

```
data/raw/
└── rrf/                           (từ Kaggle zip)
    ├── RXNCONSO.RRF              (500 MB - concepts)
    ├── RXNREL.RRF                (relationships)
    ├── RXNSAT.RRF                (attributes)
    └── ...

data/processed/
└── rxnorm_drugs_full.jsonl        (output - 37,000+ drugs)
```

---

## What Gets Parsed

### RXNCONSO.RRF Format (Pipe-delimited)
```
RXCUI|LAT|TS|LUI|STT|SUI|ISPREF|RXAUI|SAUI|SCUI|SDUI|SAB|TTY|CODE|STR|SRL|SUPPRESS|CVF
207106|ENG|P|L12345|PT|S12345|Y|A12345||||RXNORM|BN|000000|Aspirin|0|N|4096
```

### Filters Applied
- ✓ Language = English only
- ✓ Unique RXCUI (first occurrence)
- ✓ Skip empty names
- ✓ Keep all term types (BN, IN, SBD, SCD, etc)

### Output JSONL Format
```json
{
  "rxcui": "207106",
  "name": "Aspirin",
  "tty": "BN",
  "language": "EN",
  "is_prescribable": true
}
```

---

## Expected Results

| Metric | Value |
|--------|-------|
| Total drugs | ~37,000 |
| File size | ~100-150 MB |
| Parse time | 2-5 minutes |
| Lines in JSONL | 37,000+ |

---

## Troubleshooting

### Problem: RXNCONSO.RRF not found
```bash
# Find the file
find data/raw -name "RXNCONSO.RRF"

# If in wrong location, move it
mv data/raw/nlm-rxnorm/rrf/* data/raw/rrf/
```

### Problem: Slow parsing
- RXNCONSO.RRF is large (~500 MB)
- Parsing takes 2-5 minutes
- Progress shown every 50,000 drugs
- Let it run, don't interrupt

### Problem: Permission denied
```bash
chmod -R 755 data/raw/
```

### Problem: Encoding errors
- Script handles UTF-8 with error='ignore'
- Skips problematic lines
- Check output with `tail -20 data/processed/rxnorm_drugs_full.jsonl`

---

## Verification

### Count records
```bash
wc -l data/processed/rxnorm_drugs_full.jsonl
# Expected: 37000+
```

### Check format
```bash
head -5 data/processed/rxnorm_drugs_full.jsonl | python3 -m json.tool
```

### Load in Python
```python
import json

with open('data/processed/rxnorm_drugs_full.jsonl') as f:
    for i, line in enumerate(f):
        drug = json.loads(line)
        if i < 3:
            print(drug)
```

---

## Data Quality Notes

- **Missing fields**: Some drugs may not have all optional fields
- **Duplicates by name**: Different RxCUI for same drug name (formulations)
- **Term types vary**: BN (Brand), IN (Ingredient), SBD (Branded), SCD (Clinical)
- **Language**: Mostly English, some multilingual entries

### Tips for Using
```python
# Filter by term type
drugs_by_name = [d for d in drugs if d['tty'] == 'BN']

# Filter prescribable only
prescribable = [d for d in drugs if d.get('is_prescribable')]

# Search by name
aspirin = [d for d in drugs if 'aspirin' in d['name'].lower()]
```

---

## Next Steps

After getting full dataset:

1. **Merge with ICD-10**
   - Link diseases → medications
   - Create association matrix

2. **Build indices**
   - Full-text search on drug names
   - RxCUI → name mapping

3. **Develop features**
   - Concept extraction
   - Entity linking
   - Medication normalization

---

## File Locations

| File | Path | Size | Status |
|------|------|------|--------|
| Raw ZIP | `data/raw/nlm-rxnorm.zip` | ~50 MB | Downloaded |
| RXNCONSO.RRF | `data/raw/rrf/RXNCONSO.RRF` | ~500 MB | Extracted |
| Output JSONL | `data/processed/rxnorm_drugs_full.jsonl` | ~100 MB | Parsed |

---

**Time to completion:** ~10 minutes (including download & parse)  
**Last updated:** 2026-07-07
