# Oracle Forge: Driver 2 Sprint Plan (Agent Logic & Context Engineering)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Agent Logic & Context Engineering layer for The Oracle Forge — an NL-to-query agent spanning 4 database types with self-correction, three-layer context, and verifiable output traces.

**Architecture:** `AgentCore` orchestrates the main loop (intent → decomposition → query generation → synthesis). `PromptLibrary` centralizes all LLM prompts. Three context layers (schema, domain knowledge, corrections log) are injected at session start and used throughout.

**Tech Stack:** Python, Anthropic Claude API (`anthropic`), Pydantic v2, MCP Toolbox (HTTP), FastAPI (agent server), pytest

---

## PLAN ASSESSMENT: Existing Implementation Plan Review

**What is valid and correct:**
- Phase structure (Foundation → Core Build → Context Engineering → Adversarial Testing → Final) matches the challenge rubric exactly
- Driver role separation is clean — Driver 1 owns infra/execution, Driver 2 owns logic/prompts/context
- Deliverable list maps to the grading rubric (25% running agent, 20% DAB benchmark, 20% context layers, etc.)
- Collaboration points (mob session, API design workshop, paired evaluation) are correctly placed

**Gaps and issues to address:**
1. **No concrete code structure** — plan says "create AgentCore skeleton" but never shows the class interface or file layout
2. **No prompt templates** — "draft NL-to-SQL prompt" is listed but the actual prompt design is left undefined
3. **AGENT.md has no template** — the most critical file for context layer injection has no defined structure
4. **Self-correction loop is underspecified** — plan says "retry up to 3 times" but doesn't define the 4 failure type diagnosis logic
5. **Token budget management is missing** — context layers can blow the context window; truncation strategy is mentioned but never designed
6. **The Internal Probing Strategy doc is misread** — it's a meta-methodology for probing AI systems' own internals (memory, tool use, provenance), not just adversarial DAB queries. It should inform how the agent handles its own transparency and the probe design process
7. **Timeline is tight** — today is Day 3 (April 9). Days 1-2 tasks may be undone. Prioritize what remains

**CRITICAL DATE CONTEXT:**
- Day 1 = April 7 | Day 2 = April 8 | **Day 3 = April 9 (TODAY)**
- Interim submission: **Tuesday April 14, 21:00 UTC** (Day 6 of sprint, 5 days away)
- Final submission: **Saturday April 18, 21:00 UTC** (Day 10 of sprint)
- Agent must be running on team server before interim submission

---

## File Structure

```
agent/
├── AGENT.md                    # Master context file (Context Layer 1 schema + behavioral rules)
├── agent_core.py               # AgentCore: main loop, intent analysis, response synthesis
├── prompt_library.py           # PromptLibrary: all LLM prompt templates, centralized
├── context_manager.py          # ContextManager: loads and manages 3 context layers
├── self_corrector.py           # SelfCorrector: failure diagnosis + retry logic (4 failure types)
├── response_synthesizer.py     # ResponseSynthesizer: merges results → human-readable answer
├── models.py                   # Pydantic data contracts shared with Driver 1
└── tools.yaml                  # MCP Toolbox config (owned by Driver 1, you coordinate)

kb/
├── corrections/corrections.md  # Corrections log (Layer 3) — failures → fixes
├── domain/domain_knowledge.md  # Domain KB (Layer 2) — from Intelligence Officers
├── architecture/schema.md      # Schema descriptions (Layer 1 supplement)
└── evaluation/                 # Evaluation docs

utils/
├── token_counter.py            # Token budget estimator for context window management
├── text_extractor.py           # Unstructured text → structured data extraction
└── README.md                   # Utils usage examples
```

---

## SPRINT PLAN — DRIVER 2 TASKS

### CATCH-UP: Days 1–2 (If Not Done)

These tasks from the original plan must be complete before Day 3 work:

