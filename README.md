# Mystaria: The Living Codex

Public player guide: https://resonant-genie-1ee11c.netlify.app/

The site teaches the current HP/d20 and Training Points game through focused lessons, comparison sheets, optional deeper explanations, and searchable reference entries. The original artwork, purple/paper theme, browser bookmarks, and reading themes remain.

## Content lives with canon

The 25 teaching pages live in [`MyStalker/mystaria-codex/public/players`](https://github.com/MyStalker/mystaria-codex/tree/main/public/players), not in website implementation. Approved player-facing changes update the owning detailed subject, changelog, and affected teaching page together. The existing cloud publisher retrieves latest main and rebuilds the site without the author's computer.

`content/reading-manifest.json` defines each guide's stable URL, title, section, source document, and supporting references. `content/public-manifest.json` explicitly includes its source files and applies privacy rules. New headings in an included guide automatically enter rendering and search. New guides require explicit inclusion. Do not publish arbitrary repository directories.

Selected source tables (HP/END bands, sleep recovery, enchantment modes, Sorcery purchases and catalogues), current Wakecraft/Psycraft/Anvilcant rank tables, and eligible weapon enchantment entries are ingested at build time. Historical corrections, removed mechanics, proposals, simulation reports, and private campaigns are not the main reading material. Full manuscripts remain on GitHub. Incomplete mechanical decisions stay brief and explicit.

## Build and validate

Python 3.12; Node.js for browser utility checks. Exact Python dependencies are pinned in `requirements.lock`.

```sh
python -m pip install -r requirements.lock
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/validate.py dist
node --check assets/site.js
node --check assets/reader.js
node tests/calculators.cjs
```

The normal build downloads current main commits once per source repository, verifies Git blobs, filters public sections, expands the teaching templates, renders Markdown, and validates a temporary artifact before replacing `dist`. `--offline` is for an already integrity-checked development cache. It is never a production stale-source fallback.

## Architecture

| File or directory | Purpose |
|---|---|
| `scripts/sources.py` | Pinned retrieval, integrity checks, explicit public selections and privacy filtering. |
| `scripts/reading.py` | Lesson rendering, optional detail sections, live source tables, catalogue, search records and page chrome. |
| `scripts/build.py` | Section/home/glossary generation, stories, compatibility routes, provenance, validation and atomic output. |
| `assets/codex.css`, `assets/reader.js` | Responsive lesson hierarchy, expandable depth, printing, search, catalogue filtering and fragment reveal. |
| `content/reading-manifest.json` | Stable guide routes and teaching organization. |
| `content/public-manifest.json` | Explicit allowed sources and public/privacy policy. |
| `content/legacy-routes.json`, `content/editorial.json` | Earlier bookmark routes and preserved illustrative stories. |
| `scripts/validate.py`, `tests/` | Whole-artifact links/privacy/accessibility checks, player-content regressions and publishing/failure tests. |
| `netlify.toml`, `.github/workflows/` | Existing-site cloud builds, validation and reconciliation. |

Only `dist` is published. Cache, source manuscripts, implementation, credentials, and original recovery archives never enter it. Search is static and makes no visitor GitHub queries. Legacy calculators remain available at their existing address with a clear earlier-rules boundary; they are not linked as current HP/TP tools.

See [maintenance](docs/MAINTENANCE.md) and the [player-edition delivery notes](docs/PLAYER-EDITION.md). The original infrastructure delivery record remains [archived here](docs/DELIVERY-REPORT.md).
