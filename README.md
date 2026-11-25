# Mystaria: The Living Codex 2.0

Public reference website: https://resonant-genie-1ee11c.netlify.app/

Website implementation: https://github.com/MyStalker/mystaria-living-codex

The Python static builder ingests reviewed public sections from the latest `main` branches of `MyStalker/mystaria-codex` and `MyStalker/mystaria-economy`. The Combat Lab is not a canon source. The site retains the original illustration, paper-and-purple theme, introductory stories, browser-local bookmarks, themes and operative arithmetic aids. No new artwork is generated.

## Build and validate

Python 3.12 and Node.js for JavaScript checks. Production has no application server or database.

```sh
python -m pip install -r requirements.lock
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/validate.py dist
node --check assets/site.js
node --check assets/reader.js
node tests/calculators.cjs
python -m http.server 8766 --directory dist
```

`dist` is the only publish directory. A normal build retrieves current upstream heads and records exact commit hashes in `dist/build.json`. It downloads pinned archives, verifies selected files against Git blob hashes, renders public selections, generates navigation/search/downloads/compatibility pages, and validates the whole artifact before replacement. Network, integrity, selection or validation failures fail the build. `--offline` uses an existing verified `.cache` strictly for development; production never silently falls back to stale sources.

## Content and status

`content/public-manifest.json` explicitly includes documents and public heading selections. `id` is stable across source moves. Basename matching accommodates a directory move; a true rename requires updating `path`, retaining `id` and any legacy aliases. New source documents do not automatically become public.

The upstream manuscripts accumulate corrections. The website uses conservative **Reference · revisions apply** labels rather than treating every paragraph of a file on main as current approved canon. Explicit HP/d20 experimental sections and proposals are separated; historical headings have their own pages and are excluded from default search. Individual qualifications remain binding. Source extraction cannot resolve an unmarked contradiction on behalf of the author.

Public downloads use the same filtered text as the reader. GM/campaign sections, private paragraph markers, excluded source links and raw manuscripts are omitted. No spoiler toggle is treated as access control. The original public GM page is retired and original raw-source download routes return 404 in Netlify.

## Architecture

| Component | Purpose |
|---|---|
| `scripts/sources.py` | Resolve current main, download pinned sources, verify Git blobs, select public blocks and classify status. |
| `scripts/build.py` | Render Markdown, tables, section pages, inherited introductions/stories, downloads, provenance and legacy routes. |
| `scripts/validate.py` | Check all generated links/anchors/search targets, page structure, privacy and credential markers. |
| `scripts/reconcile.py` | Cloud source-head reconciliation and safe publishing marker updates. |
| `content/public-manifest.json` | Central public-content and navigation policy. |
| `content/editorial.json` | Preserved illustrative stories; no source manuscripts or GM volume. |
| `content/legacy-routes.json` | Compatibility for all 121 earlier page addresses. |
| `assets/` | Original artwork/theme/utilities, improved reading CSS and search. |
| `tests/` | Public policy, synthetic publishing, failure preservation and calculator boundaries. |
| `netlify.toml` | Existing-site build, publish directory, headers and retired raw-source routes. |
| `.github/workflows/` | Cloud validation and two-hour reconciliation fallback. |

Math is converted at build time to native MathML using pinned latex2mathml 3.78.1; original TeX remains in public Markdown downloads. No visitor math script or font CDN is required. Search is static, browser-local and makes no visitor GitHub requests. Its generated index currently covers approximately 2,000 sections.

## Publishing and rollback

See [maintenance instructions](docs/MAINTENANCE.md) and [delivery report](docs/DELIVERY-REPORT.md) for verified deployment status, setup, source coverage and remaining limits. Configuration files alone do not prove a live integration.

The complete recovered implementation remains in the original local archive and Git bundle; it contains raw and hidden material and is not mirrored into this public repository. Public baseline theme/utilities were preserved on main before modernization in commit `c33100d6d9bc0ebb75fd17996555296351a915d0`.
