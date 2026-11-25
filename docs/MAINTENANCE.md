# Operating the Living Codex

## Existing production project

Keep site `resonant-genie-1ee11c`, Netlify site ID `1c12c5a7-1002-4553-bd67-e1072e8b1081`. Do not create a replacement site. The original known production deployment before modernization is `6b00ec8d59a20d0cae88d22f` (November 20, 2026).

Build command: `python scripts/build.py`. Publish directory: `dist`. Python: 3.12. Public-source ingestion needs no GitHub secret. GitHub Actions uses its ephemeral repository token for API rate limits; this token is not sent to codeload or the browser.

## Automatic publishing

The immediate event path is the `Publish Living Codex` GitHub Action in each authoritative repository. A push of root Markdown or selected `public/players/*.md` on main, or a manual workflow dispatch, posts to the existing Netlify build hook targeting website main. Both repositories store that URL in their encrypted `LIVING_CODEX_BUILD_HOOK` secret. The source workflow needs no GitHub token permissions or checkout. The hook URL must never be committed, placed in the manifest, printed in logs or shipped to visitors.

The website's `Reconcile canonical sources` GitHub Action runs every two hours, at minute 17 UTC. It compares source heads with actual production provenance, updates only `content/source-revisions.json` when a rebuild is needed, and pushes the marker to website main. A failed earlier marker build is retried rather than mistaken for successful publication. Netlify's Git integration then builds the site. This fallback does not depend on the author's PC or a personal token. Scheduled workflows can be delayed by GitHub and may be disabled by GitHub after prolonged repository inactivity; check the Actions tab if updates stop.

The workflow also runs on publishing-configuration changes. It declares a manual **force_rebuild** input; the boolean dispatch UI did not create an observable run during setup, so the configuration-change push verified the cloud worker. A marker commit does not prove deployment: inspect the Netlify deploy result and its `/build.json`. GitHub's own push workflows do not recursively trigger from `GITHUB_TOKEN` commits; the Netlify integration and build validation remain necessary.

Initial linking, webhooks and the end-to-end reconciliation test must be marked verified in the delivery report before relying on them. Until configured and verified, these are implementation capabilities, not claims of an active service.

## Current player teaching content

HP/d20 and Training Points are the current player-facing default by the author’s November 25 instruction; no playtest label is applied. The 25 selected teaching pages live in `MyStalker/mystaria-codex/public/players/`. Update the owning detailed subject/changelog and affected public guide together when a rule changes. The website ingests those files from latest main, expands explicit source-table selections, and regenerates pages/search/downloads. Guide additions and headings require no local website build or manual deploy. A new guide needs a stable entry in `content/reading-manifest.json` and explicit public-manifest selection.

The canon push workflow includes root Markdown and `public/players/*.md`. Keep history, supersession records, simulation evidence and proposals in the detailed repositories. Deterministic publication does not rewrite a teaching summary semantically when only its owning subject changes: maintaining both is part of approving current canon, now specified in canon AGENTS.

## Canon updates

1. Publish the author's approved changes in the owning canon/economy reference and appropriate changelog/index, following that repository's workflow.
2. An event or reconciliation rebuild resolves current heads and captures exact source revisions.
3. Public selection, rendering and validation run in Netlify. Failures leave the previous production deployment serving.
4. Inspect source revisions on the website or `/build.json` to confirm incorporation.

Do not promote a Combat Lab result by editing website status rules. Resolve canon ambiguities in the authoritative repository. An ordinary new paragraph in a reviewed public section needs no website edit; a new document or newly private section requires manifest/privacy review. Automated filters are defense in depth, not a substitute for upstream editorial care.

## Review a substantial website change

Keep the existing production deploy locked against automatic publication while first linking or testing the modernization. Build a Netlify preview/permalink, check representative desktop/mobile pages, search, math, tables, bookmarks, calculators and privacy, then publish that exact successful deploy. Preserve audience and production URL.

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
