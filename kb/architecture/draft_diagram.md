# Oracle Forge — Architecture Diagrams

---

## Diagram 1 — Main Agent Pipeline

```mermaid
flowchart TD
    %% Global Node Styles
    classDef default fill:#2d2d2d,stroke:#888,stroke-width:1px,color:#ffffff;

    %% Functional Group Styles
    classDef entryExit fill:#1a3a3a,stroke:#00f2ff,stroke-width:2px,color:#ffffff;
    classDef logic fill:#2d2d2d,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef contextNode fill:#0d1b2a,stroke:#3a86ff,stroke-width:2px,color:#ffffff;
    classDef database fill:#1b2e1b,stroke:#4caf50,stroke-width:2px,color:#ffffff;
    classDef error fill:#3a1a1a,stroke:#ff5252,stroke-width:2px,color:#ffffff;

    %% Subgraph Styling (This fixes the gray box)
    style CTX fill:#121212,stroke:#3a86ff,stroke-width:2px,color:#ffffff,stroke-dasharray: 5 5

    U([User Question]) --> SM
    class U entryExit;

    SM["StateManager\nConversation history · token-bounded truncation"] --> CM
    class SM logic;

    subgraph CTX ["Context Layers"]
        L1["Layer 1 — agent/AGENT.md\nSchemas · join rules · behavioral rules"]
        L2["Layer 2 — kb/domain/\nDomain terms · attribute rules"]
        L3["Layer 3 — kb/corrections/\n32 failures → fixes · self-learning loop"]
    end
    class L1,L2,L3 contextNode;

    CTX --> CM["ContextManager\nAssembles 3 layers within token budget"]
    CM --> PL["PromptLibrary\nintent_analysis · nl_to_sql · nl_to_mongodb · self_correct · synthesize"]
    PL --> AI["analyze_intent() → LLM\ntarget_databases · requires_join · join_direction"]
    AI --> DQ["decompose_query()\nSubQuery per database"]
    DQ --> DR["DatabaseRouter\nRoutes each SubQuery to correct DB type"]
    DR --> QE["QueryExecutor → MCP Toolbox · localhost:5000"]
    class CM,PL,AI,DQ,DR,QE logic;

    QE --> MG[(MongoDB\nbusiness · review · user · tip)]
    QE --> DK[(DuckDB\nreview · user · tip)]
    QE --> PG[(PostgreSQL\nbooks_info)]
    QE --> SL[(SQLite\nreview)]
    class MG,DK,PG,SL database;

    QE -- on failure --> SC["SelfCorrector\nsyntax_error · wrong_table\njoin_key_format · domain_knowledge_gap\nretry max 3×"]
    SC -- corrected query --> QE
    SC -- append failure+fix --> L3
    class SC error;

    MG & DK & PG & SL --> JK["join_key_resolver\nbusinessid_N ↔ businessref_N\nmongodb_first · duckdb_first"]
    JK --> PP["Python Post-processing\nstate · category extraction via regex"]
    PP --> RS["ResponseSynthesizer\nanswer · confidence · QueryTrace"]
    class JK,PP,RS logic;

    RS --> ANS([Answer to User])
    RS --> LOG["eval/run_logs/timestamp.json"]
    LOG -- score_log.md update --> L3
    class ANS entryExit;
    class LOG logic;
```

---

## Diagram 2 — Three-Layer Context Assembly

How `ContextManager` builds the prompt context window before every LLM call, respecting the token budget.

