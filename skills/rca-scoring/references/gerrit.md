# Gerrit API retrieval (on demand)
Use authenticated HTTPS with least-privilege credentials. Never log tokens. Gerrit JSON may begin with `)]}'` plus newline; remove prefix before parsing.

1. `GET /changes/{id}/detail` — resolve change, project, status and revision.
2. `GET /changes/{id}/revisions/{rev}/commit` — commit message and SHA.
3. `GET /changes/{id}/revisions/{rev}/files` — changed files.
4. `GET /changes/{id}/revisions/{rev}/files/{file-id}/diff` — relevant hunks.
5. Optionally query comments, related changes, and test links if available in deployment.

URL-encode identifiers, revision and file paths. Pin exact revision SHA rather than floating `current` after resolution. For merge commits, renames, binary changes, generated code and multi-commit fixes, explicitly record coverage limitations. Commit messages are claims, not proof. Diff supports a mechanism but alone may not prove runtime behavior; request logs or tests where needed.

Evidence references should look like `change:<id>@<sha>:<path>:<line-range>` or test run IDs; preserve link in gerrit[].url. Only cite hunks actually read. If access is denied, mark insufficient evidence rather than 0.
