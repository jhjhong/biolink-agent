# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-06-03
### Added
- **Core Architecture**: Pluggable Multi-Agent framework (`CoordinatorAgent`, `BaseAgent`).
- **Agents**: `LiteratureAgent` and `VariantAgent`.
- **Tools**: `PubMedTool` and `ClinVarTool` utilizing NCBI E-utilities.
- **LLM Provider**: Unified adapter supporting Gemini, OpenAI, and Anthropic Claude.
- **Database Layer**: Asynchronous SQLite logging (`QueryLog`) using `aiosqlite` and `SQLAlchemy`.
- **API Layer**: FastAPI application with `POST /api/query` endpoint and CORS enabled.
- **Frontend**: Next.js (React) chat interface featuring Tailwind CSS, dark mode, and inline task planning visualization.
- **Multi-Language Support**: Explicitly supports English and Traditional Chinese for biomedical querying and synthesis.
