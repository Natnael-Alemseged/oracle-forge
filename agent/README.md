# agent/ — Core Agent Implementation

The main oracle-forge agent: natural language → database query → synthesized answer, with self-correction and 3-layer context loading.

## Files

| File | Purpose |
|------|---------|
| `AGENT.md` | **Context Layer 1** — master context file loaded at every session start: DB schemas, join rules, behavioral rules |
| `agent_core.py` | Main orchestration loop — `analyze_intent()` → `decompose_query()` → execute → `synthesize()` → log |
| `prompt_library.py` | All LLM prompts: `intent_analysis`, `nl_to_sql`, `nl_to_mongodb`, `self_correct`, `synthesize_response`, `text_extraction` |
| `context_manager.py` | Assembles 3-layer KB within token budget — loads AGENT.md, domain KB, corrections log |
| `self_corrector.py` | 4-type failure diagnosis + retry (max 3×): `syntax_error`, `wrong_table`, `join_key_format`, `domain_knowledge_gap` |
| `response_synthesizer.py` | Merges DB results → narrative answer with confidence score and QueryTrace |
| `database_router.py` | Routes sub-queries to correct DB type based on intent and schema knowledge |
| `query_executor.py` | MCP Toolbox JSON-RPC calls to the 6 available tools |
| `state_manager.py` | Conversation history with token-based truncation |
| `llm_client.py` | OpenRouter interface (gemini-2.0-flash-001, OpenAI-compatible) |
| `models.py` | Pydantic data contracts: `QueryRequest`, `SubQuery`, `QueryTrace`, `AgentResponse` |

## Architecture

```
User question
    ↓
StateManager (conversation history, token-bounded)
    ↓
ContextManager.get_full_context()
    → Layer 1: AGENT.md (schemas, join rules)
    → Layer 2: kb/domain/ (domain terms, field maps)
    → Layer 3: kb/corrections/corrections_log.md (32 documented fixes)
    ↓
analyze_intent() → LLM → {target_databases, requires_join, join_direction}
    ↓
decompose_query() → [SubQuery(db_type, query, intent), ...]
    ↓
For each SubQuery:
    QueryExecutor → MCP Toolbox → DB result
    On failure: SelfCorrector.correct() → diagnose → retry (max 3×)
    ↓
DatabaseRouter merges results (join_key_resolver for format mismatches)
    ↓
ResponseSynthesizer.synthesize() → answer + confidence + QueryTrace
    ↓
AgentCore._log_run() → eval/run_logs/<timestamp>.json
```

## MCP Tool Names

- `postgres_query` — PostgreSQL
- `mongo_aggregate` / `mongo_find` — MongoDB
- `sqlite_query` — SQLite
- `duckdb_query` — DuckDB
- `cross_db_merge` — cross-database result merge

## Quick Test

```bash
python eval/run_query.py --question "What is the average rating of businesses in Las Vegas?"
```
