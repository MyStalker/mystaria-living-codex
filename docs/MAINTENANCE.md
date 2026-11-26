# Operating the Living Codex

## Existing production project

Keep site `resonant-genie-1ee11c`, Netlify site ID `1c12c5a7-1002-4553-bd67-e1072e8b1081`. Do not create a replacement site. The original known production deployment before modernization is `6b00ec8d59a20d0cae88d22f` (November 20, 2026).

Local build command: `python scripts/build.py`. Netlify's production command first runs `node scripts/production_guard.cjs --build-check`, then the Python builder. Publish directory: `dist`. Python: 3.12. Public-source ingestion needs no GitHub secret. GitHub Actions uses its ephemeral repository token for API rate limits; this token is not sent to codeload or the browser.

## Automatic publishing

The former per-file Netlify hooks are **retired**. They caused repeated paid production deploys while related canon files were saved separately. Neither authoritative repository should call a Netlify build hook. Old hook secrets are not used; never print or copy them into source.

The website's **Queue reviewed Codex release** Action is the single publisher. It checks hourly at minute 17 UTC and after website build-input changes, builds/validates current public sources on GitHub, compares meaningful output with production, and requests at most one release through a durable marker commit. Defaults: six hours between automatic requests, at most 2 requests in 24 hours and 12 in 30 days. Internal docs, timestamps and source-head changes alone do not cause releases. See [Publishing safeguards](PUBLISHING-SAFEGUARDS.md) for exact policy, manual controls and recovery.

Manual runs default to **dry_run**. **publish_now** bypasses the batching interval, and **retry** explicitly permits a new attempt after an unconfirmed release has been inspected; neither bypasses the shared request budget. Unconfirmed requests stop further automatic publishing instead of creating endless retries. GitHub pushes do not recursively trigger GitHub workflows from `GITHUB_TOKEN`; the existing Netlify Git integration handles release marker commits. GitHub schedules may be delayed or disabled after prolonged inactivity.

Initial linking, webhooks and the end-to-end reconciliation test must be marked verified in the delivery report before relying on them. Until configured and verified, these are implementation capabilities, not claims of an active service.

## Current player teaching content

HP/d20 and Training Points are the current player-facing default by the author’s November 25 instruction; no playtest label is applied. The 25 selected teaching pages live in `MyStalker/mystaria-codex/public/players/`. Update the owning detailed subject/changelog and affected public guide together when a rule changes. The website ingests those files from latest main, expands explicit source-table selections, and regenerates pages/search/downloads. Guide additions and headings require no local website build or manual deploy. A new guide needs a stable entry in `content/reading-manifest.json` and explicit public-manifest selection.

Keep history, supersession records, simulation evidence and proposals in the detailed repositories. Save related subject, changelog/index and player-guide changes in one atomic commit when possible. Deterministic publication does not rewrite a teaching summary semantically when only its owning subject changes: maintaining both remains part of approving current canon.

## Canon updates

1. Publish the author's approved changes in the owning canon/economy reference and appropriate changelog/index, following that repository's workflow.
2. The shared queue resolves current heads, captures exact revisions, builds and validates public output, then applies batching and request budgets.
3. An accepted marker triggers the guarded Netlify build. Failures leave the previous production deployment serving; inspect failures before an explicit queue retry.
4. Inspect source revisions on the website or `/build.json` to confirm incorporation.

Do not promote a Combat Lab result by editing website status rules. Resolve canon ambiguities in the authoritative repository. An ordinary new paragraph in a reviewed public section needs no website edit; a new document or newly private section requires manifest/privacy review. Automated filters are defense in depth, not a substitute for upstream editorial care.

## Review a substantial website change

Use a development branch and Netlify Deploy Preview/permalink, check representative desktop/mobile pages, search, math, tables, bookmarks, calculators and privacy, then release the completed main revision through the shared queue. Do not repeatedly publish production during development. Preserve audience and production URL. Emergency rollback through Netlify remains available; inspect any pending queue request before resuming publication.

## Failure and rollback

- Retrieval, missing-source, integrity, source-selection and artifact validation errors abort the build before replacing output.
- The local builder stages output and restores the prior directory if replacement fails.
- Netlify failed builds do not replace the last successful production deployment.
- For a regression, use the existing project's Deploys history to publish the last accepted deploy; lock it to stop immediate auto-publication while fixing the source. The original November 20 deploy ID is above.
- Revert the offending website commit, rebuild and validate; publishing an older deploy alone does not undo current code or upstream canon.
- An old raw-source URL returning 404 is intentional. Never restore public hidden data to repair such a link.

## Extending content and tools

For a new teaching page, write current player-facing Markdown in the canon repository's `public/players/`, add an explicit reviewed public document with a stable id in `content/public-manifest.json`, and add its stable URL/title/section/supporting sources in `content/reading-manifest.json`. Existing included guide sections and headings flow into rendering and search automatically. Do not publish a full source manuscript to avoid writing an explanation. Use `::: detail` for optional depth; selected `{{table:...}}` and `{{ranks:...}}` expansions are defined in `scripts/reading.py` and must select public source blocks unambiguously.

Keep future character builders, item databases and calculators as separate modules with documented public data contracts. Preserve incomplete-rule boundaries and do not turn trial figures into finalized player statistics.

## Known limits

Publication is deterministic rather than an AI rewrite of subject manuscripts. Approved player-facing changes must maintain the affected public teaching page as part of normal canon editing; the canon repository's AGENTS records this workflow. Unmarked contradictions and missing numerical decisions still require author/editorial work. A true source rename needs a manifest path update while keeping stable ids; a unique directory move resolves automatically. New private material must be explicitly excluded.

Tables/rank selectors fail on missing or ambiguous structure rather than silently importing an unrelated passage. Markdown and optional detail markup are supported; formulas compile to native MathML using the pinned dependency. Old calculators preserve their original rules and are not current HP/TP tools. Source metadata and archive material remain available on GitHub without burdening ordinary player reading.
