# 🧬 BioLink Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

**[English](./README.md) | [繁體中文](./README_zh.md)**

A **multi-agent AI platform** for biomedical and genomic research. BioLink Agent translates natural language questions into structured queries across multiple scientific databases, gathers evidence, and synthesizes cited answers.

## ✨ Features

- **Multi-Agent Architecture**: A `CoordinatorAgent` routes tasks to domain-specialized agents (Literature, Variant, Genomics, Pathway, Protein, Disease, dbSNP, and more).
- **Pluggable Scientific Tools**: Supports PubMed, NCBI ClinVar, dbSNP, Ensembl, UniProt, and 10+ extensible tool interfaces.
- **Universal LLM Adapter**: Works with Google Gemini, OpenAI, and Anthropic Claude.
- **Async Database Logging**: SQLite-based evidence tracking via SQLAlchemy + aiosqlite.
- **REST API**: FastAPI backend with OpenAPI docs at `/docs`.

## 🏗️ Architecture

```
biolink-agent/
├── agents/          # CoordinatorAgent + domain-specific agents
├── api/             # FastAPI routes
├── core/            # LLM adapter, config
├── database/        # SQLAlchemy models, async DB
├── tools/           # Scientific tool interfaces (PubMed, ClinVar, ...)
├── main.py          # Application entrypoint
└── tests/           # Test suite
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+

### Installation

```bash
git clone https://github.com/jhjhong/biolink-agent.git
cd biolink-agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and fill in your API keys
```

### Running the API Server

```bash
source venv/bin/activate
python main.py
```

The API will be available at **http://localhost:8000**
- Interactive docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## 📡 API Reference

### `POST /api/query`

Submit a natural language biomedical question.

**Request body:**
| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Natural language question (English or Traditional Chinese) |

**Response:**
| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Synthesized answer with evidence |
| `plan` | array | Agent execution plan (which agents were invoked) |
| `evidence_collected` | integer | Number of evidence pieces gathered |

---

## 💡 Usage Examples

### Via `curl`

```bash
# Look up a gene across multiple databases
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the pathogenic variants in BRCA1 and their clinical significance?"}'

# Query by rsID
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about rs7412 in dbSNP"}'

# Traditional Chinese query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "EGFR 基因有哪些已知的藥物靶點？"}'
```

### Via Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/query",
    json={"query": "What is the allele frequency of rs7412 in global populations?"}
)
result = response.json()
print(result["answer"])
```

### Example Natural Language Queries

| Query Type | Example |
|------------|---------|
| **Gene overview** | `What are the genomic coordinates of TP53 in Ensembl and its protein length in UniProt?` |
| **Variant lookup** | `rs7412 — variant type, gene, and allele frequency` |
| **VCF coordinate** | `What variant is at chr8:19962213 C>T in dbSNP?` |
| **Clinical variants** | `What pathogenic BRCA1 variants are in ClinVar?` |
| **Drug targets** | `What drugs target EGFR? Check GWAS and DGIdb` |
| **Protein structure** | `Fetch the AlphaFold structure for TP53 and summarize its domains` |
| **Pathway** | `Which Reactome pathways involve KRAS?` |
| **Expression** | `In which tissues is BRCA2 most highly expressed? (Human Protein Atlas)` |
| **Literature** | `Recent PubMed papers on CRISPR treatment of sickle cell disease` |
| **繁體中文** | `查詢 BRCA1 在不同組織的表現量，以及與它有交互作用的蛋白質` |

### Agent Routing

The `CoordinatorAgent` automatically selects the right agent(s) for each query:

| Agent | Databases | Triggered by |
|-------|-----------|---------------|
| `LiteratureAgent` | PubMed | Paper/publication queries |
| `VariantAgent` | ClinVar | Pathogenicity, ACMG classification |
| `DbSNPAgent` | dbSNP | rsIDs, SNP/indel lookups, VCF coords |
| `GenomicsAgent` | Ensembl | Gene coordinates, transcripts |
| `ProteinAgent` | UniProt, AlphaFold | Protein sequence, structure |
| `StructureAgent` | RCSB PDB | 3D structure, PDB entries |
| `PathwayAgent` | Reactome | Biological pathways |
| `ExpressionAgent` | Human Protein Atlas | Tissue expression |
| `InteractionAgent` | STRING DB | Protein-protein interactions |
| `OntologyAgent` | QuickGO | Gene Ontology terms |
| `ChemAgent` | PubChem, ChEMBL | Chemical compounds, drugs |
| `PharmacogenomicsAgent` | DGIdb | Drug-gene interactions |
| `DiseaseAgent` | GWAS Catalog | Disease associations |
| `TaxonomyAgent` | NCBI Taxonomy | Species classification |

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `FRONTEND_URL` | Frontend origin for CORS (e.g. `https://your-app.vercel.app`) |

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## 📄 License

Apache 2.0 License — see [LICENSE](./LICENSE) for details.
