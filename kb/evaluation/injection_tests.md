# Injection Tests — kb/evaluation/

**Protocol:** Each document was injected into a fresh LLM session (no other context). A question was asked that the document should answer. All tests run against `google/gemini-2.0-flash-001` via OpenRouter.

---

## Test 1 — `dab_read.md`

**Document injected:** `kb/evaluation/dab_read.md`

**Question asked:**
> What is the minimum number of trials per query required for a valid DAB submission, and what does pass@1 mean in this context?

**Expected answer:**
Minimum 5 trials per query (n ≥ 5). Pass@1 means the agent must return the correct answer on its **first attempt** within each trial — there is no partial credit. The reported score is the fraction of queries passed across all trials. Retries within a single trial do not count as a first attempt.

**Result:** PASS — LLM returned 5 trials minimum, correctly defined pass@1 as first-attempt success only.

---

## Test 2 — `dab_read.md` (submission format)

**Document injected:** `kb/evaluation/dab_read.md`

**Question asked:**
> How do teams submit DAB benchmark results, and what must the PR include?

**Expected answer:**
Results are submitted as a GitHub Pull Request to `ucbepic/DataAgentBench`. The PR must include: (1) a results JSON file at `submission/team_[name]_results.json`, (2) an `AGENT.md` describing the agent architecture, key design decisions, what worked, and what did not. PR title format: `[Team Name] — TRP1 FDE Programme, April 2026`.

**Result:** PASS — LLM gave the correct repository, file path, and PR title format.

---

## Test 3 — `scoring_method.md`

**Document injected:** `kb/evaluation/scoring_method.md`

**Question asked:**
> What is the current best pass@1 score on DAB, and which system achieved it?

**Expected answer:**
38% pass@1, achieved by PromptQL + Gemini. This is the baseline to beat. The gap between this score and 100% represents the engineering problem — not a model capability ceiling but a context and execution reliability problem.

**Result:** PASS — LLM returned 38% and PromptQL + Gemini as the current leader.

---

## Test 4 — `ddb_read.md`

**Document injected:** `kb/evaluation/ddb_read.md`

**Question asked:**
> What float tolerance does the DAB evaluation use when comparing numeric answers?

**Expected answer:**
±0.01 tolerance for floating point comparisons. An answer of 4.25 passes if the expected answer is anywhere in [4.24, 4.26].

**Result:** PASS — LLM stated ±0.01 tolerance correctly.