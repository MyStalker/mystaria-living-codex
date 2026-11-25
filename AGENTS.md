# Living Codex maintenance

This repository implements Mystaria's public static reference website. It does not own canon.

1. Start with the latest `main` of `MyStalker/mystaria-codex`: Canon Index, Canon Changelog, subject files, repository instructions. Consult the visual guide for design and linguistic reference for new dialogue. The author's latest explicit approvals have priority. Never infer canon from Combat Lab results.
2. Read `content/public-manifest.json`, `README.md`, and `docs/MAINTENANCE.md` before modifying ingestion or publishing.
3. Build with `python scripts/build.py`. Install exact dependencies from `requirements.lock`. `--offline` is only for a previously integrity-checked local cache; never deploy a stale fallback when current source retrieval fails.
4. Public document inclusion is explicit. Stable `id` values define routes. Changing a source path must retain its id. New documents require public/privacy review and an explicit manifest entry. Never publish whole repository trees or copy `.cache`, campaign records, hidden revelations, local recovery archives or credentials into `dist` or Git.
5. Source manuscripts contain approvals, experiments, history and proposals. Labels are conservative. An experimental heading never replaces operative rules. Do not make numerical or creative decisions during website maintenance. Keep qualifications and unresolved details visible.
6. Build into a temporary stage, validate it, then replace `dist`. Failed builds must leave successful output and Netlify production intact.
7. Preserve inherited artwork, theme identity, `mystaria-theme` and `mystaria-bookmarks` local-storage keys, and old routes through compatibility pages. Do not generate new canon artwork.
8. Run `python -m unittest discover -s tests -v`, `node tests/calculators.cjs`, JS syntax checks and full artifact validation. Use browser QA on a Netlify deploy permalink before publishing substantial changes. Report tests that could not run.
9. Canon changes follow author-approved direct-to-main documentation workflows. Website infrastructure changes must be concrete, tested and reversible; avoid unnecessary approval interruptions. Never delete or recreate the existing Netlify site. Preserve its URL and deploy history.
10. Report changed files, source hashes, live GitHub/Netlify status, limitations and required author actions. Never equate a local build, a commit or a queued build with a verified deployment.
