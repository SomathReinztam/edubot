# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Start the app database (PostgreSQL with pgvector):**
```bash
docker compose up -d
```

**Create app database tables (run once after first `docker compose up`):**
```bash
python3 -m src.database.crud.crud
```

**Run the FastAPI server:**
```bash
uvicorn src.api.main:app --reload
```

**Run the analyst agent directly (for testing/dev):**
```bash
python3 -m src.analyst.graphs.create_analyst_agent
```

**Test the API manually:**
```bash
python3 test/api/user.py
```

All `python3 -m` commands must be run from the project root so that `src.*` imports resolve correctly.

## Architecture

### Two Databases

The system connects to two separate PostgreSQL databases:

1. **App DB** (`DB_*` env vars) — local database managed by Docker Compose, stores `appusers` and `analysis` records.
2. **EduBot DB** (`EDUBOTDB_*` env vars) — external PostgreSQL database for Solenium/Unergy's Discord monitoring system. This is the data source the AI analyst queries. Its schema is documented in `src/analyst/prompts/edubotdb.py` (`DB_SKILL_1`).

### LangGraph Analyst Agent (`src/analyst/`)

The core feature is a multi-LLM pipeline built with LangGraph (`src/analyst/graphs/create_analyst_agent.py`). It uses **three separate LLM roles**:

- **`llm_analyst`** — high-level reasoning; formulates natural-language queries and writes the final analytical report.
- **`llm_querier`** — ReAct agent with SQL tools; translates natural-language queries into SQL and executes them against the EduBot DB.
- **`llm_halting`** — classifier; decides whether the analyst has gathered enough data or needs to keep querying (returns JSON `{"query": bool, "analysis": bool, "other": bool}`).

The graph has two separate message channels in state (`messages_analyst` and `messages_ReAct`) that are managed independently. `messages_ReAct` is cleared after each querier cycle via `RemoveMessage`.

**Graph flow:**
```
START → initial_deep_query_node → set_ReAct_messages_node → querier_ReAct_node
         ↑                                                          ↓ (tool calls?)
         │                                          tool_node_wrapper ← yes
         │                                                          ↓ no
         └──── set_ReAct_messages_node ← deep_query_node ← clear_ReAct_messages_node
                                                ↓
                                         should_end_node → END (or loop back)
```

### SQL Toolkit (`src/analyst/tools/toolkit.py`)

`PostgresToolKit` exposes three LangChain `StructuredTool`s to the querier LLM:
- `get_db_tables_names` — lists all tables
- `get_tables_schemas` — returns DDL for specified tables
- `query_data_base` — executes SELECT queries, capped at `top_n` rows

### API (`src/api/`)

FastAPI app structured as `src/api/main.py` → `src/api/v1/routers/` → `src/api/v1/schemas/`. Currently two routers:
- `POST /users/` — creates an app user
- `POST /analysis/` — runs the full analyst agent and stores the result

The `Analysis` request body specifies all three LLM roles independently via a discriminated union (`GoogleModel | GroqModels | DeepSeekModels`). Supported providers: Google Gemini, Groq, DeepSeek.

### Settings and Environment

`src/utils/settings.py` loads all config from `.env` via `python-dotenv`. Required vars:
- `DB_*` — app database credentials
- `EDUBOTDB_*` — EduBot/Discord monitoring database credentials
- `GOOGLE_API_KEY`, `GROQ_API_KEY`, `DEEPSEEK_API_KEY`

### Logging

`src/utils/logging_config.py` writes rotating log files to `.logs/graph/` (gitignored). Two log files: `deep_queries.log` (analyst LLM) and `thinking_react.log` (querier/ReAct loop).
