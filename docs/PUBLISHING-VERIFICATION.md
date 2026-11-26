# Publishing safeguards verification — November 25, 2026

## Changes published to main

| Repository | Files |
|---|---|
| `MyStalker/mystaria-codex` | `.github/workflows/publish-living-codex.yml`, `AGENTS.md` |
| `MyStalker/mystaria-economy` | `.github/workflows/publish-living-codex.yml`, `README.md` |
| `MyStalker/mystaria-living-codex` | `.github/workflows/reconcile.yml`, `.github/workflows/validate.yml`, `AGENTS.md`, `README.md`, `docs/MAINTENANCE.md`, `docs/PUBLISHING-SAFEGUARDS.md`, `content/publishing-policy.json`, `netlify.toml`, `scripts/build.py`, `scripts/reconcile.py`, `scripts/publication.py`, `scripts/production_guard.cjs`, `tests/test_publishing.py`, `tests/test_reconcile.py`, `tests/deploy_guard.test.cjs`; this verification report |

No lore, mechanical definitions, source inclusion policy, website artwork, account plan or public URL changed. The existing Netlify project was retained. No subscription or paid recharge was enabled. The retired hook/secrets were not read or removed; the replacement does not use them.

Implementation commits:

- [Canon instructions and hook retirement](https://github.com/MyStalker/mystaria-codex/commit/1d1151b1ce70666cc0e86d02c86bc64eddcc3be9)
- [Economy hook retirement](https://github.com/MyStalker/mystaria-economy/commit/d5ccdaf56a10b7044aaf2203638c0a9cf22f2e7b)
- [Shared queue and production guard](https://github.com/MyStalker/mystaria-living-codex/commit/73397c01c6d56fe7feb08f6cc320e648e8fdd83a)

## Verified checks

- Local public build and artifact validation passed: 336 HTML files, 9,823 links, 243 search records, no validator errors or warnings. That local build used the existing integrity-checked development cache (`canon 4ab9ac153d40fadbf82d4a375cce3956dd715fa0`, `economy 0f8591d431f412ef6ab495f597540b7c9733c2af`); it was not a production deployment.
- 38 Python tests passed, including the full isolated publishing build and preservation of accepted output after failed retrieval/integrity checks. A second full fixture build with only changed upstream commit metadata produced the same public-content fingerprint.
- 12 Node production-guard tests passed. They cover ordinary commits, valid releases, duplicate/expired releases, retired production hooks, ledger/budget checks, unavailable production metadata and preview availability.
- 14 existing calculator boundary assertions passed; browser JavaScript syntax checks passed.
- [Cloud validation](https://github.com/MyStalker/mystaria-living-codex/actions/runs/45746678930) passed its current-main build, all tests and anonymous checks of the existing production site.
- [Cloud release queue](https://github.com/MyStalker/mystaria-living-codex/actions/runs/45746678588) passed build/validation using current source commits `canon 1d1151b1ce70666cc0e86d02c86bc64eddcc3be9` and `economy d5ccdaf56a10b7044aaf2203638c0a9cf22f2e7b`, then created exactly one durable request.
- Initial queued request: `4f7ed8bd-cc53-414f-8f86-951074d4344a`, marker commit [542fe72](https://github.com/MyStalker/mystaria-living-codex/commit/542fe722019c1893391892529f6c701dd8aaed3b). A request is not proof that Netlify accepted/published the build.
- Re-ran the cloud queue job against current main. It succeeded, reported that the previous release was unconfirmed, and created no second request or marker commit. A subsequent GitHub read confirmed the original request ID and ledger length of exactly one. This verifies cloud repeat-run suppression while Netlify publication is unconfirmed.

## Remaining limits and action

The Netlify dashboard previously reported production deploys paused because only operational credits remained. A new production publication of the safeguard metadata has not been verified. Source editing and scheduled checks are available; an unconfirmed request holds further automatic release requests. When production deploys are available again, inspect Netlify and use the shared queue's explicit **retry** (uncheck **dry_run**) to issue one fresh request if needed. Daily and 30-day budgets still apply.

There is no verified refund of previously used credits, no verified account reset date, and no account-wide usage cap imposed by this code. The rolling queue ledger starts with these safeguards and does not include earlier deployments. Other sites, serving traffic and direct uploads remain separate. Existing-site availability was checked in cloud CI; a real Netlify release and post-release metadata check remain necessary to verify the hosting-side path end to end.
