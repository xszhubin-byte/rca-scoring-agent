# Public GitHub assessment (2026-10-25)

50 genuine PR identifiers from Apache Camel K release notes: https://github.com/apache/camel-k/releases. Four PR pages manually checked: #6442 #6460 #6609 #6665. Source-level labels disclose which entries were only release-indexed. Scores intentionally null: no owner-authored RCA + complete diff + test records. No model-vs-human accuracy claim.

To complete the requested 50-case numerical benchmark: use GitHub API with authenticated access to freeze PR head SHA, fetch PR body/commits/files/checks/linked issues, have two expert raters label all five dimensions, then run LLM on identical snapshots and compute MAE/weighted kappa.
