> 历史记录：原始评测结论保留；当前目录与复现入口见 [开发说明](../development.md)。

# Public GitHub assessment (2026-10-25)

## Latest executed continuation

The initial release-index audit below is retained as history. The continuation
retrieved fixed-SHA diffs for all 50 cases, CI check metadata and representative
workflow job steps. See `evidence_v1_4/snapshots.json`,
`executed_v1_4/summary.json`, `codex_v1_4/summary.json`, and
`../references/codex-calibration.md`. The continuation uses Codex CLI.
Raw test log requests returned 410; no upstream test execution is claimed.

## Original audit (before evidence retrieval)

50 genuine PR identifiers from Apache Camel K release notes: https://github.com/apache/camel-k/releases. Four PR pages manually checked: #6442 #6460 #6609 #6665. Source-level labels disclose which entries were only release-indexed. Scores intentionally null: no owner-authored RCA + complete diff + test records. No model-vs-human accuracy claim.

To complete the requested 50-case numerical benchmark: use GitHub API with authenticated access to freeze PR head SHA, fetch PR body/commits/files/checks/linked issues, have two expert raters label all five dimensions, then run LLM on identical snapshots and compute MAE/weighted kappa.
