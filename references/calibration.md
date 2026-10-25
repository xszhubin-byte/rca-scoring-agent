# Public-source calibration fixtures (2026-10-25)

These are **public evidence fixtures**, not expert gold-label scores. No Claude Code CLI or GitHub API/Diff retrieval was available in this runtime. Do not report accuracy, kappa, MAE or token savings from them.

| Case | Public URL | Observed evidence | Critical distinction | Expected evaluator behavior |
|---|---|---|---|---|
| CLI-12325 | https://github.com/cli/cli/issues/12325 | Issue reports projectItems null GraphQL node and nil pointer panic in queries_projects_v2.go | Issue report, not verified patch | Do not claim code fix or passing regression tests; authenticity unknown without patch |
| CAMELK-6589 | https://github.com/apache/camel-k/pull/6589 | PR description says typed nil runtime.Object reaches recorder and causes panic; author reports live EKS test; e2e happy-path gap | Author test claim vs independent test logs | Depth can be evaluated from supplied text; independent regression evidence unverified |
| K8S-140561 | https://github.com/kubernetes/kubernetes/issues/140561 | Issue describes gvr.String() nil dereference and proposed log spec.resource; claims unit regression | Proposed fix not necessarily merged | Require actual PR/commit/diff before marking verified |

## Scoring calibration protocol
1. Obtain immutable PR SHA, full relevant diff, linked issue, CI logs and reviews. Record source URL, fetch date, and file path/line for each observation.
2. Have two independent senior reviewers grade all 25 subscores without seeing LLM output; adjudicate disagreements; store gold labels and rationales.
3. Run Claude Code three times per case with fixed model, Skill revision and evidence pack. Measure dimension MAE, weighted MAE, agreement within 10 points, critical false-verified rate, unknown handling, and token usage.
4. Hold out at least 20% of cases from prompt tuning. Release only after reviewing failures and checking regression tests.
5. Suggested initial gate (not measured): dimension MAE <= 10, critical false-verified rate = 0, missing-evidence handling >= 95%; adjust with expert consensus.
