# Contributing Guide

## Team Workflow

### 1. Data Management

#### Raw Data (`data/raw/`)
- **Immutable** - never modify original files
- Keep source files as-is
- Document source/date in filename
- Example: `icd10_tt06_20260101.csv`

#### Processed Data (`data/processed/`)
- Clean, validated, ready-to-use data
- Format: JSONL for large datasets
- One dataset = one file (no splitting)
- Example: `rxnorm_drugs_full_v1_20260707.jsonl`

**Rule**: Always commit data version in filename like:
```
{name}_{version}_{date}.{ext}
        ↓          ↓
    v1.0     20260707
```

### 2. Scripts Organization

#### Crawlers (`scripts/crawlers/`)
- Web scraping, API calls, data fetching
- Naming: `crawl_{source}_{approach}.py`
- Examples:
  - `crawl_rxnorm.py` - Basic RXnorm API crawler
  - `crawl_rxnorm_comprehensive.py` - Advanced multi-strategy crawler
- Must include:
  - Progress tracking
  - Error handling & retry logic
  - Checkpoint save (for long-running)

#### Processors (`scripts/processors/`)
- Data cleaning, transformation, parsing
- Naming: `process_{source}_{operation}.py`
- Examples:
  - `process_icd10_parse.py`
  - `generate_rxnorm_dataset.py`
- Must include:
  - Input validation
  - Output schema verification
  - Logging

### 3. Code Style

**Python**: Follow PEP 8

```python
#!/usr/bin/env python3
"""
Module docstring describing purpose
"""
import json
import time
from typing import List, Dict

def fetch_data(url: str, timeout: int = 10) -> Dict:
    """
    Fetch data from API.
    
    Args:
        url: API endpoint
        timeout: Request timeout in seconds
        
    Returns:
        Parsed JSON response
    """
    # Implementation
    pass

if __name__ == '__main__':
    main()
```

**Rules**:
- Use type hints
- 4-space indentation
- Max line length: 100 chars
- Use descriptive variable names
- Add docstrings for functions

### 4. Commit Messages

**Format**:
```
<type>: <subject>

<body>
```

**Types**:
- `data`: Add/update dataset
- `feature`: New functionality
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code reorganization
- `chore`: Build, config, dependencies

**Examples**:
```
data: Add RXnorm full dataset v1 (37,000 drugs)

- Downloaded from NLM official source
- Parsed RRF format to JSONL
- Verified 37,150 unique drug concepts

feat: Add RXnorm comprehensive crawler

- Implements 4-strategy crawl approach
- Handles API rate limiting + retries
- Saves checkpoint for resume capability

docs: Update DATA_SCHEMA with JSONL examples
```

### 5. Pull Request Checklist

Before submitting PR:

- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Type hints added for parameters & return values
- [ ] No debug print statements left
- [ ] Tested locally
- [ ] Data files are small enough for git (< 50MB)
- [ ] Updated relevant documentation
- [ ] Commit message follows format
- [ ] No hardcoded paths (use relative paths)
- [ ] No credentials/secrets in code

### 6. Data Files in Git

**Allowed in Git**:
- JSONL files < 50MB
- CSV files < 50MB
- Config files (YAML, JSON)
- Schema definitions
- Small sample data (< 1MB)

**NOT Allowed**:
- Raw downloads > 50MB
- Large ZIP files
- Binary formats
- Temporary files (checkpoints, logs)

**For large files**: Use Git LFS or document download instructions

```bash
# Example: Large file not in repo
git lfs track "*.zip"
```

### 7. Testing

**Unit tests** (if applicable):
```python
import unittest

class TestRXnormParser(unittest.TestCase):
    def test_parse_valid_drug(self):
        result = parse_drug(sample_data)
        self.assertEqual(result['rxcui'], '207106')
        
    def test_parse_invalid_drug(self):
        with self.assertRaises(ValueError):
            parse_drug(invalid_data)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python -m pytest scripts/tests/ -v
```

### 8. Documentation Updates

When adding new features:
1. Update relevant doc in `docs/`
2. Update README if major change
3. Add examples to `DATA_SCHEMA.md` if data format changed
4. Update `PROJECT_STRUCTURE.md` if new directories added

### 9. Code Review Checklist

When reviewing team member's PR:

- [ ] Code is readable & well-documented
- [ ] No obvious bugs or logic errors
- [ ] Handles edge cases & errors gracefully
- [ ] No hardcoded values
- [ ] Consistent with project style
- [ ] Data schema follows standards
- [ ] Commit messages are clear
- [ ] Tests pass

### 10. Collaboration Tips

**Communication**:
- Use GitHub Issues for bugs/features
- Use PR discussions for code review
- Document decisions in commit messages

**Branches**:
```bash
# Feature branch
git checkout -b feature/concept-mapping

# Bugfix branch
git checkout -b fix/rxnorm-parser

# Data branch
git checkout -b data/icd10-full-dataset
```

**Before Pulling Latest**:
```bash
git fetch origin
git rebase origin/main  # or merge if collaborative branch
```

---

## Questions?

- Check existing docs in `docs/`
- Ask in PR discussions
- Review similar code in repo
