# Data Schema Documentation

## ICD-10 Dataset (`leaf_details.jsonl`)

**Format**: JSONL (1 record per line)  
**Size**: ~2.7 MB  
**Records**: Disease/condition leaf nodes

### Schema
```json
{
  "code": "A00",           // ICD-10 disease code
  "name": "Cholera",       // Disease name (Vietnamese/English)
  "parent_code": "A00",    // Parent category code
  "level": 3,              // Hierarchy level (1-5)
  "description": "...",    // Full description
  "category": "Infectious" // Disease category
}
```

### Fields
| Field | Type | Required | Example |
|-------|------|----------|---------|
| code | string | ✓ | "A00.0" |
| name | string | ✓ | "Cholera due to Vibrio cholerae O1, biovar Cholerae" |
| parent_code | string | ✓ | "A00" |
| level | integer | ✓ | 4 |
| description | string | ○ | Extended description |
| category | string | ○ | "Infectious Diseases" |

---

## RXnorm Dataset (`rxnorm_drugs_full.jsonl`)

**Format**: JSONL (1 record per line)  
**Size**: ~24 KB (sample) | Full: ~50-100 MB  
**Records**: Drug concepts (37,000+ in full version)

### Schema
```json
{
  "rxcui": "207106",                    // RxCUI unique identifier
  "name": "Aspirin",                    // Drug name
  "tty": "BN",                          // Term type (BN=Brand Name, IN=Ingredient)
  "language": "EN",                     // Language code
  "category": "NSAID",                  // Drug category
  "dosage": "325mg, 500mg, 650mg",     // Available dosage forms
  "related_names": {}                   // Related drug names
}
```

### Fields
| Field | Type | Required | Example |
|-------|------|----------|---------|
| rxcui | string | ✓ | "207106" |
| name | string | ✓ | "Aspirin" |
| tty | string | ✓ | "BN", "IN", "SBD" |
| language | string | ✓ | "EN" |
| category | string | ○ | "NSAID", "Antibiotic", "Statin" |
| dosage | string | ○ | "325mg, 500mg" |
| related_names | object | ○ | {} |

### RxCUI Term Types
- `BN` - Brand Name (e.g., "Aspirin")
- `IN` - Ingredient (e.g., "acetylsalicylic acid")
- `SBD` - Semantic Branded Drug
- `SCD` - Semantic Clinical Drug
- `DF` - Dose Form

---

## Tree Structure (`tree_nodes.json`)

**Format**: JSON (hierarchical tree)  
**Structure**: ICD-10 hierarchy representation

### Schema
```json
{
  "nodes": [
    {
      "id": "A00",
      "name": "Cholera",
      "level": 1,
      "children": ["A00.0", "A00.1"],
      "parent": null
    }
  ],
  "edges": [
    {"source": "A00", "target": "A00.0", "type": "parent-child"}
  ]
}
```

---

## File Naming Convention

- **Raw files**: Keep original names
- **Processed files**: `{type}_{version}_{date}.{ext}`
  - Example: `rxnorm_drugs_full_v1_20260707.jsonl`
  - Version format: `v{major}.{minor}`
  - Date format: `YYYYMMDD`

---

## Data Quality Standards

### ICD-10 (`leaf_details.jsonl`)
- ✓ No duplicate codes
- ✓ All fields present (except optional ones)
- ✓ UTF-8 encoding
- ✓ One record per line (JSONL)

### RXnorm (`rxnorm_drugs_full.jsonl`)
- ✓ No duplicate RxCUI
- ✓ Valid RxCUI format
- ✓ Dosage field must be pipe-delimited if multiple forms
- ✓ UTF-8 encoding
- ✓ One record per line (JSONL)

---

## Accessing Data

### Read JSONL
```python
import json

with open('data/processed/rxnorm_drugs_full.jsonl') as f:
    for line in f:
        drug = json.loads(line)
        print(drug['name'], drug['rxcui'])
```

### Count Records
```bash
wc -l data/processed/rxnorm_drugs_full.jsonl
```

### Convert to DataFrame
```python
import pandas as pd

df = pd.read_json('data/processed/rxnorm_drugs_full.jsonl', lines=True)
```
