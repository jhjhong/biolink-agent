# 🧬 BioLink Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

**[English](./README.md) | [繁體中文](./README_zh.md)**

一個專為生物醫學與基因體研究設計的 **多智能體 AI 平台**。BioLink Agent 能將自然語言問題轉化為針對多個科學資料庫的結構化查詢，收集實證，並彙整出附有引用來源的答案。

## ✨ 特色功能

- **多智能體架構**：`CoordinatorAgent` 將任務自動路由給專業領域 Agent（文獻、變異、基因體、路徑、蛋白質、疾病、dbSNP 等）。
- **可插拔科學工具**：原生支援 PubMed、NCBI ClinVar、dbSNP、Ensembl、UniProt，並提供超過 10 種可擴充的工具介面。
- **通用 LLM 適配器**：支援 Google Gemini、OpenAI 及 Anthropic Claude。
- **非同步資料庫紀錄**：透過 SQLAlchemy + aiosqlite 進行 SQLite 實證追蹤。
- **REST API**：FastAPI 後端，可於 `/docs` 瀏覽 OpenAPI 互動文件。

## 🏗️ 系統架構

```
biolink-agent/
├── agents/          # CoordinatorAgent + 各領域專業 Agent
├── api/             # FastAPI 路由
├── core/            # LLM 適配器、設定
├── database/        # SQLAlchemy 模型、非同步資料庫
├── tools/           # 科學工具介面（PubMed、ClinVar 等）
├── main.py          # 應用程式進入點
└── tests/           # 測試套件
```

## 🚀 快速開始

### 系統需求
- Python 3.10+

### 安裝步驟

```bash
git clone https://github.com/jhjhong/biolink-agent.git
cd biolink-agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 編輯 .env 填入你的 API 金鑰
```

### 啟動 API 伺服器

```bash
source venv/bin/activate
python main.py
```

API 服務將運行於 **http://localhost:8000**
- 互動式文件：http://localhost:8000/docs
- OpenAPI Schema：http://localhost:8000/openapi.json

## 📡 API 說明

### `POST /api/query`

提交自然語言生物醫學問題。

**請求欄位：**
| 欄位 | 類型 | 說明 |
|------|------|------|
| `query` | string | 自然語言問題（支援英文與繁體中文） |

**回應欄位：**
| 欄位 | 類型 | 說明 |
|------|------|------|
| `answer` | string | 含佐證來源的彙整答案 |
| `plan` | array | Agent 執行計畫（呼叫了哪些 Agent） |
| `evidence_collected` | integer | 收集到的實證數量 |

---

## 💡 使用範例

### 使用 `curl`

```bash
# 查詢基因的致病性變異
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "BRCA1 的致病性變異有哪些？它們的臨床意義為何？"}'

# 用 rsID 查詢 dbSNP
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "請告訴我 rs7412 在 dbSNP 的資訊"}'

# 用 VCF 座標查詢
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "染色體 8 位置 19962213 C>T 對應哪個 rsID？"}'
```

### 使用 Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/query",
    json={"query": "rs7412 在全球族群的等位基因頻率為何？"}
)
result = response.json()
print(result["answer"])
```

### 自然語言查詢範例

| 查詢類型 | 範例問題 |
|---------|---------|
| **基因概覽** | `TP53 基因在 Ensembl 的座標為何？UniProt 上的蛋白質序列長度是多少？` |
| **rsID 查詢** | `rs7412 的變異類型、相關基因與等位基因頻率` |
| **VCF 座標** | `chr8:19962213 C>T 在 dbSNP 中是哪個變異？` |
| **臨床變異** | `BRCA1 在 ClinVar 中有哪些致病性（Pathogenic）變異？` |
| **藥物靶點** | `哪些藥物可以靶向 EGFR？請查詢 GWAS 和 DGIdb` |
| **蛋白質結構** | `取得 TP53 的 AlphaFold 結構並總結其功能域` |
| **訊號路徑** | `KRAS 參與哪些 Reactome 路徑？` |
| **組織表現量** | `BRCA2 在哪些組織中表現量最高？（Human Protein Atlas）` |
| **文獻搜尋** | `PubMed 中關於 CRISPR 治療鐮刀型細胞貧血症的近期論文` |

### Agent 路由對照表

`CoordinatorAgent` 會自動根據問題選擇對應的 Agent：

| Agent | 資料庫 | 觸發時機 |
|-------|--------|---------|
| `LiteratureAgent` | PubMed | 論文、文獻查詢 |
| `VariantAgent` | ClinVar | 致病性分類、ACMG 證據 |
| `DbSNPAgent` | dbSNP | rsID、SNP/indel、VCF 座標查詢 |
| `GenomicsAgent` | Ensembl | 基因座標、轉錄本 |
| `ProteinAgent` | UniProt, AlphaFold | 蛋白質序列、結構 |
| `StructureAgent` | RCSB PDB | 3D 結構、PDB 條目 |
| `PathwayAgent` | Reactome | 生物訊號路徑 |
| `ExpressionAgent` | Human Protein Atlas | 組織表現量 |
| `InteractionAgent` | STRING DB | 蛋白質交互作用 |
| `OntologyAgent` | QuickGO | Gene Ontology 詞條 |
| `ChemAgent` | PubChem, ChEMBL | 化合物、藥物 |
| `PharmacogenomicsAgent` | DGIdb | 藥物–基因交互作用 |
| `DiseaseAgent` | GWAS Catalog | 疾病相關性 |
| `TaxonomyAgent` | NCBI Taxonomy | 物種分類 |


## ⚙️ 環境設定

將 `.env.example` 複製為 `.env` 並填入以下設定：

| 變數名稱 | 說明 |
|----------|------|
| `GEMINI_API_KEY` | Google Gemini API 金鑰 |
| `OPENAI_API_KEY` | OpenAI API 金鑰 |
| `ANTHROPIC_API_KEY` | Anthropic Claude API 金鑰 |
| `FRONTEND_URL` | 前端來源網址，用於 CORS 設定（例如 `https://your-app.vercel.app`） |

## 🤝 參與貢獻

歡迎任何形式的貢獻！請：
1. Fork 此 repo
2. 建立功能分支（`git checkout -b feat/your-feature`）
3. 提交 commit，遵循 [Conventional Commits](https://www.conventionalcommits.org/)
4. 發送 Pull Request

## 📄 授權條款

MIT License — 詳見 [LICENSE](./LICENSE)。
