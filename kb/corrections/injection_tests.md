# Injection Tests — kb/corrections/

**Protocol:** The corrections log was injected into a fresh LLM session. Questions were asked about specific failure patterns documented in the log. All tests run against `google/gemini-2.0-flash-001` via OpenRouter.

---

## Test 1 — `corrections_log.md` (Pattern A — code fence)

**Document injected:** `kb/corrections/corrections_log.md`

**Question asked:**
> An agent is generating SQL for DuckDB but the MCP server returns: "syntax error at or near \`\`\`". What is this failure, which correction entries document it, and what is the fix?

**Expected answer:**
This is Pattern A — the agent wrapped the SQL in a markdown code fence (` ```sql ... ``` `). The MCP server receives the raw string including the fence characters, causing a syntax error. Documented in COR-002, COR-006, COR-010, COR-012, COR-013, COR-015, COR-016, COR-024. Fix: add "Return raw SQL only, no markdown code fences" to `nl_to_sql()` prompt in `prompt_library.py`.

**Result:** PASS — LLM identified the code fence pattern, cited COR-002 as the first instance, and gave the prompt fix.

---

## Test 2 — `corrections_log.md` (Pattern B — MongoDB pipeline as string)

**Document injected:** `kb/corrections/corrections_log.md`

**Question asked:**
> The MCP server returns: "pipeline must be a list, not \<class 'str'\>". What caused this, and what is the fix?

**Expected answer:**
Pattern B — the agent serialized the MongoDB aggregation pipeline as a JSON string instead of a raw JSON array. The MCP server expects a list object, not a string. Documented in COR-003, COR-004, COR-005, COR-007, COR-008, COR-009, COR-017, COR-018, COR-020, COR-023. Fix: add "Return pipeline as raw JSON array starting with `[`" to `nl_to_mongodb()` prompt.

**Result:** PASS — LLM identified the pipeline serialization error and gave the prompt fix.

---

## Test 3 — `corrections_log.md` (Pattern C — wrong table in DuckDB)

**Document injected:** `kb/corrections/corrections_log.md`

**Question asked:**
> The MCP server returns: "Catalog Error: Table with name business does not exist" on a DuckDB query. What is the root cause, and what rule prevents it?

**Expected answer:**
Pattern C — the agent queried DuckDB for business data (attributes, categories, name) that does not exist in DuckDB. DuckDB (`yelp_user.db`) only contains `review`, `user`, and `tip` tables. Business data lives in MongoDB. Documented in COR-025, COR-027, COR-029, COR-031. Fix: add "DuckDB only has review, user, tip tables — business data is in MongoDB" as a Critical Rule in `agent/AGENT.md`.

**Result:** PASS — LLM identified the DuckDB table boundary issue and the AGENT.md rule.

---

## Test 4 — `corrections_log.md` (Pattern D — strptime on mixed dates)

**Document injected:** `kb/corrections/corrections_log.md`

**Question asked:**
> An agent uses `strptime(date, '%B %d, %Y at %I:%M %p')` on `review.date` and gets: "Could not parse string '29 May 2013, 23:01'". What correction entries document this and what is the fix?

**Expected answer:**
Pattern D — `review.date` in DuckDB has at least three mixed formats; a fixed strptime format string fails on variants it was not written for. Documented in COR-014, COR-026, COR-028, COR-030, COR-032. Fix: add "Never use strptime with a fixed format on date fields; use `LIKE '%2016%'` for year filtering or `TRY_STRPTIME` with `COALESCE` over all known formats" to `nl_to_sql()` prompt.

**Result:** PASS — LLM identified all Pattern D entries, listed COR-014 as the first instance, and gave the TRY_STRPTIME fix.

---

## Test 5 — `corrections_log.md` (self-learning loop)

**Document injected:** `kb/corrections/corrections_log.md`

**Question asked:**
> How does the corrections log improve agent performance over time without retraining the underlying LLM?

**Expected answer:**
The corrections log is loaded by `ContextManager` as Layer 3 at every session start. Each new entry documents a real failure: the query, the failure category, what the agent returned, and the fix applied. When the agent encounters a similar query in the next session, the corrections log entry is already in its context — it sees the pattern, the failure, and the fix before generating any query. The agent improves because its context improves, not because its weights change.

**Result:** PASS — LLM described context injection as the mechanism and distinguished it from model retraining.