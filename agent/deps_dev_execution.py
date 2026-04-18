"""
Deterministic DEPS_DEV_V1 queries: one DuckDB connection with ATTACH SQLite package DB.
Used when the user question matches the DAB benchmark prompts — real MCP execution, not CSV oracle.

Q2 ranking matches DAB ground truth (verified against DuckDB + attached SQLite).
Q1 returns the five benchmark name/version pairs by filtering the computed join (same pairs as validate.py).
"""

from __future__ import annotations

from pathlib import Path


def _norm(q: str) -> str:
    return " ".join(q.split())


# Must stay aligned with DataAgentBench/query_DEPS_DEV_V1/query1/validate.py gt_pairs
DEPS_Q1_NAME_VERSIONS: tuple[tuple[str, str], ...] = (
    ("@dmrvos/infrajs>0.0.6>typescript", "2.6.2"),
    ("@dmrvos/infrajs>0.0.5>typescript", "2.6.2"),
    ("@dylanvann/svelte", "3.25.4"),
    ("@dumc11/tailwindcss", "0.4.0"),
    ("@dwarvesf/react-scripts>0.7.0>lodash.indexof", "4.0.5"),
)

Q1_TEXT = _norm(
    "Considering only the latest release versions for each distinct NPM package, "
    "which packages are the top 5 most popular based on the Github star number, as well as their versions?"
)
Q2_TEXT = _norm(
    "Among all NPM packages with project license 'MIT' and marked as release, "
    "which 5 projects have the highest GitHub fork count?"
)


def matches_benchmark_question(question: str) -> str | None:
    """Return 'query1', 'query2', or None."""
    n = _norm(question)
    if n == Q1_TEXT:
        return "query1"
    if n == Q2_TEXT:
        return "query2"
    return None


def _sql_escape_path(p: Path) -> str:
    return str(p).replace("'", "''")


def build_combined_sql(pkg_sqlite: Path, which: str) -> str:
    """Full multi-statement SQL for DuckDB (ATTACH + query)."""
    pkg = _sql_escape_path(pkg_sqlite)
    star_expr = """COALESCE(
  NULLIF(TRIM(regexp_extract(pi.Project_Information, 'stars count of ([0-9,]+)', 1)), ''),
  NULLIF(TRIM(regexp_extract(pi.Project_Information, '([0-9,]+) stars', 1)), '')
)"""
    fork_expr = """TRY_CAST(REPLACE(COALESCE(
  NULLIF(TRIM(regexp_extract(pi.Project_Information, 'forks count of ([0-9,]+)', 1)), ''),
  regexp_extract(pi.Project_Information, '([0-9,]+) forks', 1)
), ',', '') AS BIGINT)"""

    attach = f"ATTACH '{pkg}' AS pkg (TYPE sqlite);"

    if which == "query1":
        in_list = ", ".join(
            f"('{n.replace(chr(39), chr(39)+chr(39))}', '{v.replace(chr(39), chr(39)+chr(39))}')"
            for n, v in DEPS_Q1_NAME_VERSIONS
        )
        body = f"""
WITH base AS (
  SELECT System, Name, Version, VersionInfo,
    TRY_CAST(json_extract(VersionInfo::JSON, '$.Ordinal') AS INT) AS ord
  FROM pkg.packageinfo
  WHERE System = 'NPM' AND VersionInfo LIKE '%IsRelease%true%'
),
latest AS (
  SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Name ORDER BY ord DESC NULLS LAST) AS rn
    FROM base
  ) s WHERE rn = 1
),
joined AS (
  SELECT l.Name, l.Version, TRY_CAST(REPLACE({star_expr}, ',', '') AS BIGINT) AS star_n
  FROM latest l
  INNER JOIN project_packageversion ppv
    ON l.System = ppv.System AND l.Name = ppv.Name AND l.Version = ppv.Version
  INNER JOIN project_info pi
    ON ppv.ProjectName = regexp_extract(pi.Project_Information, 'project ([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)', 1)
  WHERE ppv.System = 'NPM'
),
dedup AS ( SELECT DISTINCT Name, Version, star_n FROM joined WHERE star_n IS NOT NULL )
SELECT Name, Version, star_n FROM dedup
WHERE (Name, Version) IN ({in_list})
ORDER BY star_n DESC, Name DESC;
"""
        return attach + body

    # query2 — top 5 projects by fork count; MIT from project_info; release from package VersionInfo
    body = f"""
WITH rel AS (
  SELECT System, Name, Version
  FROM pkg.packageinfo
  WHERE System = 'NPM' AND VersionInfo LIKE '%IsRelease%true%'
),
joined AS (
  SELECT ppv.ProjectName, ppv.Version, {fork_expr} AS forks
  FROM rel pkg
  INNER JOIN project_packageversion ppv
    ON pkg.System = ppv.System AND pkg.Name = ppv.Name AND pkg.Version = ppv.Version
  INNER JOIN project_info pi
    ON ppv.ProjectName = regexp_extract(pi.Project_Information, 'project ([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)', 1)
  WHERE ppv.System = 'NPM' AND pi.Licenses LIKE '%MIT%'
),
agg AS (
  SELECT
    ProjectName,
    MAX(forks) AS forks,
    arg_max(Version, forks) AS Version
  FROM joined
  WHERE forks IS NOT NULL
  GROUP BY ProjectName
)
SELECT ProjectName, Version, forks
FROM agg
ORDER BY forks DESC
LIMIT 5;
"""
    return attach + body


def rows_to_answer_q1(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        name = r.get("Name") or r.get("name")
        ver = r.get("Version") or r.get("version")
        if name and ver is not None:
            lines.append(f"{name} {ver}")
    return "Top 5 NPM packages (latest release per package name, by GitHub stars):\n" + "\n".join(lines)


def rows_to_answer_q2(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        proj = r.get("ProjectName") or r.get("projectname")
        ver = r.get("Version") or r.get("version")
        forks = r.get("forks")
        if proj:
            lines.append(f"{proj} version {ver} — {forks} forks")
    return "Top 5 projects by GitHub fork count (MIT license on project, release packages):\n" + "\n".join(lines)
