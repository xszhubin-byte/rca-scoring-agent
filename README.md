# RCA Scoring Agent Skill v1.4

## Install
```bash
mkdir -p .claude/skills/rca-scoring
unzip rca_chatgpt_calibration_v1_4.zip -d .claude/skills/rca-scoring
python -m pip install -r .claude/skills/rca-scoring/requirements.txt
```

Open Claude Code in the project and ask: `/rca-scoring Evaluate BUG-123 ... Gerrit change 12345, save JSON`.

## Configure Gerrit
```bash
export GERRIT_URL='https://gerrit.example.com'
export GERRIT_USER='readonly-user'
# Set GERRIT_HTTP_PASSWORD via secret manager, not committed files
python .claude/skills/rca-scoring/scripts/gerrit_fetch.py --change 12345 --out .rca-cache/12345.json
```

## Batch
```bash
python .claude/skills/rca-scoring/scripts/batch_score.py --input defects.jsonl --outdir rca-results
```

Batch runner invokes installed `claude -p`; authenticate Claude Code and ensure permissions to execute scripts and access Gerrit. See `references/claude-code.md` for caveats. Test single record first.

## Quality gates
Validator computes 25 subcriteria -> five dimensions -> overall, validates schema and evidence IDs. An unavailable authenticity score yields overall null. Review all cases with incomplete Gerrit coverage or contradictions. Real-world accuracy requires a human-labeled benchmark.

## V1.3 public GitHub calibration preparation
Run `python -m unittest discover -s tests -v`. See `references/calibration.md` for three source-grounded public fixtures, limitations, and the proposed expert/Claude repeated-run protocol. This is a validator hardening and calibration-readiness test, **not** a measured LLM accuracy study.


## ChatGPT public GitHub calibration v1.4
See calibration/50_real_github_cases.json (50 traceable public PR references), calibration/assessment.json (coverage and limitations), references/calibration_v1_4.md. This run verifies eligibility, not 50 full five-dimensional RCA scores.
