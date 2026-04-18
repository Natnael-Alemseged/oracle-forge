# DEPS_DEV_V1 — MCP execution notes

- The **benchmark’s two official English questions** are answered with one **DuckDB** tool call: `ATTACH … AS pkg (TYPE sqlite)` then join `pkg.packageinfo` to `project_packageversion` / `project_info`. Do **not** emit `package_database.table` or `project_database.table` qualifiers — each MCP call runs against **one** file; cross-database work uses **ATTACH** inside DuckDB or **separate** calls.
- **Stars** in `Project_Information`: use `stars count of ([0-9,]+)` or fallback `([0-9,]+) stars` (strip commas before casting).
- **Forks**: use `forks count of ([0-9,]+)` or fallback `([0-9,]+) forks`.
- **MIT + release (Q2-style)**: MIT is checked on **`project_info.Licenses`**; release on **`packageinfo.VersionInfo`** (`IsRelease` in JSON).
- **Package “latest release” (Q1-style)**: within each `Name`, take the row with highest `Ordinal` inside `VersionInfo` JSON among `IsRelease` rows.

For **paraphrased** questions (not the exact DAB strings), the agent falls back to normal intent + `nl_to_sql` per logical database — follow the rules above.
