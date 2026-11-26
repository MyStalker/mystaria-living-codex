// Dependency-free: Netlify runs ignore commands before package installation.
const fs = require('node:fs');
const { execFileSync } = require('node:child_process');

function localRequest(env) {
  const sha = env.COMMIT_REF;
  if (!/^[a-f0-9]{40}$/.test(sha || '')) throw new Error('Missing commit identity');
  const message = execFileSync('git', ['show', '-s', '--format=%B', sha], { encoding: 'utf8' });
  const changed = execFileSync('git', ['diff-tree', '--root', '--no-commit-id', '--name-only', '-r', sha], { encoding: 'utf8' });
  return {
    message, changed: changed.trim().split('\n'),
    marker: JSON.parse(fs.readFileSync('content/source-revisions.json', 'utf8')),
    policy: JSON.parse(fs.readFileSync('content/publishing-policy.json', 'utf8')),
    url: JSON.parse(fs.readFileSync('content/public-manifest.json', 'utf8')).site.url
  };
}

async function evaluate(env = process.env, dependencies = {}) {
  if (env.CONTEXT && env.CONTEXT !== 'production') return { allow: true, reason: 'Preview build: no production release.' };
  // Build hooks bypass Netlify's ignore setting. Reject them again in build.command.
  if (env.INCOMING_HOOK_URL) return { allow: false, reason: 'Direct production hooks are retired; use the shared release queue.' };
  try {
    const { marker, policy, message, changed, url } = (dependencies.load || localRequest)(env);
    if (!policy.enabled) return { allow: false, reason: 'Production publishing is held.' };
    if (!message.includes('[publish-codex]') || !changed.includes('content/source-revisions.json')) {
      return { allow: false, reason: 'Source saved; awaiting the validated, batched release queue.' };
    }
    if (marker.schemaVersion !== 2 || !/^[a-f0-9-]{36}$/.test(marker.requestId || '') ||
        !/^[a-f0-9]{64}$/.test(marker.publicContentSha256 || '') ||
        !/^[a-f0-9]{64}$/.test(marker.websiteInputsSha256 || '')) throw new Error('Invalid release record');
    const now = dependencies.now === undefined ? Date.now() : dependencies.now;
    const requested = Date.parse(marker.requestedAt);
    if (!Number.isFinite(requested) || now < requested || now - requested > 6 * 3600_000) {
      return { allow: false, reason: 'Release request expired; queue a fresh reviewed request.' };
    }
    const entries = marker.requests || [];
    if (!entries.some(x => x.id === marker.requestId && x.at === marker.requestedAt)) throw new Error('Missing release ledger entry');
    const dates = entries.map(x => Date.parse(x.at));
    if (dates.some(t => !Number.isFinite(t) || t > now)) throw new Error('Invalid release ledger');
    if (dates.filter(t => now - t < 24 * 3600_000).length > policy.maxRequestsPer24Hours ||
        dates.filter(t => now - t < 30 * 24 * 3600_000).length > policy.maxRequestsPer30Days) {
      return { allow: false, reason: 'Shared production release budget exceeded.' };
    }
    const response = await (dependencies.fetch || fetch)(url + '/build.json', {
      signal: AbortSignal.timeout(10_000), redirect: 'error', cache: 'no-store'
    });
    if (!response.ok) throw new Error('Production status unavailable');
    const published = await response.json();
    if (published.publicationId === marker.requestId ||
        (published.publicContentSha256 === marker.publicContentSha256 && published.websiteInputsSha256 === marker.websiteInputsSha256)) {
      return { allow: false, reason: 'This release is already published.' };
    }
    return { allow: true, reason: 'One validated production request accepted.' };
  } catch {
    return { allow: false, reason: 'Release could not be verified; holding production safely.' };
  }
}

if (require.main === module) evaluate().then(result => {
  console.log(result.reason);
  // Netlify ignore: 0=skip, 1=build. Build command: 0=allow, 1=abort.
  process.exitCode = process.argv.includes('--build-check') ? (result.allow ? 0 : 1) : (result.allow ? 1 : 0);
});
module.exports = { evaluate };
