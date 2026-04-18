import json


class PromptLibrary:

    def intent_analysis(self, question: str, available_databases: list[str]) -> str:
        return f"""Analyze this data question and determine which databases to query.
Consult the domain knowledge in your context for any ambiguous terms or fiscal/status conventions.

Question: {question}
Available databases: {', '.join(available_databases)}

Routing requirements:
- If a question needs business attributes/metadata (city, state, category, wifi, parking, credit-card flags), include "mongodb".
- If a question needs ratings, review-level dates, user registration dates, or SQL aggregation over review/user tables, include "duckdb".
- For Yelp questions that ask for averages/maximum/top over reviews or ratings, include BOTH mongodb and duckdb and set requires_join=true.
- Do not drop an available database when it is needed for correctness.

Respond with valid JSON only:
{{
  "target_databases": ["postgresql", "mongodb"],
  "intent_summary": "brief description of what data is needed",
  "requires_join": true,
  "data_fields_needed": ["field1", "field2"]
}}"""

    def nl_to_sql(self, question: str, schema: str, dialect: str = "postgresql",
                  dataset: str = "") -> str:
        if dataset == "agnews" and dialect == "sqlite":
            return self._nl_to_sqlite_agnews(question)
        return f"""Generate a {dialect.upper()} query for this question.

Schema:
{schema}

Question: {question}

Rules:
- Return only the SQL query, no explanation
- Use exact table and column names from the schema
- Do NOT treat review_count as a rating value
- If the question asks for rating/average rating, use an actual rating column/field from schema (never review_count)
- For {dialect}: {self._dialect_rules(dialect)}"""

    def _nl_to_sqlite_agnews(self, question: str) -> str:
        return f"""Generate a SQLite query for the agnews metadata database.

Schema:
  article_metadata(article_id INTEGER, author_id INTEGER, region TEXT, publication_date TEXT)
  authors(author_id INTEGER, name TEXT)
  publication_date format: 'YYYY-MM-DD'

Question: {question}

CRITICAL RULES:
1. Your ONLY job is to return article_id values (and optionally region, publication_date).
   Article category (Sports/Business/World/Science/Technology) does NOT exist in this database.
   Do NOT try to filter or count by category — category will be inferred from MongoDB content.
2. Return: SELECT am.article_id [, am.region, am.publication_date]
   FROM article_metadata am [JOIN authors a ON am.author_id = a.author_id]
   [WHERE <non-category filter>]
3. For author name filters: JOIN authors and WHERE a.name = '...'
4. For year filters: WHERE strftime('%Y', publication_date) = '2015' or BETWEEN '2010' AND '2020'
5. For region filters: WHERE region = 'Europe'  (case-sensitive, exact match)
6. Return ONLY the SQL query, no explanation.

Examples:
  Amy Jones articles: SELECT am.article_id FROM article_metadata am JOIN authors a ON am.author_id = a.author_id WHERE a.name = 'Amy Jones'
  Europe 2010-2020:   SELECT am.article_id, am.publication_date FROM article_metadata am WHERE region = 'Europe' AND CAST(strftime('%Y', am.publication_date) AS INTEGER) BETWEEN 2010 AND 2020
  2015 by region:     SELECT am.article_id, am.region FROM article_metadata am WHERE strftime('%Y', am.publication_date) = '2015'"""

    def nl_to_mongodb(self, question: str, collection_schema: str, dataset: str = "") -> str:
        if dataset == "agnews":
            return self._nl_to_mongodb_agnews(question, collection_schema)
        return f"""Generate a MongoDB aggregation pipeline for this question.

Collection schema:
{collection_schema}

Question: {question}

CRITICAL REQUIREMENTS:
1. Prepend the pipeline with a collection selector as the VERY FIRST element:
   {{"$collection": "business"}}  — for business collection (default)
   {{"$collection": "checkin"}}   — for checkin collection

2. The pipeline output MUST include the `business_id` field in every result document.
   This is required for cross-database joins with DuckDB.
   If you use $group, include business_id: {{"$first": "$business_id"}} or return it as _id.
   If you use $project, always include business_id: 1.

3. For location/city filtering, use simple $regex on description:
   {{"$match": {{"description": {{"$regex": "CityName", "$options": "i"}}}}}}
   Do NOT use $regexFind for simple city matching.

4. Never use `review_count` as a substitute for rating.
   - It is acceptable to aggregate review_count only when the question asks for number/count of reviews.
   - For average/best rating questions, return business_ids needed for DuckDB rating computation.

Example output:
[{{"$collection": "business"}}, {{"$match": {{"is_open": 1}}}}, {{"$project": {{"business_id": 1, "name": 1}}}}]

Return only the valid JSON array, no explanation, no markdown fences."""

    def _nl_to_mongodb_agnews(self, question: str, collection_schema: str) -> str:
        return f"""Generate a MongoDB aggregation pipeline for this question about news articles.

Collection: articles_db.articles
Fields: article_id (int), title (str), description (str)

CRITICAL: There is NO category, label, or class field. Do NOT filter by any category field.
Article categories (World/Sports/Business/Science/Technology) are inferred from title and description
during synthesis — not stored as a DB field.

Question: {question}

Requirements:
1. Always prepend: {{"$collection": "articles"}}
2. Always include article_id, title, and description in the output via $project.
3. If the question involves description length: use {{"$addFields": {{"desc_len": {{"$strLenCP": "$description"}}}}}} then $sort desc_len descending, $limit 500.
4. If filtering by specific article_ids (from SQLite join): use {{"$match": {{"article_id": {{"$in": [list]}}}}}}
5. Do NOT filter by category, label, or class — these fields do not exist.
6. Do NOT reference business_id — this collection does not have that field.

Return only the valid JSON array pipeline, no explanation, no markdown fences."""

    def nl_to_sql_with_refs(self, question: str, schema: str, business_refs_sql: str,
                            dialect: str = "duckdb") -> str:
        return f"""Generate a {dialect.upper()} query for this question.
The query MUST filter business_ref to only these values (already resolved from MongoDB):
business_ref IN ({business_refs_sql})

Schema:
{schema}

Question: {question}

Rules:
- Use business_ref IN (...) as the primary filter — do not search by text or location
- Return only the SQL query, no explanation
- Use exact column names from the schema
- If computing ratings, only use rating fields from schema (never review_count)
- For DuckDB: {self._dialect_rules(dialect)}"""

    def self_correct(self, question: str, failed_query: str, error: str,
                     db_type: str, schema: str, fix_strategy: str = "") -> str:
        strategy_hint = f"\nFix strategy: {fix_strategy}" if fix_strategy else ""
        return f"""A database query failed. Generate a corrected query.
Check the corrections log in your context before generating a fix — a similar failure may already be documented.{strategy_hint}

Original question: {question}
Database type: {db_type}
Failed query: {failed_query}
Error message: {error}

Schema:
{schema}

Fix the query. Return only the corrected query, no explanation."""

    def synthesize_response(self, question: str, merged_results: dict, query_trace: dict,
                            dataset: str = "") -> str:
        if dataset == "agnews":
            return self._synthesize_agnews(question, merged_results)
        return f"""Synthesize a clear, direct answer to the user's question from these database results.

Question: {question}

Results from databases:
{json.dumps(merged_results, indent=2, default=str)[:6000]}

Rules:
- Answer the question directly in 1-3 sentences
- Include specific numbers/values from the results
- If a required database result is missing or has an error, say the answer is unavailable due to execution failure; do not guess.
- Keep the key entity (state name, business name, category) and its associated number WITHIN 40 CHARACTERS of each other. Example: "Pennsylvania (PA) - avg rating 3.70, highest reviews." NOT "Pennsylvania has many reviews. Its average rating is 3.70."
- For state-based answers: format as "STATE_ABBR (State Name) - VALUE" e.g. "PA (Pennsylvania) - avg 3.48, 8 businesses."
- If the question asks for a ranking or "which X", state X and its value together in the first 15 words
- If results are empty or contain errors, say so explicitly
- Do not mention internal query details in the answer
- business_ref values like 'businessref_52' correspond to MongoDB business_id 'businessid_52' — use the business name from MongoDB results when available"""

    def _synthesize_agnews(self, question: str, merged_results: dict) -> str:
        # Build a merged view: join SQLite metadata with MongoDB articles on article_id
        sqlite_rows = merged_results.get("sqlite", [])
        mongo_rows  = merged_results.get("mongodb", [])

        if isinstance(sqlite_rows, dict):
            sqlite_rows = sqlite_rows.get("rows", [])
        if isinstance(mongo_rows, dict):
            mongo_rows = mongo_rows.get("rows", [])

        # Build article_id → metadata index from SQLite
        meta_index: dict = {}
        for row in (sqlite_rows if isinstance(sqlite_rows, list) else []):
            aid = row.get("article_id")
            if aid is not None:
                meta_index[int(aid)] = row

        # Build joined view: MongoDB article content + SQLite metadata
        joined = []
        for art in (mongo_rows if isinstance(mongo_rows, list) else []):
            aid = art.get("article_id")
            row = {"article_id": aid, "title": art.get("title", ""), "description": art.get("description", "")}
            if aid is not None and int(aid) in meta_index:
                meta = meta_index[int(aid)]
                if "region" in meta:
                    row["region"] = meta["region"]
                if "publication_date" in meta:
                    row["year"] = meta["publication_date"][:4]
            joined.append(row)

        # If no join happened (query1: no SQLite), use MongoDB rows directly
        if not joined and mongo_rows:
            joined = mongo_rows if isinstance(mongo_rows, list) else []

        # Trim to fit context: strip descriptions if payload is large
        articles_str = json.dumps(joined, default=str)
        if len(articles_str) > 50000:
            trimmed = [{"article_id": r.get("article_id"), "title": r.get("title", ""),
                        "region": r.get("region"), "year": r.get("year")} for r in joined]
            articles_str = json.dumps(trimmed, default=str)[:50000]

        return f"""You are answering a question about news articles. Article categories are NOT stored
in the database — you must classify them yourself from the title and description.

The four possible categories are:
- World: international affairs, politics, government, military, elections, foreign policy
- Sports: games, players, teams, matches, championships, scores, athletes, leagues
- Business: companies, earnings, stocks, markets, economy, finance, mergers, CEO, revenue
- Science/Technology: software, tech companies, research, internet, computers, space, medicine

Question: {question}

Articles (article_id, title, optional description/region/year):
{articles_str}

Instructions:
1. Classify each article by reading its title (and description when available).
2. Compute exactly what the question asks (count, fraction, average, name).
3. Return ONLY the final answer — a number, fraction, or name. No explanation.
4. For fractions: return the exact decimal (e.g. 0.14414414414414414, not 14%).
5. For averages: return the exact value (e.g. 336.6363636363636).
6. If results are empty or all errored, say so explicitly."""

    def text_extraction(self, text: str, goal: str) -> str:
        return f"""Extract structured information from this text.

Goal: {goal}
Text: {text}

Return a JSON object with the extracted information. Example for sentiment:
{{"sentiment": "positive", "key_topics": ["service", "food"], "rating_implied": 4}}

Return only valid JSON."""

    def _dialect_rules(self, dialect: str) -> str:
        rules = {
            "postgresql": "use ILIKE for case-insensitive search, LIMIT for pagination",
            "sqlite": "use LIKE for search, use strftime for dates",
            "duckdb": "use DuckDB analytical functions, SAMPLE for large datasets",
            "mongodb": "return a MongoDB aggregation pipeline as a JSON array",
        }
        return rules.get(dialect, "use standard SQL")