- [ ] Read all three source docs: Challenge, Practitioner Manual, Internal Probing Strategy
- [ ] Clone repo, configure local env, verify Tailscale connectivity
- [ ] Draft `planning/inception_v1.md` (AI-DLC Inception document) — press release paragraph, user FAQ (3 Q&A), technical FAQ (3 Q&A), key decisions, definition of done (5-8 items). Get mob session approval.
- [ ] Create `agent/models.py` with Pydantic data contracts (coordinate with Driver 1):

```python
from pydantic import BaseModel
from typing import Optional, Any

class QueryRequest(BaseModel):
    question: str
    available_databases: list[str]
    session_id: str

class SubQuery(BaseModel):
    database_type: str  # "postgresql" | "sqlite" | "mongodb" | "duckdb"
    query: str
    intent: str

class QueryTrace(BaseModel):
    timestamp: str
    sub_queries: list[SubQuery]
    databases_used: list[str]
    self_corrections: list[dict]
    raw_results: dict[str, Any]
    merge_operations: list[str]

class AgentResponse(BaseModel):
    answer: str
    query_trace: QueryTrace
    confidence: float  # 0.0–1.0
    error: Optional[str] = None
```

- [ ] Create `agent/prompt_library.py` skeleton with placeholder methods
- [ ] Create `agent/agent_core.py` skeleton with `AgentCore` class interface

---

### Day 3 (TODAY — April 9): Core Agent Loop

**Goal:** End of today — agent receives NL query, routes to correct DB type, generates a query, executes via Driver 1's QueryExecutor, and returns structured result with trace.

#### Task 1: Implement AgentCore main loop

**File:** `agent/agent_core.py`

- [ ] Implement `analyze_intent()` — LLM call to identify which databases are needed and extract structured intent:

```python
import anthropic
from agent.models import QueryRequest, AgentResponse, QueryTrace, SubQuery
from agent.prompt_library import PromptLibrary
from agent.context_manager import ContextManager
from datetime import datetime
import json

class AgentCore:
    def __init__(self, context_manager: ContextManager, prompt_library: PromptLibrary):
        self.client = anthropic.Anthropic()
        self.ctx = context_manager
        self.prompts = prompt_library

    def analyze_intent(self, question: str, available_databases: list[str]) -> dict:
        """Returns: {"target_databases": [...], "intent_summary": str, "requires_join": bool}"""
        system_context = self.ctx.get_full_context()
        prompt = self.prompts.intent_analysis(question, available_databases)
        msg = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=system_context,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def run(self, request: QueryRequest) -> AgentResponse:
        intent = self.analyze_intent(request.question, request.available_databases)
        sub_queries = self.decompose_query(request.question, intent)
        # Driver 1's QueryExecutor handles execution — we pass sub_queries to it
        ...
```

- [ ] Implement `decompose_query()` — breaks multi-DB queries into sub-queries per database type

#### Task 2: Implement PromptLibrary

**File:** `agent/prompt_library.py`

- [ ] Implement `intent_analysis` prompt (returns JSON with target databases + intent):

```python
class PromptLibrary:
    def intent_analysis(self, question: str, available_databases: list[str]) -> str:
        return f"""Analyze this data question and determine which databases to query.

Question: {question}
Available databases: {', '.join(available_databases)}

Respond with valid JSON only:
{{
  "target_databases": ["postgresql", "mongodb"],  // which DB types to query
  "intent_summary": "brief description of what data is needed",
  "requires_join": true/false,  // does this need cross-DB merging?
  "data_fields_needed": ["field1", "field2"]  // key fields from the question
}}"""

    def nl_to_sql(self, question: str, schema: str, dialect: str = "postgresql") -> str:
        return f"""Generate a {dialect.upper()} query for this question.

Schema:
{schema}

Question: {question}

Rules:
- Return only the SQL query, no explanation
- Use exact table and column names from the schema
- For {dialect}: {self._dialect_rules(dialect)}"""

    def _dialect_rules(self, dialect: str) -> str:
        rules = {
            "postgresql": "use ILIKE for case-insensitive search, LIMIT for pagination",
            "sqlite": "use LIKE for search, no ILIKE, use strftime for dates",
            "duckdb": "use DuckDB analytical functions, SAMPLE for large datasets",
            "mongodb": "return a MongoDB aggregation pipeline as a JSON array"
        }
        return rules.get(dialect, "use standard SQL")
```

