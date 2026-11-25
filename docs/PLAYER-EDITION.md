# Player teaching edition — November 25, 2026

The previous site rendered accumulated source manuscripts. This pass replaces that reading path with 25 focused teaching pages, a searchable 37-entry weapon/shield enchantment catalogue, a terminology sheet, and concise section introductions. The author explicitly chose **HP/d20 plus Training Points as the current game, without a playtest label**.

## Main deliverables

- `/learn/character/`: concept, race/background, five attributes, three budgets, abilities, loadout, sheet checklist and first turn.
- `/learn/training/`: attribute progression, independent SP/TP income and spending, escalating rank purchases, derived statistics and build planning.
- `/learn/health/`: natural END-derived HP, training, damage/armor, Shimmer Reserve/Break and the latest sleep-restoration ruling.
- `/learn/equipment/`, `/learn/enchantments/`: readable profile fields, armor/shields, Weight/handling, specialty tradeoffs, enhancement modes, Soul Strain, Leywells, actions, slots and pricing boundaries.
- `/economy/regions/`: Scarlands–Canopy side-by-side strengths, constraints, trade, inequality and the Imperium's place.
- `/economy/mana/`: usable MP, depleted mana, managmins, generation/refining, storage/distribution, waste collection and disposal. Six optional sections cover cargo references, Leshy deep-soil cleanup, Leydrain accounting, directional ecological burdens, the exact five valid depleted-color Hex pairs, and Hexen reclamation.
- Additional guides cover combat, conditions, magic, races, regions, society, creatures, food, trade, magical traditions and materials.

## Source and publishing architecture

The new teaching prose is owned by [`mystaria-codex/public/players`](https://github.com/MyStalker/mystaria-codex/tree/main/public/players). The website has route/presentation configuration rather than a second copy of those lessons. Detailed subject manuscripts retain canon precedence and their complete historical record. Canon AGENTS now requires affected player guides to be maintained alongside approved source changes.

Canon status direction: `fe4aada2f528d2c044eeb8ec743d7fefe9043c0c`.

Public guide/source-workflow integration: `634178e0bf6679e73ddaaef209cfef41a48e7367`. Current guide/rank-choice revision: `4ab9ac153d40fadbf82d4a375cce3956dd715fa0`.

Economy source: `0f8591d431f412ef6ab495f597540b7c9733c2af`.

The public manifest selects 61 supporting source documents plus 25 player guides. Builds retrieve current main, verify blobs, filter private sections, expand selected source tables and catalogue entries, render new guide sections, and generate navigation/search/downloads. Changes to included guide prose/sections need no website code or local rebuild. The canon push workflow now includes `public/players/*.md`; existing Netlify hooks and the cloud reconciliation fallback remain in place.

This is deterministic publication, not an AI semantic rewrite on each commit. A substantive rule approval must also update the affected teaching page through the normal canon workflow. New guides still need an explicit manifest entry. Unmarked contradictions are not automatically adjudicated.

## Presentation and preservation

The familiar Explore the Codex categories, artwork, paper/purple theme, bookmarks and theme preferences remain. Start here and Build a character provide a clear entry point. Historical and manuscript routes lead to the relevant lesson through compatibility pages and Netlify redirects; their old text is not copied into the player edition. Search indexes current teaching sections and independently addressable catalogue entries. Direct fragment links open the appropriate optional explanation automatically.

Wide tables become labeled topic cards on phones, preserving the comparison-table layout on desktop and print. Two-column tables fit their available width; a bounded scroll region remains available when needed. Optional detail, a collapsible contents list, print controls/styles, and Markdown downloads support different reading needs. Source links and build revisions are available as optional further reading rather than repeated warnings and badges. Earlier calculators are retained at their old address, clearly separated from the current HP/TP rules.

## Validation and deployment

Local artifact checks cover all pages, links/anchors, privacy/credential boundaries, search targets and original artwork. The Python suite covers source policy, current-rule presentation, HP/recovery examples, the five Hex pairs, catalogue anchors, optional-section escaping, synthetic source publication and preservation of accepted output after failure. Calculator assertions and JS syntax checks remain.

The local browser preview could not connect, so browser acceptance used a locked Netlify permalink. The reviewed release was then published to the existing production site and automatic publication unlocked. No site, deployment history or URL was replaced.

## Remaining rules decisions

No new training price ladder, HP-per-rank schedule/cap, complete five-stat racial array, item conversion, missing spell selection, numeric channel schedule, or unresolved edge case is invented. The guide tells players what each system does and identifies actual sheet/menu decisions for their GM. The physical/economic working references keep their proper context rather than becoming universal item or market laws.

## Rollback

Publish the previously accepted deploy in the same Netlify site and lock while fixing the regression. Pre-player-edition production is deploy `6b070860b5a2c07e40e8d858` at website commit `b9f8c4152130666291193acf29ea05c28d6bd7eb`. Revert the offending website or source change and validate before resuming publication. Promoting an older deploy does not revert Git. No historical deployment or source manuscript was deleted.

## Verified release evidence

- Production URL: https://resonant-genie-1ee11c.netlify.app/
- Accepted player-edition deploy: `6b0715ef15c341ebd9cd3038`, website `a277575de675725bf92f3f22f213e75ff58ba993`, canon `4ab9ac153d40fadbf82d4a375cce3956dd715fa0`, economy `0f8591d431f412ef6ab495f597540b7c9733c2af`. Actual production `/build.json` was read after publishing and matched these revisions. Later documentation/test commits may supersede the website revision without changing the lessons.
- Clean cloud build/test validation: https://github.com/MyStalker/mystaria-living-codex/actions/runs/45661318403 . Subsequent final verification runs appear in the same Actions history.
- A change **only inside the public guide directory** triggered the canon push publisher successfully: https://github.com/MyStalker/mystaria-codex/actions/runs/45661434635 . Its Netlify hook built the accepted release above; the preview's metadata showed the new guide source hash and the new learned-rank tables were rendered. No synthetic unapproved canon was added upstream.
- The reconciliation worker also succeeded during the pass: https://github.com/MyStalker/mystaria-living-codex/actions/runs/45660053540 , creating marker `108e4a9655d05094d62538250582cd05413b5b3a` and a successful Netlify build.
- Local final artifact: **336 HTML files including compatibility pages and 404, 9,823 links/anchors checked, 243 search records, zero validation errors**. The page count includes compatibility stubs, not 335 newly authored lessons. Netlify processed 282 redirects successfully.
- The suite now contains **21 Python tests**, including the added current rank-choice regression; 14 preserved calculator assertions and shipped JS syntax checks also pass.
- Browser acceptance covered the character guide on desktop and 390px mobile, the responsive regional comparison, a fitting two-column Hex-pair table, optional detail/direct-fragment opening, precise Dreamcatcher search, 37-entry catalogue filtering to Guardian, bookmark add/remove, theme toggling/restoration, and the six expandable Wakecraft trees. No horizontal page overflow was observed on checked mobile pages.
- New teaching coverage includes six Wakecraft, three Psycraft and four established Anvilcant rank trees as optional live reference tables. Their capability identities do not waive casting, resistance or missing HP conversion rules.

No author setup action remains. Continue approving canon normally, including the affected `public/players` teaching page in the same editorial pass. Publishing happens in the cloud. New creative/mechanical decisions remain the author's authority.
