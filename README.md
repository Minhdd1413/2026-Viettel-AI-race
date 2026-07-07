# Hệ Thống AI Xử Lý Văn Bản Y Khoa - Viettel AI Race 2026

**Xây dựng hệ thống AI phát hiện, chuẩn hóa và suy luận các khái niệm y tế từ văn bản tự do**

---

## 📋 Tổng Quan

Dự án này tập trung vào việc phát triển một hệ thống AI có khả năng:
- **Xác định và chuẩn hóa** các khái niệm y tế từ văn bản lâm sàng tự do
- **Ánh xạ (mapping)** các khái niệm với chuẩn y tế quốc tế (ICD-10, RxNorm)
- **Suy luận ontology** - xác định mối liên hệ giữa các khái niệm (phủ định, tiền sử, người nhà)
- **Xử lý đa loại khái niệm**: triệu chứng, bệnh, xét nghiệm, thuốc, thông tin bệnh nhân

Hệ thống này là nền tảng quan trọng cho **chuyển đổi số y tế** và **khai thác dữ liệu lâm sàng quy mô lớn**.

---

## 🏥 Bối Cảnh Bài Toán

### Thách Thức Hiện Tại
Dữ liệu y khoa trong các bệnh viện, phòng khám thường tồn tại dưới dạng:
- **Ghi chú bác sĩ**: không chuẩn hóa, đa dạng cách diễn đạt
- **Giấy xuất viện**: chứa thông tin bệnh lý phức tạp
- **Kết quả xét nghiệm**: ký hiệu chuyên ngành, đơn vị khác nhau
- **Hồ sơ EHR**: dữ liệu từ nhiều nguồn, không đồng bộ

**Vấn đề**: Cùng một khái niệm được biểu đạt theo nhiều cách khác nhau (từ viết tắt, lỗi chính tả, biến thể địa phương), khó khăn trong việc:
- Liên thông dữ liệu giữa các cơ sở y tế
- Khai thác thông tin cho chẩn đoán và nghiên cứu dịch tễ
- Xây dựng các ứng dụng AI y khoa quy mô lớn

### Giải Pháp
Sử dụng các chuẩn y tế quốc tế như **ICD-10**, **RxNorm**, **UMLS** làm "ngôn ngữ chung" để:
- Đồng bộ hóa dữ liệu giữa các hệ thống
- Chuẩn hóa các khái niệm lâm sàng
- Cho phép các ứng dụng AI tương thích quy mô lớn

---

## 🎯 Mô Tả Bài Toán

### Input
**Một đoạn văn bản y khoa dạng tự do (free-form text)** có thể là:
- Kết quả khám lâm sàng
- Giấy xuất viện
- Ghi chú của bác sĩ
- Kết quả chẩn đoán hình ảnh
- Kết quả xét nghiệm
- Hồ sơ sức khỏe điện tử (EHR)

**Ví dụ Input:**
```
Bệnh nhân nam 70 tuổi bị bệnh 1 tuần nay, ho đờm xanh, tức ngực, đau thượng vị, ợ hơi, 
được chẩn đoán mắc bệnh trào ngược dạ dày - thực quản. Bệnh nhân có tiền sử sử dụng 
Chlorpheniramine 0.4 MG/ML, Capsaicin 0.38 MG/ML, đã tiến hành tổng phân tích tế bào 
máu bằng máy lazer (tbm): WBC:14,43; NEUT%:76,4; LYPH%:12,8;
```

### Output
**Danh sách các khái niệm y tế được phát hiện** với cấu trúc JSON:

```json
[
  {
    "text": "ho đờm xanh",
    "position": [45, 56],
    "type": "TRIỆU_CHỨNG",
    "assertions": []
  },
  {
    "text": "bệnh trào ngược dạ dày - thực quản",
    "position": [110, 145],
    "type": "CHẨN_ĐOÁN",
    "assertions": [],
    "candidates": ["K21.0", "K21.9"]
  },
  {
    "text": "Chlorpheniramine 0.4 MG/ML",
    "position": [165, 192],
    "type": "THUỐC",
    "assertions": ["isHistorical"],
    "candidates": ["360047"]
  },
  {
    "text": "WBC",
    "position": [245, 248],
    "type": "TÊN_XÉT_NGHIỆM",
    "assertions": []
  },
  {
    "text": "14,43",
    "position": [249, 254],
    "type": "KẾT_QUẢ_XÉT_NGHIỆM",
    "assertions": []
  }
]
```