- [ ] Implement `nl_to_mongodb` prompt (aggregation pipeline generation)

#### Task 3: Wire up first self-correction cycle (basic version)

**File:** `agent/self_corrector.py`

- [ ] Implement basic retry wrapper (full 4-type diagnosis comes Day 5):

```python
class SelfCorrector:
    def __init__(self, prompt_library: PromptLibrary, client):
        self.prompts = prompt_library
        self.client = client
        self.max_retries = 3

    def correct(self, original_question: str, failed_query: str, error: str,
                db_type: str, schema: str, attempt: int) -> str:
        """Generate corrected query given the error."""
        prompt = self.prompts.self_correct(original_question, failed_query, error, db_type, schema)
        msg = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text.strip()
```

- [ ] Add `self_correct` to PromptLibrary:

```python
def self_correct(self, question: str, failed_query: str, error: str,
                 db_type: str, schema: str) -> str:
    return f"""A database query failed. Generate a corrected query.

Original question: {question}
Database type: {db_type}
Failed query: {failed_query}
Error message: {error}

Schema:
{schema}

Fix the query. Return only the corrected query, no explanation."""
```

- [ ] Integrate SelfCorrector into AgentCore.run() — wrap QueryExecutor calls with retry

---

### Day 4 (April 10): Multi-DB Dialects + Response Synthesis

**Goal:** Agent generates correct query dialects for all 4 DB types. Human-readable answers produced with full query trace.

#### Task 4: Complete PromptLibrary for all DB types

- [ ] Add MongoDB aggregation pipeline prompt to PromptLibrary (full implementation):

```python
def nl_to_mongodb(self, question: str, collection_schema: str) -> str:
    return f"""Generate a MongoDB aggregation pipeline for this question.

Collection schema:
{collection_schema}

Question: {question}

Return a valid JSON array representing the aggregation pipeline stages.
Example: [{{"$match": {{"status": "active"}}}}, {{"$group": {{"_id": "$category", "count": {{"$sum": 1}}}}}}]

Return only the JSON array, no explanation."""
```

- [ ] Add DuckDB analytical SQL prompt
- [ ] Add response synthesis prompt:

```python
def synthesize_response(self, question: str, merged_results: dict, query_trace: dict) -> str:
    return f"""Synthesize a clear, direct answer to the user's question from these database results.

Question: {question}

Results from databases:
{json.dumps(merged_results, indent=2)}

Rules:
- Answer the question directly in 1-3 sentences
- Include specific numbers/values from the results
- If results are empty, say so explicitly
- Do not mention internal query details in the answer"""
```

#### Task 5: Implement ResponseSynthesizer

**File:** `agent/response_synthesizer.py`

- [ ] Implement `ResponseSynthesizer.synthesize()` — calls LLM with merged results to produce answer
- [ ] Implement `ResponseSynthesizer.extract_from_text()` — unstructured text → structured data:

```python
def extract_from_text(self, text_field: str, extraction_goal: str) -> dict:
    """Extract structured data from free-text fields (reviews, notes, etc.)"""
    prompt = self.prompts.text_extraction(text_field, extraction_goal)
    msg = self.client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(msg.content[0].text)
```

- [ ] Add `text_extraction` to PromptLibrary:

```python
def text_extraction(self, text: str, goal: str) -> str:
    return f"""Extract structured information from this text.

Goal: {goal}
Text: {text}

Return a JSON object with the extracted information. Example for sentiment:
{{"sentiment": "positive", "key_topics": ["service", "food"], "rating_implied": 4}}

Return only valid JSON."""
```

#### Task 6: Implement ContextManager (skeleton for Day 6 full implementation)

**File:** `agent/context_manager.py`

- [ ] Implement layer loading stubs so the rest of the code can call `get_full_context()`:

