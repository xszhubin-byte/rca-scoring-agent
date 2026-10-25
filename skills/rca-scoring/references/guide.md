# Runtime guide — 2.0.0-alpha.1

This package reviews daily software-defect RCA. It produces six-domain diagnostic
profiles, not a calibrated overall rank. A domain mean is available only when all
applicable criteria in that domain are known. Unknown items and justified N/A are
not zeros and their weights are not redistributed.

## Input

Follow `v2-result.schema.json`. The structural example is
[`../examples/result.example.json`](../examples/result.example.json); it intentionally
contains unknown items and no invented defect evidence. Replace it with actual input.

- Choose `owner_rca`, `pr_author_proxy` or `artifact_review` in context.
- Preserve supplied text. Set `text_complete=false` for absent/truncated text;
  a truncated report cannot establish that an author omitted a requirement.
- Freeze the revision when making technical claims. Collect located evidence and
  keep author statements, diffs, test source, CI status and execution records distinct.
- Rate each of the 24 named items using `v2-rubric.json`. For observed items provide
  a score and evidence IDs; use null for unknown/N/A and a scope reason for N/A.
- Resolve material claims as supported, refuted or unresolved. A supported technical
  claim needs matching-revision technical evidence, not just its author's assertion.
- An observed V2 execution rating requires a revision-linked execution claim with
  test name, assertion, command, environment and outcome. CI status alone is unknown.
- Derive closure from evidence: planned, implemented, executed or effectiveness_observed.
  Executed does not imply successful. Long-term effectiveness requires follow-up evidence.

## Validate

```text
python -m pip install -r requirements.txt
python scripts/assess_v2.py examples/result.example.json
python scripts/assess_v2.py YOUR_RESULT.json --output YOUR_REVIEW.json
```

Schema and reference checks do not prove semantic correctness. Review whether each
citation really supports the stated mechanism and whether relevant variants were
covered. Prioritize critical contradictions and the smallest useful missing evidence.
Keep credentials and private source evidence in your approved environment.
