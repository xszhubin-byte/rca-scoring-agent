# Codex CLI calibration of the 50 public cases

The 2026-10-25 run uses **Codex CLI**, not Claude CLI. This is an offline,
fixed-evidence evaluation. Codex is instructed not to call tools, execute patches,
fetch URLs, or treat PR bodies as instructions. It reads the supplied rubric,
public PR body, aggregate fixed-SHA diff, check-run metadata and selected job steps.

## Reproduce

Use Python 3.10+ and `pip install -r requirements.txt`. Authenticate Codex CLI with
your own account; no credentials belong in this repository. Then run:

```text
python -m unittest discover -s tests -v
python scripts/calibrate_snapshots.py
python scripts/run_codex_calibration.py --private-run-dir ../private-codex-runs
```

The runner invokes `codex exec --ignore-user-config --ephemeral --sandbox read-only
--skip-git-repo-check --json --output-schema ... --output-last-message ... -`.
The CLI's default model is used; the event stream did not expose its resolved
model identifier. Do not infer a model name. Metadata records CLI version, usage,
elapsed time, prompt hash, evidence hash and exit status. Output schema compliance
is separate from substantive score correctness. `--ignore-user-config` reduces
machine-specific settings; it does not replace CLI account authentication.
For a future run, `--model YOUR_EXPLICIT_MODEL` pins the requested model; it does
not retroactively identify the model used by these recorded default-model runs.

To repeat a fixed five-case batch independently (zero-based index):

```text
python scripts/run_codex_calibration.py --private-run-dir ../private-codex-runs --repeat-batch 6 --repeat-label repeat-02
python scripts/run_codex_calibration.py --private-run-dir ../private-codex-runs --repeat-batch 6 --repeat-label repeat-03
```

Raw CLI event streams and diagnostic files stay in the private run directory.
Do not upload local authentication files, configuration, environment variables,
or unreviewed diagnostics. Only structured final results and filtered execution
metadata belong in `calibration/codex_v1_4/`.

## Meaning of the results

- `executed_v1_4/owner_scores.json`: schema-valid abstentions for real Owner RCA
  scores. No case supplied a distinct Owner's RCA record.
- `codex_v1_4/batch-*.json`: actual CLI model responses. A substantive PR body
  may qualify as `pr_author_proxy`; it is never silently promoted to Owner input.
- Missing regression execution is null, even when check-run metadata says success.
  Test source supports test-design observations, not a claim that assertions ran.
- `executed_v1_4/controlled_regression.json`: 9 unique synthetic rule scenarios
  executed for each case ID (450 invocations). These repeat the same rules; they
  are not 450 independent real defects or 450 judgments of upstream patch quality.

There are no independent expert gold labels. Do not report model accuracy, MAE
against humans, weighted kappa, false-positive rates on human labels, or a model
comparison. A repeatability delta, if available, measures self-consistency only.

## Evidence boundaries

All 50 head/base SHAs were fetched. GitHub's fixed-SHA compare API provides an
aggregate merge-base-to-head diff covering multi-commit PRs. File count and hunk
addition/deletion counts are verified against returned metadata. This does not
mean complete repository context, semantic correctness, or exhaustive deployment
coverage. Removed-file URLs correctly point to the merge base.

All check runs and workflow runs fit the requested 100-item first page. One
representative workflow was expanded to job steps per case (prefer `common`,
otherwise first test/build workflow). Other workflow details were not expanded.
One successful job's raw log was requested per case; all 50 returned HTTP 410.
No raw test log was obtained, and no upstream Go/Kubernetes test was rerun locally.
An unavailable log does not mean the test failed. Old PR descriptions and CI
conclusions are mutable observations with collection timestamps, not signed proof.

Original release-index data remains unchanged for provenance. New snapshots and
execution results supersede its old evidence-availability audit; they do not
retroactively turn the original 50 records into gold labels. PRs include features,
dependency upgrades and maintenance, so this is not a representative defect-only
sample. Source code and excerpts remain attributable to Apache Camel K and the
listed original URLs; no project authorship is claimed here.

Official Codex evaluation workflow:
https://developers.openai.com/blog/eval-skills

## V2 research continuation

The active skill entrypoint now routes daily defect reviews to the experimental
V2 diagnostic framework. Its six-domain design has not been proven superior to
four or five domains. Read `v2-design-review.md` for candidate comparison and
the independent-label study plan; archived V1.4 results retain their old scale.

`python scripts/run_v2_behavioral_probe.py --private-run-dir ../private-codex-runs
--run-label new-independent-run` runs an independent five-input synthetic probe.
It preserves original outputs, validates evidence/maturity constraints and
checks counterexamples. The initial run passed 2/5 behavioral checks; after
aligning an inconsistent execution-evidence anchor and the program gate, the
targeted rerun passed 5/5. This is a regression result on seen constructed inputs,
not a held-out accuracy result. Full records are in `calibration/v2_behavioral/`.
