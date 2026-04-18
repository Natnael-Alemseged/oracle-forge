# Injection Tests — kb/architecture/

**Protocol:** Each document was injected into a fresh LLM session (no other context). A question was asked that the document should answer. If the LLM returned the expected answer from the document alone, the document passes. All tests run against `google/gemini-2.0-flash-001` via OpenRouter.

---

## Test 1 — `self_correction_loop.md`

**Document injected:** `kb/architecture/self_correction_loop.md`

**Question asked:**
> An agent joins PostgreSQL and MongoDB on customer ID and gets zero rows. Walk through the four steps of the self-correction loop for this failure.

**Expected answer:**
Step 1 — execute the join, receive zero rows. Step 2 — diagnose: zero rows on a join is a join key format mismatch (not a routing error, because both databases were reached). Step 3 — recover: call `resolve_join_key()` to convert the PostgreSQL integer ID to the MongoDB string format, then retry the join. Step 4 — log the mismatch, the format conversion applied, and whether the retry succeeded in `kb/corrections/corrections_log.md`.

**Result:** PASS — LLM returned the four steps with correct diagnosis (join key format mismatch) and correct recovery action (`resolve_join_key()`).

---

## Test 2 — `dab_failure_modes.md`

**Document injected:** `kb/architecture/dab_failure_modes.md`

**Question asked:**
> What are the four DAB failure categories, and which one is hardest to detect automatically?

**Expected answer:**
The four categories are: (1) multi-database routing failure, (2) ill-formatted join key mismatch, (3) unstructured text extraction failure, (4) domain knowledge gap. Domain knowledge gap (Category 4) is hardest to detect automatically because the query runs without error and returns a result — but the result is wrong because the agent used a naive interpretation of a term instead of the domain-correct definition. There is no exception to catch.

**Result:** PASS — LLM identified all four categories and correctly flagged Category 4 as the silent failure mode.

---

## Test 3 — `claude_code_memory.md`

**Document injected:** `kb/architecture/claude_code_memory.md`

**Question asked:**
> What is the three-layer memory structure in Claude Code, and what is the purpose of MEMORY.md?

**Expected answer:**
The three layers are: (1) MEMORY.md — a short index file always loaded into context; (2) topic files — detailed documents loaded on demand; (3) session transcripts — searchable history. MEMORY.md is the always-loaded index that tells the agent which topic files to load without loading everything upfront.

**Result:** PASS — LLM described all three layers and correctly identified MEMORY.md as the always-loaded index.

---

## Test 4 — `tool_scoping_and_parallelism.md`

**Document injected:** `kb/architecture/tool_scoping_and_parallelism.md`

**Question asked:**
> Why does Oracle Forge use narrow tool scoping (one tool per database type) instead of a single generic database tool?

**Expected answer:**
Narrow tool scoping prevents routing failures by making the agent commit to a database at tool-selection time. A generic database tool would require the agent to determine the database internally, creating an opaque failure mode. With narrow tools (`postgres_query`, `mongo_aggregate`, `duckdb_query`), the wrong tool produces an immediate, diagnosable error rather than a silent wrong result. It also enables parallel execution across databases.

**Result:** PASS — LLM gave routing failure prevention and parallel execution as the two key reasons.

---

## Test 5 — `openai_data_agent_context.md`

**Document injected:** `kb/architecture/openai_data_agent_context.md`

**Question asked:**
> How many context layers does the OpenAI in-house data agent use, and which three are mandatory for Oracle Forge?

**Expected answer:**
The OpenAI data agent uses six context layers. The three mandatory layers for Oracle Forge are: (1) schema and metadata knowledge loaded before any query, (2) institutional and domain knowledge (business term definitions, join key formats), and (3) interaction memory / corrections log (past failures and corrections, read and written each session).

**Result:** PASS — LLM correctly identified six total layers and the three mandatory ones.
