const { test } = require('node:test');
const assert = require('node:assert/strict');
const { evaluate } = require('../scripts/production_guard.cjs');
const now = Date.parse('2026-11-26T02:00:00Z');
const id = '11111111-1111-4111-8111-111111111111';
function fixture() {
  return {
    message: '[publish-codex] Publish one validated public-content batch',
    changed: ['content/source-revisions.json'], url: 'https://public.example',
    policy: { enabled: true, maxRequestsPer24Hours: 2, maxRequestsPer30Days: 12 },
    marker: { schemaVersion: 2, requestId: id, requestedAt: new Date(now).toISOString(),
      publicContentSha256: 'a'.repeat(64), websiteInputsSha256: 'b'.repeat(64),
      requests: [{ id, at: new Date(now).toISOString() }] }
  };
}
async function check(change = () => {}, published = {}, env = {}) {
  const data = fixture(); change(data);
  return evaluate({ CONTEXT: 'production', ...env }, { now, load: () => data,
    fetch: async () => ({ ok: true, json: async () => published }) });
}
test('ordinary source commits cannot start production', async () => {
  assert.equal((await check(x => { x.message = 'Improve a guide'; })).allow, false);
});
test('a release label without a changed request cannot start production', async () => {
  assert.equal((await check(x => { x.changed = ['README.md']; })).allow, false);
});
test('one fresh validated request is allowed', async () => {
  assert.equal((await check()).allow, true);
});
test('an already published request is skipped', async () => {
  assert.equal((await check(() => {}, { publicationId: id })).allow, false);
});
test('identical live content and implementation is skipped', async () => {
  assert.equal((await check(() => {}, { publicContentSha256: 'a'.repeat(64), websiteInputsSha256: 'b'.repeat(64) })).allow, false);
});
test('expired requests cannot redeploy old code', async () => {
  assert.equal((await check(x => { x.marker.requestedAt = '2026-11-24T00:00:00Z'; })).allow, false);
});
test('direct production hooks cannot bypass the build-command guard', async () => {
  assert.equal((await check(() => {}, {}, { INCOMING_HOOK_URL: 'https://redacted.example' })).allow, false);
});
test('unavailable production status fails closed', async () => {
  const result = await evaluate({ CONTEXT: 'production' }, { now, load: fixture, fetch: async () => { throw new Error('offline'); } });
  assert.equal(result.allow, false);
});
test('missing ledger entry is rejected', async () => {
  assert.equal((await check(x => { x.marker.requests = []; })).allow, false);
});
test('over-budget requests are rejected', async () => {
  assert.equal((await check(x => { x.marker.requests.push(...Array.from({ length: 2 }, () => ({ id: 'another', at: new Date(now).toISOString() }))); })).allow, false);
});
test('hold stops production', async () => {
  assert.equal((await check(x => { x.policy.enabled = false; })).allow, false);
});
test('previews remain available without a production request', async () => {
  assert.equal((await evaluate({ CONTEXT: 'deploy-preview' })).allow, true);
  assert.equal((await evaluate({ CONTEXT: 'branch-deploy' })).allow, true);
});