### Các Trường Output

| Trường | Kiểu | Mô Tả |
|--------|------|-------|
| **text** | string | Cụm từ y tế được phát hiện trong văn bản |
| **position** | [int, int] | Vị trí bắt đầu và kết thúc (tính từ 0) |
| **type** | string | Loại khái niệm: `TRIỆU_CHỨNG`, `TÊN_XÉT_NGHIỆM`, `KẾT_QUẢ_XÉT_NGHIỆM`, `CHẨN_ĐOÁN`, `THUỐC` |
| **assertions** | list | Mối liên hệ: `"isNegated"` (phủ định), `"isFamily"` (người nhà), `"isHistorical"` (tiền sử) |
| **candidates** | list | Mã chuẩn (ICD-10 cho CHẨN_ĐOÁN, RxNorm cho THUỐC) |

### Loại Khái Niệm

- **TRIỆU_CHỨNG**: Các triệu chứng/dấu hiệu bệnh nhân mắc phải
- **TÊN_XÉT_NGHIỆM**: Tên bài xét nghiệm được thực hiện
- **KẾT_QUẢ_XÉT_NGHIỆM**: Kết quả số/giá trị của xét nghiệm
- **CHẨN_ĐOÁN**: Bệnh/chẩn đoán (ánh xạ với ICD-10)
- **THUỐC**: Tên thuốc điều trị (ánh xạ với RxNorm)

### Assertions (Suy Luận Ngữ Cảnh)

- **isNegated**: Khái niệm bị phủ định (VD: "không ho", "không sốt")
- **isFamily**: Liên quan đến người nhà/họ hàng (VD: "bố bệnh nhân mắc bệnh tiểu đường")
- **isHistorical**: Tiền sử bệnh nhân (VD: "có tiền sử hen suyễn")

---

## 📊 Dữ Liệu

### Tập Dữ Liệu
- **100 bản ghi** trong tập test
- Mỗi bản ghi là một file `.txt` chứa văn bản y khoa tự do
- Mỗi văn bản chứa **nhiều hơn 1 khái niệm**

### Cơ Sở Dữ Liệu Chuẩn Y Tế
- **ICD-10**: Bệnh tật và chẩn đoán
- **RxNorm**: Thuốc và hóa chất
- **UMLS**: Kho tri thức y khoa toàn diện

### Cấu Trúc Dữ Liệu

```
data/
├── tree_nodes.json          # ICD-10 hierarchy
├── leaf_details.jsonl       # Chi tiết ICD-10 codes
├── icd10_tt06.csv          # ICD-10 mapping (TT06)
├── icd10_tt06.xlsx         # ICD-10 mapping (Excel)
└── test/
    └── input/
        ├── 1.txt
        ├── 2.txt
        └── ...
        └── 100.txt
```

---

## 🔧 Công Nghệ & Công Cụ

### Ngôn Ngữ & Framework
- **Python 3.8+**: Lập trình chính
- **NLP/LLM**: NER (Named Entity Recognition), Text Classification
- **Agents**: Có thể sử dụng LLM agents để suy luận phức tạp
- **Knowledge Graphs**: Suy luận ontology

### Thư Viện Có Thể Sử Dụng
- `transformers` (Hugging Face) - Pre-trained models
- `spaCy` - NLP pipeline
- `NLTK` - Natural language processing
- `pandas` - Xử lý dữ liệu
- `numpy` - Tính toán số học
- `faiss` / `hnswlib` - Vector similarity search
- `networkx` - Graph reasoning

---

## 📁 Cấu Trúc Project

