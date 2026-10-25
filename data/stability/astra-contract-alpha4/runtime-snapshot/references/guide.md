# Runtime guide — 2.0.0-alpha.3

The six-domain diagnostic profile is experimental. Material availability, factual
claim support, quality and execution maturity are distinct outputs.

## Freeze before rating

Set `context.review_contract` to `1.0`. For an owner/proxy report include the
unchanged text, text_complete flag and a located author_statement evidence record.
Freeze typed evidence before grading. Evidence kinds are declarations that require
provenance review; the program cannot establish their authenticity.

```text
python scripts/review_contract.py INPUT.json --output CONTRACT.json
```

Contract 1.0 fixes the appraisal subject, each item's material-availability basis,
and the maximum stage actually represented by the supplied records. It does not
assign quality scores or factual claim statuses. A complete report is evaluable
content: grade only its explanation, using 0 for known missing required content.
A patch cannot supply explanations that its author omitted. Artifacts can support
or refute existing claims, but do not become additional report text.

For artifact review, source kinds determine available fields: current diffs cannot
reveal introduction history, process escape or an unprovided follow-up plan.
Observed means material is available for appraisal, not that a claim is true.
Unknown means unavailable material and stays null. Older unconstrained records
remain readable, but do not carry the contract's repeatability claim. Contract 1.0
has no implicit N/A exclusions; explicit applicability-policy support needs a new
version rather than ad hoc exclusions by the grading model.

O1 concerns introduction history/implementation assumptions, not the failure's
runtime trigger. L4 concerns an explicit closure-check plan; describing the current
regression test belongs to V1 and does not itself supply a follow-up plan.

## Execution facts

A matching-revision record must identify the test, assertion, command, environment
and outcome to establish recorded execution. A failed execution is still executed.
V2 grades the record's verifiability, not success; whether a passing claim is false
is judged separately as a claim and can require revision regardless of quality scores.
CI status and test source alone do not prove a specific assertion ran. A structured
record is still subject to authenticity review; source labels are not calibrated confidence.

## Validate

[The structural example](../examples/result.example.json) has no defect evidence and
therefore returns needs_evidence. Replace it with actual input and item judgments.

```text
python -m pip install -r requirements.txt
python scripts/assess_v2.py YOUR_RESULT.json --output YOUR_REVIEW.json
```

The validator rejects item states or closure inconsistent with contract 1.0.
It validates located references and assertion-linked execution requirements but
cannot prove the cited material supports the causal mechanism. Keep evidence gaps,
critical contradictions and minimal prioritized follow-up actions visible.
