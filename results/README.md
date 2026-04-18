# Results — Oracle Forge (Team Falcon)

This directory contains benchmark evaluation results from Oracle Forge runs against the UC Berkeley DataAgentBench (DAB) benchmark suite, plus the GitHub PR submission evidence.

**Live agent:** https://greatest-thesaurus-deposit-engineers.trycloudflare.com/docs

## Contents

| File | Description |
|------|-------------|
| `dab_submission.json` | DAB-formatted results JSON (query/run/answer, 0-indexed runs) |
| `oracleforge_teamfalcon_trp1_n5.json` | Same results in alternative format |
| `PR_SUBMISSION.md` | PR submission record — [PR #35](https://github.com/ucbepic/DataAgentBench/pull/35) submitted 2026-04-18 |

## Benchmark Summary

| Dataset | Queries | Best pass@1 | Trials Run |
|---------|---------|-------------|------------|
| yelp | 7 | 100% | 5 |
| bookreview | 3 | 33% | 1 |
| GITHUB_REPOS | 4 | 0% | 1 |
| stockmarket | 5 | 0% | 1 |

Full score progression (25+ dated runs) is in [`eval/score_log.md`](../eval/score_log.md).

## Submission Format

Each entry in `dab_submission.json` follows the DAB required structure:

```json
{
  "dataset": "<dataset_name>",
  "query_id": "<query_id>",
  "run": <run_number>,
  "answer": "<agent_generated_answer>"
}
```

## How to Reproduce

```bash
# Run a full 5-trial benchmark for any dataset
python eval/run_benchmark.py --dataset yelp --trials 5

# Results are saved to eval/run_logs/benchmark_<dataset>_<timestamp>.json
# Convert to DAB submission format
python eval/score.py --results eval/run_logs/benchmark_yelp_<timestamp>.json
```