```
viettel-race-2026/
├── README.md                        # Tài liệu này
├── requirements.txt                 # Dependencies
├── .gitignore                       # Git ignore rules
│
├── data/                            # Dữ liệu
│   ├── raw/                         # Dữ liệu thô (không sửa đổi)
│   │   ├── icd10_tt06.csv
│   │   ├── icd10_tt06.xlsx
│   │   └── RxNorm_full_*.zip
│   │
│   └── processed/                   # Dữ liệu đã xử lý (sẵn dùng)
│       ├── leaf_details.jsonl       # ICD-10 leaf nodes (2.7MB)
│       ├── rxnorm_drugs_full.jsonl  # RXnorm drugs (37,000+ items)
│       └── tree_nodes.json          # ICD-10 hierarchy
│
├── scripts/                         # Scripts
│   ├── crawlers/                    # Crawl & fetch data
│   │   ├── crawl_rxnorm.py
│   │   ├── crawl_rxnorm_full.py
│   │   └── crawl_rxnorm_comprehensive.py
│   │
│   └── processors/                  # Process & transform data
│       └── generate_rxnorm_dataset.py
│
├── notebooks/                       # Jupyter notebooks
│   └── analysis.ipynb
│
├── docs/                            # Documentation
│   ├── PROJECT_STRUCTURE.md         # Project structure guide
│   ├── DATA_SCHEMA.md              # Data format & schema
│   ├── CONTRIBUTING.md             # Contribution guidelines
│   └── RXNORM_DOWNLOAD_GUIDE.md    # RXnorm download guide
│
├── config/                          # Configuration files
│   └── config.yaml
│
└── .claude/                         # Claude Code settings
    └── settings.json
```

**📖 Documentation Guide**:
- Start here: [`PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) - Overview & directory purposes
- Data format: [`DATA_SCHEMA.md`](docs/DATA_SCHEMA.md) - JSONL schemas & examples
- Contributing: [`CONTRIBUTING.md`](docs/CONTRIBUTING.md) - Team guidelines
- RXnorm data: [`RXNORM_DOWNLOAD_GUIDE.md`](docs/RXNORM_DOWNLOAD_GUIDE.md) - How to get full dataset

---

## 🚀 Hướng Tiếp Cận

### Giai Đoạn 1: Concept Extraction (Xác định khái niệm)
- Sử dụng NER models để phát hiện các cụm từ y tế
- Phân loại loại khái niệm (TRIỆU_CHỨNG, CHẨN_ĐOÁN, ...)

### Giai Đoạn 2: Concept Mapping (Chuẩn hóa)
- Ánh xạ concept với ICD-10 hoặc RxNorm
- Tìm top-k candidates phù hợp nhất

### Giai Đoạn 3: Assertion Detection (Suy luận ngữ cảnh)
- Phát hiện phủ định (negation)
- Xác định tiền sử (historical)
- Nhận diện liên quan người nhà (family)

### Giai Đoạn 4: Relation Extraction (Quan hệ giữa khái niệm)
- Suy luận mối liên hệ ngữ cảnh giữa các khái niệm
- Xây dựng knowledge graph

---

## 💻 Cài Đặt & Sử Dụng

### Yêu Cầu
- Python 3.8 hoặc cao hơn
- pip hoặc conda

### Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### Chạy Hệ Thống
```bash
# Xử lý toàn bộ tập test
python main.py --input data/test/input --output output

# Xử lý một file cụ thể
python main.py --input data/test/input/1.txt --output output/1.json
```

### Output
Mỗi file `.txt` sẽ tạo ra một file `.json` tương ứng trong thư mục `output/`:
```
output/
├── 1.json
├── 2.json
└── ...
└── 100.json
```

---

## 📚 Tài Liệu Tham Khảo

### Chuẩn Y Tế
- **ICD-10**: https://www.who.int/standards/classifications/classification-of-diseases
- **RxNorm**: https://www.nlm.nih.gov/research/umls/rxnorm
- **SNOMED CT**: https://www.snomed.org/
- **UMLS**: https://www.nlm.nih.gov/research/umls

### Papers & Resources
- Clinical NER in Vietnamese: Xử lý văn bản y khoa tiếng Việt
- Biomedical Entity Linking: Kỹ thuật ánh xạ entity
- Ontological Reasoning: Suy luận trên ontology y tế

---

## 👥 Đóng Góp

Dự án này là bài thi của **Viettel AI Race 2026**.

**Tác giả**: [Minhdd1413](https://github.com/Minhdd1413)

---

## 📝 Ghi Chú

- Tất cả dữ liệu cá nhân (tên, tuổi, địa chỉ, số điện thoại) trong tập dữ liệu là dữ liệu tổng hợp (synthetic), không phải thông tin người thật.
- Dự án tuân thủ các quy định về bảo mật và riêng tư dữ liệu y tế.

---

**Phát triển lần cuối**: 2026-07-07
