# Publishing efficiently

The November 25, 2026 safeguard replaces per-file upstream build hooks. The production URL, artwork, content inclusion and last published site are preserved.

## One release queue

Both canon repositories now save approved content without calling Netlify. This website's **Queue reviewed Codex release** Action checks current canon and economy together hourly (minute 17 UTC, subject to GitHub scheduling delays), and after website build-input changes. It builds and validates on GitHub before it can request production. No personal token or build-hook secret is needed.

The queue compares fingerprints of the generated public pages, search index, downloads, routes and assets with production `/build.json`. Timestamps and source revision links alone do not count as public changes. Website build code, dependencies, configuration and assets have a separate fingerprint so a deployment-affecting code/configuration change is retained. Internal docs, tests, budget settings and marker timestamps alone do not require deployment. The production provenance can therefore intentionally lag current GitHub heads when public content has not changed.

If there is a meaningful change, the queue writes exactly one durable request to `content/source-revisions.json` and pushes one `[publish-codex]` commit. The existing Netlify Git integration handles that commit. Normal website commits are held by `scripts/production_guard.cjs`; previews continue to work. No new hosting service is introduced.

## Conservative limits

`content/publishing-policy.json` controls the shared Living Codex queue:

| Setting | Default |
|---|---|
| Minimum automatic release interval | 6 hours |
| Maximum requests in any rolling 24 hours | 2 |
| Maximum requests in any rolling 30 days | 12 |
| Estimated cost per successful production deploy | 15 Netlify credits |

Twelve successful production requests would use 180 credits. This reserves part of the current Free allowance for traffic and other projects; it is **not an account-wide spending limit**. Serving requests, bandwidth, other sites and deployments made outside this workflow are separate. Rolling windows are independent of Netlify billing dates. Limits count requests conservatively, even if Netlify skips or rejects them. Existing deployments made before this ledger began are not included. Changes remain saved when the budget is reached and become eligible later.

Do not increase limits, enable auto recharge, buy services, clear the ledger or bypass the queue without the author's explicit direction. `enabled: false` holds all queue releases while keeping source editing and previews available.

## Everyday work

1. Retrieve current main and update the owning approved rules, changelog/index and affected player guide in one atomic commit where practical. Preserve private-source exclusions.
2. Let the shared queue combine related updates. The author's PC does not need to be online.
3. For website development, use a branch, local checks and Netlify Deploy Previews; publish a completed change through the queue. Do not repeatedly deploy production to test it.
4. Read the workflow summary for "unchanged", batching, budget or unconfirmed-release decisions. A skipped publishing decision is normal.
5. Verify actual publication through Netlify's deploy status and `/build.json` (including `publicationId`, both fingerprints and exact source commits). A successful GitHub job alone is not a successful Netlify release.

## Publish sooner or recover

Open [the queue Action](https://github.com/MyStalker/mystaria-living-codex/actions/workflows/reconcile.yml), choose **Run workflow** on main:

- Keep **dry_run** checked to inspect the decision without spending a request.
- To release changed content sooner, uncheck **dry_run** and check **publish_now**. This bypasses the six-hour wait only; daily/30-day budgets still apply.
- If a prior request was skipped, failed or blocked by exhausted Netlify credits, inspect Netlify first. After fixing the cause, also check **retry** to create a fresh request. Automatic checks never repeatedly retry an unconfirmed release.
- Requests expire after six hours. A stale request cannot be resurrected by repeated Netlify retries. Use the queue to issue a fresh reviewed request.
- If production metadata cannot be verified, publication stops. Restore website access or investigate the outage; do not assume missing metadata authorizes another deployment.

The first release after installing these safeguards bootstraps the new public fingerprint metadata. If Netlify credits are currently exhausted, that request can remain unconfirmed; source work and tests continue. After credits refresh, use the queue's explicit retry instead of repeatedly rebuilding in Netlify. No automatic credit reset date is assumed.

## Retired hook and remaining boundaries

Netlify explicitly does **not** honor `ignore` for build-hook requests. Both upstream workflows therefore stop calling hooks, and the production build command independently rejects `INCOMING_HOOK_URL` requests. The old hook/secrets may remain stored until dashboard cleanup; the new system neither reads nor calls them. Removing the obsolete hook in Netlify is optional cleanup and requires dashboard access.

This is a source-controlled safeguard against accidental repeated releases, not a security boundary against a repository/account owner intentionally changing settings or directly uploading a deploy. GitHub serialization controls the single queue; production checks skip already-published requests. Host behavior and credit accounting still require a real Netlify verification when production deploys are available. Do not claim a new site version is live or that credits have been refunded merely because these files are on main.

## Checks

Run Python tests, the public build/validator, calculator assertions, and `node --test tests/deploy_guard.test.cjs`. Tests cover unchanged/provenance-only output, changed output/assets, batching, rolling budgets, manual/retry limits, request identity/history, failed production reads, expired/duplicate requests, ordinary-commit blocking, retired hooks and previews. Production failures retain the existing accepted deployment.
