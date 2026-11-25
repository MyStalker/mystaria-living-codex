> Historical 2.0 infrastructure report. The current player teaching pass is documented in [PLAYER-EDITION.md](PLAYER-EDITION.md).

# Living Codex 2.0 — delivery report

November 25, 2026. **Published at the original production URL, with immediate canon publishing and a verified cloud reconciliation path.**

- [Production website](https://resonant-genie-1ee11c.netlify.app/)
- [Website repository](https://github.com/MyStalker/mystaria-living-codex)
- [Operating and rollback instructions](MAINTENANCE.md)

## Recovery assessment

Recovered archive: `Mystaria-Living-Codex-Modernization-2026-11-20.zip`, 17,160,532 bytes, 364 entries; SHA-256 `697046bbaf4e3b8d4ecc4ca7271618b4cea09854f8ffd1e79701c62debef1773`. SOURCE, PUBLISH and ROLLBACK contain the editable implementation, output and recovery artifacts. The separately supplied `(1)` duplicate was not independently byte-compared. The recovered implementation matches the live site's observed November 20 version, artwork and functionality.

The original is Python plus markdown-it-py and static HTML/CSS/JavaScript, previously deployed by Netlify Drop. Its original archive and Git bundle remain untouched. Public theme/browser utilities were preserved on GitHub before modernization in [baseline commit c33100d](https://github.com/MyStalker/mystaria-living-codex/commit/c33100d6d9bc0ebb75fd17996555296351a915d0). The complete historical source, containing raw manuscripts and GM material, remains in local recovery archives rather than a complete public Git baseline.

## Architecture and files

The site remains static. Python 3.12 uses pinned markdown-it-py 3.0.0, mdurl 0.1.2 and latex2mathml 3.78.1. A normal build resolves current main once per authoritative repository, downloads immutable archives, verifies selected files against Git blob hashes, selects public sections, renders, validates and atomically replaces output. Production never silently substitutes stale cached sources.

| Files | Purpose |
|---|---|
| `scripts/sources.py` | Pinned ingestion, integrity, public selection and conservative status classification. |
| `scripts/build.py`, `scripts/math_render.py` | Reader, headings, tables, native MathML, navigation, search, downloads, provenance and staged output. |
| `scripts/validate.py`, `scripts/check_production.py` | Whole-artifact validation and anonymous production HTTP checks. |
| `scripts/reconcile.py` | Compare current heads with actual production provenance; retry stale production even if an earlier marker already advanced. |
| `content/public-manifest.json` | Explicit document inclusion, stable ids, sections, filters and aliases. |
| `content/editorial.json`, `content/calculators.html`, `content/legacy-routes.json` | Preserved public editorial material/calculators and compatibility for all 121 earlier HTML addresses. |
| `content/source-revisions.json` | Cloud publishing marker, containing hashes and timestamp only. |
| `assets/codex.css`, `assets/reader.js` | Responsive reference presentation and ranked/filterable search. |
| Existing theme, utilities, illustration and favicon | Preserved; original storage keys and operative arithmetic remain usable. |
| `tests/`, dependency lock, `netlify.toml`, `.github/workflows/` | Validation, deployment, headers and unattended publishing. |
| `AGENTS.md`, `README.md`, `docs/` | Architecture, agent workflow, operations, evidence and rollback. |

TeX is compiled to native MathML at build time, including Markdown-escaped source expressions. Original mathematics is preserved, with TeX available in public Markdown downloads. No visitor math script/font CDN, application server, database or GitHub API access is required. Search and reading preferences operate locally in the browser.

In each authoritative repository, only `README.md` and `.github/workflows/publish-living-codex.yml` were changed for publishing. The economy README's obsolete blanket denial of approvals was replaced with a direction to consult current owning references. No subject canon, costs, prerequisites or changelog was changed: this task introduced no creative canon.

## Canon revisions

| Source | Current verified revision |
|---|---|
| [mystaria-codex](https://github.com/MyStalker/mystaria-codex) | `8dc86260b3e180ebbbe9a159e2ae4f31780e926a` |
| [mystaria-economy](https://github.com/MyStalker/mystaria-economy) | `0f8591d431f412ef6ab495f597540b7c9733c2af` |

Initial content audit: canon `bec97f56050a2277c76ab22e23d93930055ff472`, economy `7c26bce7c92a86f514dc7ccd968375e80a2d9a40`. Later source commits add publishing documentation/workflows and the safe test, without changing lore or mechanics. Each deployed `/build.json` records exact website and source commits and is the controlling record for future revisions. Combat Lab results are not treated as independent canon.

## Coverage and preservation

The public build contains **61 reviewed document selections, 216 reference/compatibility pages plus a 404 page, and 1,787 deduplicated search entries**.

| Area | Coverage |
|---|---|
| Character creation | Races, attributes, Shimmer, progression, SP, training, rewards and exceptions. |
| Combat/equipment | Operative combat, weapons, armor/materials, shields, enchantments, status, resistance, magnitude and separated HP/d20 development. |
| Magic | Sorcery, Warlock/Manacraft, Jestercraft, Anvilcant, Wakecraft, Sanguine Arts, Psycraft, Mnemonic Arts and other public Crafts. |
| World/culture | Scarlands, Imperium/Gilded Coil, Canopy polity/citizenship, public history/divinity, races, language, names, sport, fashion and Worldcoil. |
| Economy/industry | Labor, currency, regional economies, crops/nutrition, agriculture, Leshy/Beanstocks, mining/refining, materials, machinery, energy, Dreamcatchers, Leydrains and waste benchmarks. |
| Bestiary | Existing public creature references and Mossback husbandry; no invented creature-stat database. |
| Development | HP/d20 research/equipment conversion and explicitly provisional economic studies. |

The operative wound engine is distinct from the HP/d20 replacement. Approved experiments, proposals, explicitly historical headings and incomplete references carry separate labels. **Reference · revisions apply** does not certify every retained paragraph of an append-only source as current. Unmarked contradictions need upstream editorial/author reconciliation; missing statistics, costs and creative decisions are not invented.

Private campaigns, hidden revelations and excluded paragraphs are omitted from reader pages, search and downloads. The GM volume is retired; old raw-source download routes return 404. Reveal controls are not an access-control boundary. New documents need manifest review. A unique filename moving directory resolves automatically; a true rename needs a path update while retaining its stable id. Newly private material must be marked or excluded explicitly: filters cannot understand an unmarked secret automatically.

Artwork, favicon, the purple/paper identity, introductions, twelve public volume vignettes, bookmark/theme keys and operative calculators are retained. The approved deferred **The Races of Mystaria** rename is applied. No new canon art or mana symbols were generated. The optional historical PDF builder was not expanded; public Markdown and print styling provide exports.

## Testing

- Clean GitHub-hosted dependency installation and builds succeeded against actual authoritative main branches.
- Artifact validation: **217 HTML files, 8,354 links/anchors, 1,787 search targets, zero errors**. Source identity, privacy paths, credentials, language, headings, image alt text and artwork are checked.
- The suite contains thirteen Python policy/math/publishing/recovery tests and fourteen calculator boundary assertions. The initial full cloud suite passed ten Python tests; three additional reconciliation recovery tests passed locally and are included in subsequent CI runs.
- The isolated synthetic test publishes an explicitly unapproved public fixture, verifies reader/search and private-subtree exclusion, then corrupts ingestion and confirms the last successful output survives. It never writes unapproved canon upstream.
- Browser QA: desktop and 390px mobile layouts, menu, no mobile horizontal overflow, themes, bookmark add/remove, new economy search, experimental filters, calculator output, long tables and native equations. Warlock absorption rendered as MathML beside its source table. No errors were observed in the checked calculator page.
- **Fourteen anonymous production HTTP checks passed**, covering every major section, search, artwork, provenance, native math and the raw-source 404: [validation run](https://github.com/MyStalker/mystaria-living-codex/actions/runs/45650798030).
- FAO and Our World in Data study links resolved. The USDA PDF returned HTTP 403 to the retrieval service; its availability was not certified. GitHub source paths are verified through pinned trees. This is not an exhaustive external-fragment crawl.

## Automatic publishing evidence

Both authoritative repositories have encrypted `LIVING_CODEX_BUILD_HOOK` secrets. `Publish Living Codex` runs on root Markdown pushes to main and supports manual dispatch. It has no repository token permissions or checkout. The hook URL is absent from source and the client.

| Test | Observed result |
|---|---|
| [Economy push run](https://github.com/MyStalker/mystaria-economy/actions/runs/45648567779) | Succeeded; Netlify hook build completed. |
| [Canon hook run](https://github.com/MyStalker/mystaria-codex/actions/runs/45649020648) | Succeeded after enabling initially disabled canon Actions. |
| [Canon main-push test](https://github.com/MyStalker/mystaria-codex/actions/runs/45650624197) | README-only change succeeded after production auto-publication was enabled; no lore changed. |
| [Cloud reconciliation](https://github.com/MyStalker/mystaria-living-codex/actions/runs/45650024585) | Detected source heads, committed marker `b8d39cce94c597639b5ac4d619e0f071d8cefb4e`, and automatically triggered a successful Netlify build. |

The fallback worker is configured at `17 */2 * * *` UTC and on publishing-configuration changes. Its cloud worker and token-push-to-Netlify path were executed; the elapsed scheduled timer itself was not waited for. The boolean manual-dispatch UI produced no observable run during setup, so the configuration-change push path verified execution. GitHub may delay scheduled jobs or disable them after prolonged repository inactivity; immediate upstream push publishing remains separate. Recovery tests cover retrying stale production after a failed prior marker build, and avoiding redundant rebuilds when production already matches.

No publishing step depends on the author's PC being online.

## Production, failures and rollback

The existing site is retained: `1c12c5a7-1002-4553-bd67-e1072e8b1081`, URL unchanged. Netlify's GitHub installation is restricted to the public website repository. Website main is linked with build `python scripts/build.py` and publish directory `dist`. Automatic publication was unlocked after review.

First reviewed 2.0 release: [deploy 6b070590ba740ee5161376b4](https://app.netlify.com/projects/resonant-genie-1ee11c/deploys/6b070590ba740ee5161376b4). Later verification/documentation builds can supersede it; current `/build.json` identifies the live commit.

Actual setup failures included a transient Git host-key error and source-equation escaping. Neither replaced production. The equation handling was corrected; subsequent builds and native-math checks passed. Later Git preparation succeeded. The original November 20 deployment `6b00ec8d59a20d0cae88d22f` and prior history were not deleted. The existing Netlify plan's 90-day automatic deletion policy still applies; local archive recovery is separate.

Rollback: publish a previously accepted deploy in the same site's Deploys history, lock it while investigating, revert the offending source/website change, then rebuild, validate, publish and unlock. Publishing an old deploy does not revert GitHub. Never restore hidden raw-source downloads to repair a retired URL. Failed builds leave the last successful deployment serving.

## Remaining author actions and limits

**No further author action is required for ordinary updates within reviewed public sections.** Initial identity verification is complete. Maintain approved canon in its owning repositories; builds and deployment run in the cloud.

New public documents, true file renames, newly private sections and future interactive tools need manifest/development work. Unmarked canon conflicts and unresolved creative/mechanical decisions remain the author's authority. Large source pages/search may eventually need further splitting. The complete historical baseline is archived locally rather than fully mirrored into public Git. USDA retrieval and the optional boolean-dispatch UI are the specific verification limits above.
