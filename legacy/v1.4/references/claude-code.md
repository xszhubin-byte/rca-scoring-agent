# Claude Code execution guidance

Install in `.claude/skills/rca-scoring/` at the project root (or `~/.claude/skills/rca-scoring/` for personal use). Ensure directory contains `SKILL.md` with YAML name and description. Invoke `/rca-scoring` in Claude Code or ask naturally.

## Gerrit configuration

Export `GERRIT_URL=https://gerrit.example.com`, `GERRIT_USER=...`, `GERRIT_HTTP_PASSWORD=...` in your shell or inject through your secret manager. Use a dedicated read-only account and Gerrit HTTP password. Never place secrets in SKILL.md, `.claude/settings.json`, prompt or repository. Optional anonymous mode: omit credentials for public Gerrit; current fetcher still uses `/a/` so anonymous Gerrit needs an authenticated endpoint or fetcher adjustment.

Example: `python scripts/gerrit_fetch.py --change 12345 --out .rca-cache/12345.json`.

The fetcher snapshots a pinned current revision, message, files and bounded diffs; it does not assert deployment or tests. For large changes or incomplete coverage, agent must request targeted evidence or mark insufficient. Never claim the fetcher accessed Gerrit without a successful run. `.rca-cache/` and `rca-results/` should be ignored by Git.

## Batch

`python scripts/batch_score.py --input defects.jsonl --outdir rca-results/ --mode jira_lenient` (default, short JIRA screening).\n\nTo preserve the old five-dimensional Gerrit evidence assessment, pass `--mode strict_evidence`. For mixed datasets, use `--mode auto` and supply each record with `review_mode` (`jira_lenient` or `strict_evidence`). Run `--dry-run` to validate records and show selected modes without starting Claude. The lenient output has a separate JSON contract and is checked by `scripts/validate_jira_lenient.py`; strict output uses the old `scripts/validate_result.py`. Do not compare their 0–100 numbers as equivalent measures.

Requires installed authenticated `claude` CLI, Python 3.10+, jsonschema, network access and tool permissions. This wrapper calls `claude -p` and expects Claude to create the result. The `acceptEdits` mode still depends on the user's CLI/tool policy and does not guarantee access to Bash or external endpoints. Test on one defect interactively before batch use. Avoid running untrusted prompts or private Gerrit code outside approved infrastructure.

## Example input JSONL

`{"defect_id":"BUG-123","symptom":"reconnect crash","root_cause":"session pointer not checked","solution":"check state and pointer","changes":["12345"]}`

## Review gate

Require manual review for contradictions, missing critical evidence, incomplete multi-change coverage, high-risk changes and any overall null. Do not equate RCA scores with employee performance.
