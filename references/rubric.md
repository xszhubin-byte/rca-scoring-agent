# RCA Quality Rubric v1.0
All subscores 0–100; weights within each dimension sum to 100.

| dimension | overall weight | subcriteria (weight) |
|---|---:|---|
| normative 规范性 | 15% | completeness 30, clarity 25, structure 20, terminology 15, concision 10 |
| authenticity 真实性 | 25% | commit_consistency 20, diff_support 35, scenario_consistency 20, traceability 15, cross_source_consistency 10 |
| relevance 相关性 | 25% | root_fix_match 35, causal_closure 25, coverage 20, targeting 10, solution_soundness 10 |
| depth 根因深度 | 20% | symptom_vs_cause 20, trigger_conditions 20, causal_chain 30, systemic_mechanism 20, contributing_factors 10 |
| prevention 预防有效性 | 15% | regression_evidence 30, edge_tests 20, similar_issue_sweep 20, preventive_action 20, followup 10 |

## Detailed meanings
- normative: completeness of symptom, trigger, cause, fix and change reference; unambiguous language; separate fields; accurate technical terms; concise non-redundant text. Judge writing only, not truth.
- authenticity: commit message agreement; before/after diff supports stated mechanism; reported scenario aligns with code path; identifiable change/revision/file/test; independent sources agree.
- relevance: repair directly addresses stated cause; full cause→failure→fix→resolution chain; key branches covered; avoids symptom-only patches; technically sound solution.
- depth: separates symptom and cause; identifies trigger/state/timing; explains mechanism; identifies underlying design/state/interface issue where relevant; considers contributing factors if present.
- prevention: reproducible regression verification; relevant edge cases; check similar paths; preventive tests/guards/contracts; track follow-up. Proportionate to defect risk; manual/hardware test is acceptable if documented.

## Scoring anchors for EACH subcriterion
90–100: specific, complete and supported for the defect's complexity.
80–89: correct with minor omissions.
70–79: core requirement satisfied but important details absent.
60–69: weak, vague or substantially incomplete.
0–59: absent, unsupported or materially wrong (0 if entirely absent).
Use null only for evidence unavailable, never as a synonym for 0.

## Evidence and fairness
- Commit message alone caps authenticity at 69. To score higher, inspect diff or independent technical evidence.
- Without diff or equivalent technical evidence, relevance capped at 79.
- Positive contradiction caps authenticity at 39 and triggers manual review.
- If Gerrit access is missing, authenticity status `insufficient_evidence`, score null, overall null; don't label Owner dishonest.
- Missing test record is not proof tests failed; assess documented validation and state limitations.
- Do not assume latest patchset was deployed. Multi-commit fixes require reviewing the full set.
- Require evidence IDs for external claims; keep comments short and distinguish verified facts from inference.

## Formula / levels
Dimension = Σ(subscore × subweight)/100. Overall = 0.15*N + 0.25*T + 0.25*R + 0.20*D + 0.15*P. Round half-up to 1 decimal. Missing dimension => overall null.
A >=90 优秀; B >=80 良好; C >=70 合格; D >=60 待改进; E <60 不合格.

## Gerrit REST reference
GET /changes/{change-id}/detail
GET /changes/{change-id}/revisions/{revision}/commit
GET /changes/{change-id}/revisions/{revision}/files
GET /changes/{change-id}/revisions/{revision}/files/{file-id}/diff
Authenticate securely, strip Gerrit XSSI prefix, URL-encode IDs and file paths, and redact secrets. Cache by revision SHA.