```mermaid
flowchart LR
    classDef layer fill:#0d1b2a,stroke:#3a86ff,stroke-width:2px,color:#ffffff;
    classDef file  fill:#1e1e1e,stroke:#888,stroke-width:1px,color:#cccccc;
    classDef gate  fill:#2d2d2d,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef out   fill:#1a3a3a,stroke:#00f2ff,stroke-width:2px,color:#ffffff;

    subgraph L1 ["Layer 1 — Schema & Rules (always loaded)"]
        direction TB
        F1A["agent/AGENT.md\nDB schemas · tool names\ncritical routing rules\ndate format specs"]
    end
    class F1A file;

    subgraph L2 ["Layer 2 — Domain Knowledge (loaded if budget allows)"]
        direction TB
        F2A["kb/domain/domain_knowledge.md\nbusiness term definitions\nattribute parsing rules"]
        F2B["kb/domain/domain_terms.md\nchurn · active account\nfiscal quarter boundaries"]
        F2C["kb/domain/join_keys_glossary.md\nbusinessid_N ↔ businessref_N\nformat resolution rules"]
    end
    class F2A,F2B,F2C file;

    subgraph L3 ["Layer 3 — Corrections Log (loaded last, trimmed if over budget)"]
        direction TB
        F3A["kb/corrections/corrections_log.md\nCOR-001 … COR-032\nfailure → fix → post-fix score"]
    end
    class F3A file;

    L1 --> TB{"Token Budget\nCheck\n≤ 6,000 tokens"}
    L2 --> TB
    L3 --> TB
    class TB gate;

    TB -- within budget --> CTX["Full Context Window\nLayer 1 + Layer 2 + Layer 3"]
    TB -- over budget --> TRIM["Trim Layer 3\nKeep most recent N corrections\nuntil within budget"]
    TRIM --> CTX
    class CTX,TRIM out;

    CTX --> LLM["LLM Call\n(analyze_intent / nl_to_sql\nnl_to_mongodb / synthesize)"]
    class LLM gate;
```

---

## Diagram 3 — Self-Correction Loop

Detailed view of how `SelfCorrector` diagnoses failures and feeds the corrections log.

```mermaid
flowchart TD
    classDef logic  fill:#2d2d2d,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef error  fill:#3a1a1a,stroke:#ff5252,stroke-width:2px,color:#ffffff;
    classDef ok     fill:#1b2e1b,stroke:#4caf50,stroke-width:2px,color:#ffffff;
    classDef kb     fill:#0d1b2a,stroke:#3a86ff,stroke-width:2px,color:#ffffff;

    EX["QueryExecutor\nexecutes query via MCP"] --> RES{"Result OK?"}
    class EX logic;

    RES -- yes --> PASS(["Return result"])
    class PASS ok;

    RES -- no --> DIAG["SelfCorrector.diagnose(error_msg)"]
    class DIAG error;

    DIAG --> T1{"syntax_error?\n'syntax error at or near'\n'unexpected token'"}
    DIAG --> T2{"wrong_table?\n'Table does not exist'\n'Collection not found'"}
    DIAG --> T3{"join_key_format?\n'zero rows returned'\n'no matching documents'"}
    DIAG --> T4{"domain_knowledge_gap?\n'ambiguous term'\n'definition required'"}
    class T1,T2,T3,T4 error;

    T1 -- yes --> FIX1["Fix: strip code fences\nreturn raw SQL / pipeline only\ncheck for explanation text prefix"]
    T2 -- yes --> FIX2["Fix: reroute to correct DB\nconsult AGENT.md schema\nbusiness → MongoDB not DuckDB"]
    T3 -- yes --> FIX3["Fix: call join_key_resolver\nbusinessid_N ↔ businessref_N\nstrip prefix, match on integer N"]
    T4 -- yes --> FIX4["Fix: load Layer 2 KB\nlook up domain term definition\nreplace naive proxy with correct filter"]
    class FIX1,FIX2,FIX3,FIX4 logic;

    FIX1 & FIX2 & FIX3 & FIX4 --> RETRY{"Retry #\n≤ 3?"}

    RETRY -- yes --> EX
    RETRY -- no --> FAIL(["Return failure\n+ error trace"])
    class FAIL error;

    FIX1 & FIX2 & FIX3 & FIX4 --> LOG["Append to\nkb/corrections/corrections_log.md\nCOR-NNN entry"]
    class LOG kb;

    LOG --> NEXT["Loaded at next\nsession start\n→ agent doesn't repeat"]
    class NEXT kb;
```

---

## Diagram 4 — MCP Server and Database Layer

How `QueryExecutor` reaches all four database types through the custom MCP server.

