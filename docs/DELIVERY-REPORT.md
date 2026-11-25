# Living Codex 2.0 delivery record

Implementation and local validation are complete. Cloud validation, browser acceptance, Netlify linking and automatic publishing are being verified; this record will be updated with observed outcomes.

## Recovered baseline

Recovered archive: `Mystaria-Living-Codex-Modernization-2026-11-20.zip`, 17,160,532 bytes, 364 entries, SHA-256 `697046bbaf4e3b8d4ecc4ca7271618b4cea09854f8ffd1e79701c62debef1773`. It contains SOURCE, PUBLISH, ROLLBACK, completion notes and the earlier full implementation. The separately supplied duplicate attachment was not independently byte-compared; the recovered source's version, artwork and functionality match the live site's observed November 20 footer (`2026.11.20.1`, canon `3f670a3`). Original source is Python plus markdown-it-py, static HTML/CSS/JavaScript and manual Netlify Drop. No framework or application-server rewrite was needed.

The original local archive and Git bundle remain intact. Public baseline theme and browser utilities were committed first to website main in `c33100d6d9bc0ebb75fd17996555296351a915d0`. Complete raw historical/GM material was deliberately not copied into the public website repository.

## Architecture and source revisions

Dedicated repository: https://github.com/MyStalker/mystaria-living-codex

Static Python build with exact markdown-it-py 3.0.0 / mdurl 0.1.2 dependency pins. Central public manifest; immutable source archives checked against Git blob hashes; Markdown/table/TeX preservation; generated section indexes, search, downloads, legacy routes, source metadata and validation; atomic output replacement. Pinned MathJax provides optional mathematical presentation. No visitor GitHub API calls and no credentials in client code.

Initial validated canon revision: `bec97f56050a2277c76ab22e23d93930055ff472`.

Initial validated economy revision: `7c26bce7c92a86f514dc7ccd968375e80a2d9a40`.

Each later build's `/build.json` is the controlling provenance record. Combat Lab source and results are not automatically treated as approved rules.

## Coverage

61 reviewed public document selections, including operative combat references and separated HP/d20 research, progression, races, major Crafts, equipment/materials/enchantments, cultures/languages/fashion, the Imperium, Worldcoil, Canopy polity/citizenship, Leshy/Beanstocks, agricultural and mana benchmarks, currency/labor, mining/refining, machinery, energy and magical waste. Economic drafts appear only in development. The Bestiary points to approved creature references; no missing creature statistics are invented.

216 generated reference/compatibility pages plus a 404 page and 1,963 search records in the current local build. All 121 original HTML addresses retain a compatible page. The original GM volume is retired; old raw-source downloads are blocked. Existing artwork, welcome material, twelve public volume vignettes, local-storage keys and operative calculators are retained.

Missing source data and unmarked historical contradictions remain unresolved; a file on main is not blanket-certified current canon. Conservative reference labels preserve source qualifications. True file renames need a manifest path adjustment while retaining stable ids; directory moves with unique filenames resolve automatically. New documents require public-inclusion review.

## Local validation observed

- Full build: 217 HTML files, 8,571 generated links and anchors checked, zero errors.
- Seven policy/integration tests passed, including synthetic public proposal ingestion and failed-refresh preservation of last successful output.
- Fourteen operative calculator boundary assertions passed; shipped JavaScript syntax checks passed.
- Source integrity checked against pinned Git blobs.
- Privacy and credential marker scans, page language/h1/image-alt checks, search target validation and inherited artwork presence passed.
- Search index contains representative Rosewheat, Cindercorn, Avowed, Dirtmoles, Honed, Freeze, Dreamcatchers and Leydrains entries.

The local HTTP preview did not become reachable from the browser. No rendered layout acceptance is inferred from those checks; browser verification will use a Netlify deploy permalink.

## Publishing configuration and verification

`netlify.toml` targets the existing project's static build and publish directory. GitHub Actions implement clean cloud builds/tests and a two-hour source reconciliation fallback. Event-driven upstream push webhooks to a Netlify build hook are the preferred immediate path. The report must distinguish configured/tested service settings from these committed implementation files.

Production target: https://resonant-genie-1ee11c.netlify.app/

Known pre-modernization production deploy: `6b00ec8d59a20d0cae88d22f`. Existing Netlify site ID: `1c12c5a7-1002-4553-bd67-e1072e8b1081`. The signed-in account can view the existing project. No replacement site was created and no previous deploy was deleted.

## Rollback and limitations

Publish a prior accepted deployment in the same Netlify site's Deploys history, lock against automatic publication while repairing, then revert the offending website commit and rebuild. The November 20 deployment and original recovery artifacts remain available. Build failures must not replace production; isolated integration tests verify local failure preservation.

Remaining verification items are clean cloud execution, rendered desktop/mobile and interactive checks, external reference availability, live publication, event-driven webhook delivery and scheduled reconciliation behavior. The final delivery will record completed items and any exact author action still required.
