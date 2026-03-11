# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start the local app database
docker compose up -d

# Create DB tables (run once after first docker compose up)
python3 -m src.database.crud.crud

# Start the API server
uvicorn src.api.main:app --reload

# Run the LangGraph analyst agent directly (for testing)
python3 -m src.analyst.graphs.create_analyst_agent

# Manual API test
python3 test/api/user.py
```

All `python3 -m` commands must be run from the project root with the `.venv` active.

## Architecture

### Two Databases
- **App DB**: Local Docker PostgreSQL (credentials from `.env` `DB_*` vars). Stores users and analysis history.
- **EduBot DB**: External PostgreSQL at a remote host (credentials from `.env` `EDUBOTDB_*` vars). Read-only Discord monitoring data for Solenium/Unergy companies.

### LangGraph Pipeline (`src/analyst/graphs/create_analyst_agent.py`)
The core AI pipeline is a `StateGraph` with two parallel message channels:
- `messages_analyst`: High-level analyst reasoning (formulates queries, synthesizes results)
- `messages_ReAct`: Tool-using agent loop (translates natural language → SQL → executes)

**Graph flow:**
1. `initial_deep_query_node` — Analyst LLM generates the first natural language query
2. `set_ReAct_messages_node` — Seeds the ReAct channel with system prompt
3. `querier_ReAct_node` — Querier LLM interprets the query and calls SQL tools
4. `tool_node_wrapper` — Executes the SQL tools against EduBot DB
5. `clear_ReAct_messages_node` — Resets ReAct channel, passes result back to analyst
6. `deep_query_node` — Analyst refines analysis with the new data
7. `should_end_node` — Halting classifier (structured output) decides to loop or finish

Each call accumulates `input_tokens`, `output_tokens`, and `api_calls` in state.

### Three LLM Roles
All three are configured at runtime via the `Analysis` request schema (discriminated union `ModelProvider`):
- **Analyst**: Google/Groq/DeepSeek — formulates queries and synthesizes final analysis
- **Querier**: Google/Groq/DeepSeek — SQL ReAct agent with three tools
- **Halting**: Google/Groq/DeepSeek — classifier deciding whether to loop

### SQL Tools (`src/analyst/tools/toolkit.py`)
`PostgresToolKit` exposes three LangChain structured tools restricted to SELECT queries:
- `get_db_tables_names` — lists schema tables
- `get_tables_schemas` — returns `CREATE TABLE` DDL for given tables
- `query_data_base` — executes a SELECT and returns top-N rows

### API (`src/api/`)
FastAPI app with two routers:
- `POST /users/`, `POST /users/login`, `GET /users/{user_id}` — user CRUD
- `POST /edubot/analyze` — triggers the analyst pipeline, returns `StreamingResponse` (SSE format via `text/event-stream`)

### Key Conventions
- Prompts are written in **Spanish** (`src/analyst/prompts/analyst.py`)
- `src/analyst/prompts/edubotdb.py` contains the full EduBot DB schema as `DB_SKILL_1` (injected into querier prompt)
- `src/database/crud/schema.py` defines custom exceptions (`UserNotFoundError`, `ChatNotFoundError`) and the `ModelProvider` TypedDict
- Logs go to `.logs/graph/` as rotating files (5 MB max, 3 backups); configured in `src/utils/logging_config.py`
- No `requirements.txt` — dependencies are managed in `.venv` directly

## Key Dependencies
- `langgraph==1.0.10`, `langchain-core==1.2.17`
- `langchain-google-genai`, `langchain-groq`, `langchain-deepseek`
- `fastapi==0.135.1`, `uvicorn==0.41.0`
- `sqlalchemy`, `psycopg2-binary`
- `pydantic==2.12.5`
