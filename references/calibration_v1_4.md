# Calibration v1.4: evidence-first, no fabricated scores

## Eligibility gates
1. A real PR title/release note is not an Owner-filled RCA. Never infer an Owner statement from the title.
2. Require explicit owner_root_cause and owner_solution for a production score. Author PR description can be scored only when `input_origin=pr_author_proxy` and disclosed.
3. For authenticity >69 require actual relevant diff or independent technical evidence. For prevention >69 require actual test evidence.
4. If essential evidence is missing return null, status insufficient_evidence, not 0.
5. Freeze PR head SHA and provenance; verify entire multi-commit changes.
6. Preserve distinct source confidence and quality score; no artificial numerical confidence without calibration.
7. Never claim accuracy metrics without two independent human gold labels and model output.

## Sampling
50 public PRs indexed from Apache Camel K GitHub release notes. 4 PR pages separately inspected; 46 indexed from release notes. No full diff fetched in this runtime. This is a genuine public-case eligibility assessment, NOT 50 fully scored RCAs.

## Optimization
A. Two-stage preflight: schema+evidence eligibility (cheap, no LLM) then LLM scoring only for eligible records.
B. Score normative/depth from owner text, authenticity/relevance from diff, prevention from test evidence; never substitute PR title.
C. Use short comments <=40 Chinese chars and compact evidence IDs; long reasoning only on conflict.
D. Stratify 50 gold cases by nil/race/RBAC/security/config/regression/test/dependency/API and by five score levels.
E. Compare blinded expert consensus vs model: per-dimension MAE, weighted kappa, abstention precision, repeatability, token usage.