```python
class ContextManager:
    def __init__(self, agent_md_path: str, corrections_path: str, domain_kb_path: str):
        self.agent_md_path = agent_md_path
        self.corrections_path = corrections_path
        self.domain_kb_path = domain_kb_path
        self._session_history: list[dict] = []

    def get_full_context(self, token_budget: int = 8000) -> str:
        """Assemble all three layers within token budget."""
        layers = []
        layers.append(self._load_layer1_schema())      # AGENT.md
        layers.append(self._load_layer2_domain())      # domain KB
        layers.append(self._load_layer3_corrections()) # corrections log
        return self._fit_to_budget("\n\n---\n\n".join(layers), token_budget)

    def _load_layer1_schema(self) -> str:
        with open(self.agent_md_path) as f:
            return f.read()

    def _load_layer2_domain(self) -> str:
        try:
            with open(self.domain_kb_path) as f:
                return f.read()
        except FileNotFoundError:
            return "# Domain Knowledge\n(Not yet populated)"

    def _load_layer3_corrections(self) -> str:
        try:
            with open(self.corrections_path) as f:
                return f.read()
        except FileNotFoundError:
            return "# Corrections Log\n(No corrections yet)"

    def _fit_to_budget(self, text: str, token_budget: int) -> str:
        # Rough estimate: 1 token ≈ 4 chars
        char_budget = token_budget * 4
        if len(text) <= char_budget:
            return text
        # Truncate from middle (preserve Layer 1 schema and recent corrections)
        return text[:char_budget // 2] + "\n...[truncated]...\n" + text[-(char_budget // 2):]
```

---

### Day 5 (April 11): Self-Correction Hardening + First Baseline

**Goal:** Self-correction handles all 4 failure types with diagnosis. First baseline score from harness. AGENT.md with real schema descriptions. Corrections log started.

#### Task 7: Implement full 4-type failure diagnosis in SelfCorrector

**File:** `agent/self_corrector.py`

- [ ] Implement `diagnose_failure()` — categorizes error into one of 4 types:

```python
def diagnose_failure(self, error: str, query: str) -> str:
    """Categorize failure type to choose correct fix strategy."""
    error_lower = error.lower()
    if any(k in error_lower for k in ["syntax error", "parse error", "unexpected token"]):
        return "syntax_error"
    if any(k in error_lower for k in ["table", "relation", "collection", "does not exist"]):
        return "wrong_table"
    if any(k in error_lower for k in ["type mismatch", "cannot cast", "operator does not exist"]):
        return "join_key_format"
    if any(k in error_lower for k in ["no results", "empty", "null"]):
        return "domain_knowledge_gap"
    return "unknown"
```

- [ ] Implement `get_fix_strategy()` — maps failure type to specific correction approach:

```python
def get_fix_strategy(self, failure_type: str, error: str, schema: str) -> str:
    strategies = {
        "syntax_error": f"Fix SQL/query syntax. Error: {error}",
        "wrong_table": f"Check schema for correct table/collection names.\nSchema:\n{schema}",
        "join_key_format": "Normalize join key types (e.g., cast integer to varchar or vice versa)",
        "domain_knowledge_gap": "Check domain KB for correct field values, status codes, or fiscal periods",
        "unknown": f"Analyze error and regenerate query. Error: {error}"
    }
    return strategies[failure_type]
```

- [ ] Update `self_correct()` to use diagnosis before calling LLM
- [ ] Update `self_correct` prompt in PromptLibrary to include fix strategy

#### Task 8: Draft AGENT.md with real schema (Context Layer 1)

**File:** `agent/AGENT.md`

- [ ] Create AGENT.md with this structure (fill in real schema from DAB datasets):

