# 🧬 BioLink Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

**[English](./README.md) | [繁體中文](./README_zh.md)**

A **multi-agent AI platform** for biomedical and genomic research. BioLink Agent translates natural language questions into structured queries across multiple scientific databases, gathers evidence, and synthesizes cited answers.

## ✨ Features

- **Multi-Agent Architecture**: A `CoordinatorAgent` routes tasks to domain-specialized agents (Literature, Variant, Genomics, Pathway, Protein, Disease, and more).
- **Pluggable Scientific Tools**: Supports PubMed, NCBI ClinVar, and extensible tool interfaces.
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

**Request:**
```json
{
  "question": "What are the known pathogenic variants in BRCA1?",
  "language": "en"
}
```

**Response:**
```json
{
  "answer": "...",
  "plan": [...],
  "evidence": [...]
}
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `FRONTEND_URL` | Frontend origin for CORS (e.g. `https://your-app.vercel.app`) |

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repo
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.
