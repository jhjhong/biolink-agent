# 🧬 BioLink Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

**[English](./README.md) | [繁體中文](./README_zh.md)**

一個專為生物醫學與基因體研究設計的 **多智能體 AI 平台**。BioLink Agent 能將自然語言問題轉化為針對多個科學資料庫的結構化查詢，收集實證，並彙整出附有引用來源的答案。

## ✨ 特色功能

- **多智能體架構**：`CoordinatorAgent` 將任務自動路由給專業領域 Agent（文獻、變異、基因體、路徑、蛋白質、疾病等）。
- **可插拔科學工具**：原生支援 PubMed、NCBI ClinVar，並提供可擴充的工具介面。
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

**請求：**
```json
{
  "question": "BRCA1 已知的致病性變異有哪些？",
  "language": "zh-TW"
}
```

**回應：**
```json
{
  "answer": "...",
  "plan": [...],
  "evidence": [...]
}
```

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
