# Injection Tests — kb/domain/

**Protocol:** Each document was injected into a fresh LLM session (no other context). A question was asked that the document should answer. All tests run against `google/gemini-2.0-flash-001` via OpenRouter.

---

## Test 1 — `domain_knowledge.md` (active business + WiFi)

**Document injected:** `kb/domain/domain_knowledge.md`

**Question asked:**
> A query asks for "active businesses in Las Vegas with WiFi." What are the three domain rules the agent must apply, and which fields/collections are involved?

**Expected answer:**
1. "Active" = `is_open == 1` AND reviewed in last 12 months — JOIN to DuckDB review table on `business_ref`
2. "Las Vegas" = `{$match: {description: {$regex: "Las Vegas", $options: "i"}}}` on MongoDB `business.description`
3. "WiFi" = `attributes.WiFi` NOT IN `[null, "u'no'", "no", "None"]` on MongoDB `business.attributes`

All three filters apply to the MongoDB `business` collection before the cross-DB join to DuckDB.

**Result:** PASS — LLM applied all three rules with correct field names and MongoDB filter syntax.

---

## Test 2 — `domain_knowledge.md` (date parsing)

**Document injected:** `kb/domain/domain_knowledge.md`

**Question asked:**
> A DuckDB query needs to filter reviews from 2018. What is the safe approach for date filtering?

**Expected answer:**
`review.date` has mixed formats including `"August 01, 2016 at 03:44 AM"`, `"29 May 2013, 23:01"`, and ISO format. Never use `strptime()` with a fixed format string. For year-only filtering, use `LIKE '%2018%'` as the safe fallback, or `TRY_STRPTIME` with `COALESCE` over multiple known format strings.

**Result:** PASS — LLM rejected fixed strptime and recommended `LIKE '%2018%'`.

---

## Test 3 — `join_keys_glossary.md`

**Document injected:** `kb/domain/join_keys_glossary.md`

**Question asked:**
> A MongoDB query returns `businessid_42`. What is the corresponding value in DuckDB's review table?

**Expected answer:**
`businessref_42` — strip the `businessid_` prefix, keep the numeric suffix `42`, prepend `businessref_`. The numeric suffix is identical across both databases.

**Result:** PASS — LLM returned `businessref_42` and described the prefix-swap rule correctly.

---

## Test 4 — `yelp_schema.md`

**Document injected:** `kb/domain/yelp_schema.md`

**Question asked:**
> Does the DuckDB Yelp database have a business table? Where is business data stored?

**Expected answer:**
No. DuckDB (`yelp_user.db`) contains only `review`, `user`, and `tip` tables. Business data (name, location, attributes, categories, is_open) is in the MongoDB `business` collection. Any query requiring business attributes must route to MongoDB first.

**Result:** PASS — LLM correctly stated DuckDB has no business table and identified MongoDB as the source.

---

## Test 5 — `domain_knowledge.md` (repeat customer)

**Document injected:** `kb/domain/domain_knowledge.md`

**Question asked:**
> What is the correct definition of "repeat customer" in the Yelp dataset, and why is the naive definition wrong?

**Expected answer:**
Correct: a user who reviewed businesses in the **same category** more than once. Requires category extraction from `business.description`, then GROUP BY `user_id + category`.

Naive (wrong): any user with more than one review total. Wrong because a user reviewing a restaurant and a gym is not a repeat customer of either — they are an active reviewer, not a repeat customer of any category.

**Result:** PASS — LLM stated the category-specific definition and explained why total review count is incorrect.