```markdown
# Oracle Forge Agent — Context File

## Role
You are a data analytics agent. You answer questions by querying across multiple databases.
Always return structured output with a query trace. Never fabricate data.

## Available Tools (via MCP Toolbox at localhost:5000)
- `execute_postgresql`: Run SQL against PostgreSQL databases
- `execute_sqlite`: Run SQL against SQLite databases
- `execute_mongodb`: Run aggregation pipeline against MongoDB
- `execute_duckdb`: Run analytical SQL against DuckDB

## Database Schemas

### PostgreSQL — Yelp Dataset
[Paste real schema here after loading DAB datasets]
Tables: business(id, name, city, state, stars, review_count), review(id, business_id, user_id, stars, text, date), ...

### SQLite — [Dataset name]
[Paste real schema here]

### MongoDB — [Dataset name]
Collections: [list with fields]

### DuckDB — [Dataset name]
[Paste real schema here]

## Behavioral Rules
1. Always generate a query trace — never return an answer without it
2. Self-correct on execution failure — retry up to 3 times with diagnosis
3. If a join spans databases, normalize key formats before merging
4. For free-text fields (reviews, notes), extract structured data before calculation
5. If you cannot answer, say so explicitly — do not fabricate

## Domain Knowledge References
See: kb/domain/domain_knowledge.md (injected as Context Layer 2)

## Corrections Log Reference
See: kb/corrections/corrections.md (injected as Context Layer 3)
Past failures and fixes are recorded there. Consult before attempting complex queries.
```

#### Task 9: Start corrections log

**File:** `kb/corrections/corrections.md`

- [ ] Create corrections log format and add first entries from test failures:

```markdown
# Corrections Log — Oracle Forge

Format: [Query] → [What went wrong] → [Correct approach] → [Date]

---

## Entry 001
**Query:** "How many 5-star Yelp businesses are in San Francisco?"
**What went wrong:** [fill from actual test failure]
**Correct approach:** [fill from fix applied]
**Date:** 2026-04-11
```

#### Task 10: Coordinate paired evaluation with Driver 1

- [ ] Run first 10-15 DAB queries through the agent end-to-end
- [ ] Log pass/fail for each in `eval/score_log.md`:

```markdown
# Score Log

## Baseline — Day 5 (2026-04-11)
- Queries run: 15
- Pass: X
- Fail: Y
- pass@1: Z%

### Failed queries:
- Query ID X: [what failed, which DB type]
```

- [ ] Identify top 3 failure patterns and add to corrections log

---

### Day 6 (April 12): Three-Layer Context Architecture

**Goal:** All three context layers working, injected at session start, referenced in all prompts. Worth 20% of grade.

#### Task 11: Implement full ContextManager

**File:** `agent/context_manager.py`

- [ ] Add session memory tracking:

```python
def add_to_session(self, query: str, result: str, correction: Optional[str] = None):
    self._session_history.append({
        "query": query,
        "result_summary": result[:200],
        "correction": correction,
        "timestamp": datetime.utcnow().isoformat()
    })
    # Keep only last 10 interactions to manage tokens
    self._session_history = self._session_history[-10:]

def get_session_context(self) -> str:
    if not self._session_history:
        return ""
    items = [f"- {h['query']}: {h['result_summary']}" for h in self._session_history[-5:]]
    return "## Recent Session Queries\n" + "\n".join(items)
```

- [ ] Add `append_correction()` — the self-learning feedback loop:

```python
def append_correction(self, query: str, what_went_wrong: str, correct_approach: str):
    """Automatically writes new correction to the corrections log."""
    entry = f"\n---\n\n## Entry {self._next_entry_id()}\n**Query:** {query}\n**What went wrong:** {what_went_wrong}\n**Correct approach:** {correct_approach}\n**Date:** {datetime.utcnow().date()}\n"
    with open(self.corrections_path, "a") as f:
        f.write(entry)
```

- [ ] Wire `append_correction()` into SelfCorrector — call it when self-correction succeeds

#### Task 12: Integrate Context Layer 2 from Intelligence Officers

- [ ] Coordinate with Intelligence Officers: request their KB v2 documents (domain terms, fiscal calendar conventions, status code meanings, ill-formatted join key glossary)
- [ ] Ensure `domain/domain_knowledge.md` is populated with their content
- [ ] Verify ContextManager's `_load_layer2_domain()` reads this correctly

