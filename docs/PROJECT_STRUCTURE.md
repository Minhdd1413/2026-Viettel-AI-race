# Project Structure

```
viettel-race-2026/
├── README.md                          # Project overview
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── data/
│   ├── raw/                          # Original, immutable data
│   │   ├── icd10_tt06.csv           # ICD-10 disease codes
│   │   ├── icd10_tt06.xlsx
│   │   └── RxNorm_full_prescribe_*.zip  # Official RXnorm releases
│   │
│   └── processed/                     # Cleaned, processed data
│       ├── leaf_details.jsonl        # ICD-10 leaf nodes (2.7MB)
│       ├── rxnorm_drugs_full.jsonl   # RXnorm drugs dataset
│       └── tree_nodes.json           # Disease hierarchy tree
│
├── scripts/
│   ├── crawlers/                     # Data collection scripts
│   │   ├── crawl_rxnorm.py          # Basic RXnorm crawler
│   │   ├── crawl_rxnorm_full.py     # Full RXnorm API crawler
│   │   └── crawl_rxnorm_comprehensive.py  # Advanced multi-strategy crawler
│   │
│   └── processors/                   # Data processing scripts
│       ├── generate_rxnorm_dataset.py    # Generate sample dataset
│       └── process_icd10.py (TODO)      # Process ICD-10 data
│
├── notebooks/
│   └── analysis.ipynb                # Exploratory data analysis
│
├── docs/
│   ├── PROJECT_STRUCTURE.md          # This file
│   ├── DATA_SCHEMA.md               # Data format documentation
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── RXNORM_DOWNLOAD_GUIDE.md     # RXnorm download instructions
│   └── API.md (TODO)                # API documentation
│
├── config/
│   ├── config.yaml                  # Main configuration
│   └── schema/                      # Data schema definitions
│       ├── icd10_schema.json
│       └── rxnorm_schema.json
│
└── .claude/                          # Claude Code settings
    ├── settings.json
    └── projects/
```

## Directory Purposes

### `/data`
- **raw/**: Original data files - NEVER MODIFIED
- **processed/**: Clean data ready for analysis/use

### `/scripts`
- **crawlers/**: Web scraping & data fetching
- **processors/**: Data cleaning, transformation, parsing

### `/docs`
- Technical documentation
- Usage guides
- API references
- Contribution guidelines

### `/notebooks`
- Jupyter notebooks for exploration
- Analysis & visualization
- Quick experiments

### `/config`
- Configuration files
- Schema definitions
- Constants
