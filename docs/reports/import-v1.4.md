> 历史记录：原始评测结论保留；当前目录与复现入口见 [开发说明](../development.md)。

# Import verification — 2026-10-25

Source: rca_chatgpt_calibration_v1_4.zip (19 files).
Source archive SHA-256: `6407f004d29abc1e39a4a9be5b84d83e2d0e69f8d1b38b78fb3a01923d9f9b43`.

## Publication review
All 19 original files were decoded and checked for credential patterns, private-key markers, embedded URL credentials, email addresses, and nonpublic service hosts. No actual credentials or private data were identified. The only URL hosts were github.com, json-schema.org, and the placeholder gerrit.example.com. Gerrit credentials are read from environment variables; no environment values were read or published. Public-case records contain public PR references and summaries, not private Gerrit evidence.

## Import changes
- Explicit UTF-8 file reads/writes in both test modules and the Gerrit output writer for Windows compatibility.
- Added .gitignore for local credentials, private evidence, results, and Python artifacts.
- Corrected README title/archive name to v1.4 and declared the tested jsonschema dependency.
- Scoring weights, schema, and calibration data were preserved.

## Executed checks
Python 3.14; jsonschema 4.26.0. `python -m unittest discover -s tests -v`: all 7 tests passed. JSON files parsed successfully. No authenticated Gerrit fetch or Claude model scoring was executed.

The 50 public-case records are an evidence eligibility audit; the 50 rule scenarios are data fixtures, not 50 executed unit tests or a measured accuracy benchmark. This review is not a guarantee against every possible secret format.