#### Task 13: Update all prompts to reference three-layer context

- [ ] Update `intent_analysis` prompt to mention: "Consult the domain knowledge in your context for any ambiguous terms"
- [ ] Update `self_correct` prompt to mention: "Check the corrections log in your context before generating a fix"
- [ ] Test full flow: ask a query that was in the corrections log → verify agent avoids the same mistake

---

### Day 7 (April 13-14): Logging + Interim Submission

**Goal:** Full audit trail logging. README and documentation complete. Interim submission checklist satisfied by April 14, 21:00 UTC.

#### Task 14: Comprehensive logging in AgentCore

- [ ] Log a structured JSON object per run to `eval/run_logs/`:

```python
import json, os
from datetime import datetime

def _log_run(self, request: QueryRequest, response: AgentResponse, intent: dict,
             sub_queries: list, self_corrections: list):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": request.question,
        "identified_databases": intent.get("target_databases", []),
        "sub_queries": [sq.model_dump() for sq in sub_queries],
        "self_corrections": self_corrections,
        "answer": response.answer,
        "confidence": response.confidence,
        "error": response.error
    }
    os.makedirs("eval/run_logs", exist_ok=True)
    fname = f"eval/run_logs/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(log_entry, f, indent=2)
```

#### Task 15: Polish prompts and document improvements

- [ ] Re-run 10-15 test queries and compare pass rate vs. Day 5 baseline
- [ ] Update `eval/score_log.md` with Day 7 scores
- [ ] Update corrections log with any new failures found

#### Task 16: Verify interim submission checklist

Check each item from the challenge document:
- [ ] README.md at root — team info, architecture, setup instructions, server link
- [ ] agent/ — AGENT.md, all source files, requirements.txt, tools.yaml
- [ ] kb/ — architecture/, domain/, corrections/ with CHANGELOG.md in each
- [ ] eval/ — harness source, initial score log with first-run baseline
- [ ] planning/ — AI-DLC Inception document with approval records (date, who approved, hardest question)
- [ ] utils/ — minimum 3 reusable modules with README and tests
- [ ] signal/ — engagement_log.md with Week 8 post links
- [ ] Agent running on shared server, handling ≥2 DB types

---

### Day 8 (April 15): Adversarial Probes + Prompt Refinement

**Goal:** Fix failures from Intelligence Officers' adversarial probe library. Update corrections log.

#### Task 17: Run and respond to adversarial probes

For each failed probe (coordinate with Intelligence Officers who own probe library):
- [ ] Read `probes/probes.md` — identify which probes target Driver 2 areas (prompt/context failures vs. infra failures)
- [ ] For each failing probe: trace the query log, identify root cause, update prompt or corrections log
- [ ] Document each fix in `probes/probes.md` standard format:

```markdown
## Probe 001
**Query:** [exact query]
**Failure category:** multi-database-routing | ill-formatted-key | unstructured-text | domain-knowledge-gap
**Expected failure:** [what the probe was designed to trigger]
**Observed failure:** [what actually failed]
**Fix applied:** [prompt change / corrections log entry / context update]
**Post-fix score:** [pass | fail]
```

**Probe types to focus on (from Internal Probing Strategy doc):**
- **Provenance probes**: Does the agent correctly attribute results to the right database? (Not conflating MongoDB data with PostgreSQL data)
- **Boundary probes**: Does the agent correctly say "I cannot answer" vs. fabricating? Test edge cases like empty results
- **Behavioral signal probes**: Does the agent use the corrections log when it should? Run a query it previously failed → verify it changes behavior
- **Architecture disclosure**: Does the agent's query trace accurately reflect what it actually did?

#### Task 18: Verify self-learning loop

- [ ] Re-run 3 queries that previously failed after corrections log update
- [ ] Confirm agent now passes them (or at least uses different strategy)
- [ ] Document evidence in `kb/corrections/CHANGELOG.md`:

