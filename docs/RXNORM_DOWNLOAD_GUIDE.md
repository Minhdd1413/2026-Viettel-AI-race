# RXnorm Dataset - Download Guide

## Vấn đề
- NLM API bị chặn/rate limit từ nhiều network
- Cần UMLS account để download trực tiếp từ NIH

## Giải pháp: Download từ Kaggle

### Bước 1: Tạo Kaggle Account
1. Vào https://www.kaggle.com/
2. Đăng ký tài khoản (miễn phí)
3. Xác nhận email

### Bước 2: Download Dataset
- Truy cập: https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm/data
- Click "Download" button
- File sẽ là `nlm-rxnorm.zip` (~200-300 MB)

### Bước 3: Convert RRF → JSONL

Sau khi download, giải nén và chạy script này:

```bash
python3 <<'EOF'
import csv
import json

# Parse RXNconso.RRF (pipe-delimited)
drugs = {}
with open('RXNconso.RRF', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f, delimiter='|')
    for row in reader:
        if len(row) >= 5:
            rxcui = row[0]
            language = row[1]
            
            if language == 'ENG' and rxcui not in drugs:  # English only, unique RXCUI
                drugs[rxcui] = {
                    'rxcui': rxcui,
                    'name': row[4],
                    'tty': row[2],  # Term Type
                    'language': 'EN',
                    'str': row[4]
                }

# Save to JSONL
with open('rxnorm_drugs.jsonl', 'w', encoding='utf-8') as f:
    for drug in drugs.values():
        f.write(json.dumps(drug) + '\n')

print(f"✓ Converted {len(drugs)} drugs to JSONL")
EOF
```

### Bước 4: Copy vào Project
```bash
# Copy file vào data directory
cp rxnorm_drugs.jsonl /home/mink/Outsource/viettel-race-2026/data/
```

## Cấu trúc File

Mỗi line trong JSONL:
```json
{"rxcui": "207106", "name": "Aspirin", "tty": "BN", "language": "EN", "str": "Aspirin"}
```

## Sample File

File `rxnorm_drugs.jsonl` đã tạo sẵn với 10 drugs phổ biến để test.

## RRF File Meaning
- **RXNconso.RRF** - Concepts (tên thuốc)
- **RXNrel.RRF** - Relationships (liên kết giữa các thuốc)
- **RXNsat.RRF** - Attributes (tính chất)

## Alternative: API Call

Nếu muốn query từng thuốc via API (không download):

```python
import requests

def get_drug_info(name):
    r = requests.get(
        "https://rxnav.nlm.nih.gov/REST/approximateMatch.json",
        params={'term': name, 'maxEntries': 5}
    )
    return r.json()
```

## Links
- Dataset: https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm/data
- RXnorm Docs: https://www.nlm.nih.gov/research/umls/rxnorm/docs/techdoc.html
- RRF Format: https://www.nlm.nih.gov/research/umls/rxnorm/docs/definitions.html