```mermaid
flowchart LR
    classDef logic    fill:#2d2d2d,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef server   fill:#1a1a2e,stroke:#e94560,stroke-width:2px,color:#ffffff;
    classDef database fill:#1b2e1b,stroke:#4caf50,stroke-width:2px,color:#ffffff;
    classDef proto    fill:#2d2d2d,stroke:#888,stroke-width:1px,color:#aaaaaa;

    QE["QueryExecutor\nagent/query_executor.py"] -->|"JSON-RPC 2.0\nPOST /mcp"| MCP
    QE -->|"REST fallback\nPOST /v1/tools/{name}:invoke"| MCP

    subgraph MCP ["mcp/mcp_server.py — FastAPI · localhost:5000"]
        direction TB
        T1["postgres_query\nStructured transactional queries"]
        T2["mongo_aggregate\nAggregation pipelines"]
        T3["mongo_find\nSimple single-collection lookups"]
        T4["sqlite_query\nLightweight dataset queries"]
        T5["duckdb_query\nAnalytical queries"]
        T6["cross_db_merge\nJoin results across two DBs"]
    end
    class T1,T2,T3,T4,T5,T6 server;

    T1 -->|psycopg2| PG[(PostgreSQL\nbookreview · googlelocal\npancancer · patents)]
    T2 & T3 -->|pymongo| MG[(MongoDB\nyelp_businessinfo\nbusiness · checkin)]
    T4 -->|sqlite3| SL[(SQLite\nbookreview review_database\ndab_sqlite.db)]
    T5 -->|duckdb| DK[(DuckDB\nyelp_user\nreview · tip · user)]
    T6 -->|"Python merge\n+ join_key_resolver"| MR(["Merged Result\nset"])
    class PG,MG,SL,DK database;
    class MR logic;

    note1["Note: Google MCP Toolbox binary\nfails on this VPS — Snowflake CGO bug.\nmcp_server.py is the production replacement.\nExposes identical endpoints."]
    class note1 proto;
```

---

## Diagram 5 — Evaluation Harness and Score Loop

How a benchmark run flows from query input to score log update.

```mermaid
flowchart TD
    classDef logic   fill:#2d2d2d,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef file    fill:#1e1e1e,stroke:#888,stroke-width:1px,color:#cccccc;
    classDef ok      fill:#1b2e1b,stroke:#4caf50,stroke-width:2px,color:#ffffff;
    classDef fail    fill:#3a1a1a,stroke:#ff5252,stroke-width:2px,color:#ffffff;
    classDef entry   fill:#1a3a3a,stroke:#00f2ff,stroke-width:2px,color:#ffffff;

    CMD(["python eval/run_benchmark.py\n--dataset yelp --trials 5"]) --> LOAD
    class CMD entry;

    LOAD["Load DAB query set\neval/expected_answers.json\n54 queries across 12 datasets"] --> LOOP
    class LOAD logic;

    LOOP["For each query\n× N trials"] --> AGENT["AgentCore.run(question)\nFull pipeline execution"]
    class LOOP,AGENT logic;

    AGENT --> PRED["Predicted answer\n+ QueryTrace"]
    PRED --> CMP{"Match expected\nanswer?"}
    class PRED logic;

    CMP -- exact / fuzzy match --> PASS["pass = 1\nfor this trial"]
    CMP -- mismatch --> FFAIL["pass = 0\nlog failure trace"]
    class PASS ok;
    class FFAIL fail;

    PASS & FFAIL --> TLOG["eval/run_logs/\n<timestamp>.json\n{question, queries, result,\n expected, pass, trace}"]
    class TLOG file;

    TLOG --> SCORE["eval/score.py\npass@1 = passed_trials / total_trials"]
    class SCORE logic;

    SCORE --> SL["eval/score_log.md\nappend row:\ndate · dataset · passed · pass@1 · what changed"]
    class SL file;

    SL --> REGR{"Regression\ncheck:\npass@1 ≥ previous?"}
    class REGR logic;

    REGR -- yes --> GREEN(["Score improved\nor held — safe to merge"])
    REGR -- no --> RED(["Regression detected\ndo not merge\ndiagnose failure"])
    class GREEN ok;
    class RED fail;

    TLOG -- failures --> COR["Drivers add row to\nkb/corrections/corrections_log.md\nCOR-NNN"]
    COR --> KB["IOs review KB gaps\nupdate kb/architecture/\nor kb/domain/ docs"]
    class COR,KB file;
```

---

## Diagram 6 — Knowledge Base Structure and Maintenance Flow

How the KB is built, tested, and kept current by Intelligence Officers and Drivers.