```markdown
# Corrections KB CHANGELOG

## v3 — 2026-04-15
- Added 5 new entries from adversarial probe failures
- Agent now correctly normalizes integer/string join keys (verified: Probe 003 now passes)
- Added fiscal calendar convention (Q4 starts October) — resolves domain gap probes
```

---

### Day 9 (April 16): Benchmark + Final Polish

**Goal:** Full DAB benchmark run complete. Final score logged.

#### Task 19: Finalize AGENT.md for benchmark submission

- [ ] Update AGENT.md with:
  - Final architecture description (what was built, key design decisions)
  - What worked (multi-pass self-correction, three-layer context)
  - What did not work (be honest — graders expect this)
  - Final pass@1 score

#### Task 20: Update score log with final run

- [ ] `eval/score_log.md` must show minimum two data points:

```markdown
## Score Progression
| Run | Date | Queries | pass@1 | Notes |
|-----|------|---------|--------|-------|
| Baseline | 2026-04-11 | 15 | X% | First end-to-end run, 2 DB types |
| Interim | 2026-04-14 | 30 | Y% | All 4 DB types, corrections log active |
| Final | 2026-04-16 | 54 | Z% | Full DAB benchmark, 5 trials each |
```

#### Task 21: Review entire kb/ directory

- [ ] Each subdirectory must have a `CHANGELOG.md` and injection test evidence:
  - `kb/architecture/CHANGELOG.md`
  - `kb/domain/CHANGELOG.md`
  - `kb/corrections/CHANGELOG.md`
  - `kb/evaluation/CHANGELOG.md`
- [ ] "Injection test evidence" = a log showing the context was loaded into the agent (the run logs prove this)

---

### Day 10 (April 17): Demo + Final Submission

**Goal:** Demo video recorded. All docs finalized. Submission complete by April 18, 21:00 UTC.

#### Task 22: Demo prep

The demo (max 8 minutes) must show:
- [ ] Agent on shared server answering 2+ DAB queries spanning different DB types
- [ ] Self-correction in action — show a query fail, agent diagnoses and recovers
- [ ] Context layers working — agent uses KB domain knowledge to resolve an ambiguous term
- [ ] Evaluation harness producing a score with query trace
- [ ] Brief walkthrough of adversarial probe library

#### Task 23: AI-DLC Operations document

**File:** `planning/operations_v1.md`

- [ ] Write what was built, what changed from the inception plan, what the harness score is, what the next sprint's Inception should address

#### Task 24: Final submission checklist

- [ ] README.md updated with video link and final benchmark score
- [ ] `results/` directory: DAB results JSON, PR link, score log, leaderboard screenshot
- [ ] Benchmark PR submitted to ucbepic/DataAgentBench (PR title: "[Team Name] — TRP1 FDE Programme, April 2026")
- [ ] All four KB subdirectories reviewed with CHANGELOGs

---

## Verification

**End-to-end test flow:**
```bash
# 1. Start MCP Toolbox (Driver 1)
./toolbox --config mcp/tools.yaml

# 2. Run single query through agent
python eval/run_query.py --dataset yelp --query 0

# 3. Inspect output — must include answer + query_trace + confidence
cat eval/run_logs/<latest>.json | python3 -m json.tool

# 4. Run evaluation harness
python eval/run_benchmark.py --agent agent.agent_core --trials 5 --output results/team_results.json

# 5. Compute score
python eval/score.py --results results/team_results.json

# 6. Verify context layers loaded
grep "Domain Knowledge" eval/run_logs/<latest>.json  # Layer 2 should appear in trace
grep "Corrections" eval/run_logs/<latest>.json        # Layer 3 should appear
```

**Key milestones to hit:**
- Day 3 EOD: Agent answers at least 1 Yelp query end-to-end
- Day 5 EOD: Baseline score logged, self-correction handles all 4 failure types
- Day 6 EOD: All 3 context layers injected and verified in run logs
- **April 14 21:00 UTC: Interim submission live**
- Day 9 EOD: Full DAB benchmark score recorded
- **April 18 21:00 UTC: Final submission live**
