# Operating the Living Codex

## Existing production project

Keep site `resonant-genie-1ee11c`, Netlify site ID `1c12c5a7-1002-4553-bd67-e1072e8b1081`. Do not create a replacement site. The original known production deployment before modernization is `6b00ec8d59a20d0cae88d22f` (November 20, 2026).

Build command: `python scripts/build.py`. Publish directory: `dist`. Python: 3.12. Public-source ingestion needs no GitHub secret. GitHub Actions uses its ephemeral repository token for API rate limits; this token is not sent to codeload or the browser.

## Automatic publishing

The intended event path is an upstream GitHub push webhook to a Netlify build hook targeting website `main`. Configure one hook on the existing Netlify project, and use that private hook URL in the webhook settings of each authoritative repository. Subscribe only to push events. The hook is a build trigger and must never be committed, placed in the manifest or shipped to visitors. An upstream webhook may queue a rebuild for an unrelated push; public selection still controls what is published.

The website's `Reconcile canonical sources` GitHub Action runs every two hours, at minute 17 UTC. It checks current source heads, updates only `content/source-revisions.json` when they change, and pushes the marker to website main. Netlify's Git integration then builds the site. This fallback does not depend on the author's PC or a personal token. Scheduled workflows can be delayed by GitHub and may be disabled by GitHub after prolonged repository inactivity; check the Actions tab if updates stop.

The reconciliation workflow can be run manually with **force_rebuild** to verify the safe marker path without adding unapproved canon. A marker commit does not prove deployment: inspect the Netlify deploy result and its `/build.json`. GitHub's own push workflows do not recursively trigger from `GITHUB_TOKEN` commits; the Netlify integration and build validation remain necessary.

Initial linking, webhooks and the end-to-end reconciliation test must be marked verified in the delivery report before relying on them. Until configured and verified, these are implementation capabilities, not claims of an active service.

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

Add a reviewed manifest document with a unique stable id, repository, source path, section, include/exclude heading expressions and conservative status. Never insert a directory wildcard into the source list. Add old addresses to `aliases` as needed. Public Markdown and source metadata are generated automatically. Keep future character builders, item databases and calculators as separate modules using documented public data contracts; do not extract trial figures and treat them as finalized gameplay data.

## Known limits

Append-only source manuscripts can contain unmarked obsolete or contradictory paragraphs. Classification is conservative and does not semantically adjudicate them. Chapter-level revision notices and source qualifications are essential. Formula enhancement depends on a pinned external MathJax distribution; TeX remains readable when unavailable. Large reference pages and the current static search index can be split further if content growth warrants it. Public source links point to selected upstream files, which may themselves contain broader source context outside the website's filtered excerpts.