```mermaid
flowchart TD
    classDef io      fill:#1a2a3a,stroke:#3a86ff,stroke-width:2px,color:#ffffff;
    classDef drv     fill:#2a1a2a,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef file    fill:#1e1e1e,stroke:#888,stroke-width:1px,color:#cccccc;
    classDef test    fill:#1b2e1b,stroke:#4caf50,stroke-width:2px,color:#ffffff;
    classDef inject  fill:#0d1b2a,stroke:#00f2ff,stroke-width:2px,color:#ffffff;

    subgraph KB ["kb/ — Knowledge Base"]
        direction TB

        subgraph V1 ["KB v1 — Architecture"]
            A1["claude_code_memory.md\nThree-layer MEMORY.md · autoDream"]
            A2["openai_data_agent_context.md\nSix-layer context · table enrichment"]
            A3["self_correction_loop.md\nFour-type diagnosis · retry pattern"]
            A4["dab_failure_modes.md\nFour hard requirements · failure taxonomy"]
        end

        subgraph V2 ["KB v2 — Domain"]
            D1["schema_overview.md\n12 datasets · DB type map"]
            D2["yelp_schema.md\nMongoDB + DuckDB field types\nsample values · join key formats"]
            D3["domain_knowledge.md\nActive business · high-rated\nWiFi values · parking regex"]
            D4["join_keys_glossary.md\nbusinessid_N ↔ businessref_N\nconfirmed format rules"]
        end

        subgraph V3C ["KB v3 — Corrections"]
            C1["corrections_log.md\nCOR-001 … COR-032\nfailure → fix → post-fix score"]
        end

        subgraph V3E ["KB v3 — Evaluation"]
            E1["scoring_method.md\npass@1 · trial requirements"]
            E2["dab_read.md\nDAB four hard requirements\n38% Gemini 3 Pro baseline"]
        end
    end

    class A1,A2,A3,A4,D1,D2,D3,D4,C1,E1,E2 file;

    IO["Intelligence Officers\nResearch · write · maintain"] -->|"new document"| KB
    class IO io;

    KB --> IT["Injection Test\n(Karpathy method)\nFresh LLM context\n+ only this document\n→ ask verification question"]
    class IT test;

    IT -- correct answer --> CHG["Update CHANGELOG.md\ndocument passes"]
    IT -- wrong answer --> REV["Revise or remove document\nuntil it passes"]
    class CHG,REV test;

    DRV["Drivers\nObserve failures → log"] -->|"new COR-NNN entry"| C1
    class DRV drv;

    C1 -->|"loaded at session start\nvia ContextManager"| AGT["Agent Context\nLayer 3 active"]
    class AGT inject;

    AGT --> IMP["Agent does not repeat\nlogged failure patterns"]
    class IMP inject;

    IO -->|"review C1 after each mob session"| KBUP["Update kb/architecture/\nor kb/domain/ docs\nif failure reveals KB gap"]
    class KBUP file;
```

---

## Diagram 7 — Public API and Deployment

How external traffic reaches the agent from any device.

```mermaid
flowchart LR
    classDef ext     fill:#1a3a3a,stroke:#00f2ff,stroke-width:2px,color:#ffffff;
    classDef tunnel  fill:#2d1a1a,stroke:#ff9800,stroke-width:2px,color:#ffffff;
    classDef api     fill:#2d2d2d,stroke:#bb86fc,stroke-width:2px,color:#ffffff;
    classDef agent   fill:#0d1b2a,stroke:#3a86ff,stroke-width:2px,color:#ffffff;

    USER(["Any device\n(browser / curl / facilitator)"])
    class USER ext;

    USER -->|"HTTPS"| CF["Cloudflare Tunnel\ncloudflared tunnel\n--url http://localhost:8080\nEphemeral public URL"]
    class CF tunnel;

    CF -->|"HTTP · localhost:8080"| API["api/server.py\nFastAPI\n\nPOST /query\n  {question, dataset}\n  → {answer, query_trace, confidence}\n\nGET /health\nGET /datasets"]
    class API api;

    API --> CORE["AgentCore.run()\nFull pipeline\n(Context → LLM → DB → Synthesize)"]
    class CORE agent;

    CORE --> MCP["mcp/mcp_server.py\nlocalhost:5000\nAll 4 DB types"]
    class MCP agent;

    API -->|"CORS: allow *"| USER
```
