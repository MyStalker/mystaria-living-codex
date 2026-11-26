import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import publication
import reconcile

NOW = datetime(2026, 11, 26, 2, tzinfo=timezone.utc)
POLICY = dict(enabled=True, minimumIntervalHours=6, maxRequestsPer24Hours=2, maxRequestsPer30Days=12)
CANDIDATE = dict(publicContentSha256='a' * 64, websiteInputsSha256='b' * 64,
                 repositories={'canon': {'commit': 'c' * 40}})


class ReleaseDecisions(unittest.TestCase):
    def decide(self, published=None, marker=None, **kwargs):
        return publication.decide(CANDIDATE, published, marker or {}, POLICY, NOW, **kwargs)

    def marker(self, ages):
        marker = publication.make_request(CANDIDATE, {}, NOW - timedelta(hours=ages[-1]))
        marker['requests'] = [dict(id=str(n), at=(NOW - timedelta(hours=age)).isoformat()) for n, age in enumerate(ages)]
        return marker

    def confirmed(self, marker):
        return dict(publicationId=marker['requestId'])

    def test_identical_public_output_skips_despite_new_source_heads(self):
        self.assertFalse(self.decide(dict(CANDIDATE, repositories={'canon': {'commit': 'd' * 40}}))[0])

    def test_unverifiable_production_never_requests_release(self):
        self.assertFalse(self.decide()[0])

    def test_old_provenance_format_bootstraps_once(self):
        self.assertTrue(self.decide({'repositories': {'canon': {'commit': 'old'}}})[0])

    def test_previous_pending_or_failed_release_is_not_automatically_repeated(self):
        self.assertFalse(self.decide({}, self.marker([48]))[0])

    def test_explicit_retry_can_retry_pending_release(self):
        self.assertTrue(self.decide({}, self.marker([48]), retry=True)[0])

    def test_automatic_changes_wait_six_hours(self):
        marker = self.marker([2])
        self.assertFalse(self.decide(self.confirmed(marker), marker)[0])

    def test_publish_now_bypasses_wait_but_still_counts(self):
        marker = self.marker([2])
        self.assertTrue(self.decide(self.confirmed(marker), marker, publish_now=True)[0])

    def test_daily_budget_includes_retries_and_manual_requests(self):
        marker = self.marker([20, 10])
        self.assertFalse(self.decide(self.confirmed(marker), marker, publish_now=True, retry=True)[0])

    def test_rolling_monthly_budget_includes_retries(self):
        marker = self.marker([48 * n for n in range(1, 13)])
        self.assertFalse(self.decide(self.confirmed(marker), marker, publish_now=True, retry=True)[0])

    def test_expired_rolling_budget_becomes_available(self):
        marker = self.marker([31 * 24])
        self.assertTrue(self.decide(self.confirmed(marker), marker)[0])

    def test_disabled_policy_holds_even_manual_requests(self):
        self.assertFalse(publication.decide(CANDIDATE, {}, {}, dict(POLICY, enabled=False), NOW, True, True)[0])

    def test_future_or_timezone_free_ledger_is_invalid(self):
        for at in ((NOW + timedelta(hours=1)).isoformat(), '2026-11-25T01:00:00'):
            with self.assertRaises(ValueError):
                self.decide({}, {'requests': [dict(at=at)]})

    def test_request_history_is_preserved_and_each_request_has_unique_identity(self):
        original = publication.make_request(CANDIDATE, {}, NOW - timedelta(days=2))
        before = copy.deepcopy(original)
        next_request = publication.make_request(CANDIDATE, original, NOW)
        self.assertNotEqual(original['requestId'], next_request['requestId'])
        self.assertEqual(len(next_request['requests']), 2)
        self.assertEqual(original, before)


class PublicFingerprint(unittest.TestCase):
    def test_internal_docs_and_release_ledger_do_not_change_website_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for folder in ('content', 'assets', 'scripts', 'docs'):
                (root / folder).mkdir()
            for path in ('scripts/build.py', 'scripts/reading.py', 'scripts/sources.py',
                         'scripts/math_render.py', 'scripts/validate.py', 'scripts/publication.py',
                         'requirements.txt', 'requirements.lock', 'netlify.toml'):
                (root / path).write_text('original', encoding='utf8')
            first = publication.website_fingerprint(root)
            for path in ('docs/notes.md', 'content/source-revisions.json', 'content/publishing-policy.json'):
                (root / path).write_text('new internal record', encoding='utf8')
            self.assertEqual(first, publication.website_fingerprint(root))
            (root / 'netlify.toml').write_text('changed production headers', encoding='utf8')
            self.assertNotEqual(first, publication.website_fingerprint(root))

    def test_only_provenance_changes_do_not_publish_but_actual_text_does(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'index.html'
            old, new = 'a' * 40, 'b' * 40
            path.write_text(f'<a href="/blob/{old}/rules.md">{old[:12]}</a>HP 75', encoding='utf8')
            first = publication.public_fingerprint(root, {'canon': {'commit': old}})
            path.write_text(f'<a href="/blob/{new}/rules.md">{new[:12]}</a>HP 75', encoding='utf8')
            (root / 'build.json').write_text('new timestamp and source commits', encoding='utf8')
            (root / 'validation.json').write_text('different section counters', encoding='utf8')
            self.assertEqual(first, publication.public_fingerprint(root, {'canon': {'commit': new}}))
            path.write_text(path.read_text().replace('HP 75', 'HP 80'), encoding='utf8')
            self.assertNotEqual(first, publication.public_fingerprint(root, {'canon': {'commit': new}}))

    def test_asset_additions_and_deletions_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'index.html').write_text('Public', encoding='utf8')
            first = publication.public_fingerprint(root, {})
            (root / 'art.png').write_bytes(b'new binary art')
            self.assertNotEqual(first, publication.public_fingerprint(root, {}))
            (root / 'art.png').unlink()
            self.assertEqual(first, publication.public_fingerprint(root, {}))


class QueueIntegration(unittest.TestCase):
    def run_case(self, published, dry_run=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'content').mkdir()
            (root / 'dist').mkdir()
            (root / 'content/public-manifest.json').write_text(json.dumps({'site': {'url': 'https://public.example'}}), encoding='utf8')
            (root / 'content/publishing-policy.json').write_text(json.dumps(POLICY), encoding='utf8')
            (root / 'dist/build.json').write_text(json.dumps(CANDIDATE), encoding='utf8')
            path = root / 'content/source-revisions.json'
            path.write_text('{}', encoding='utf8')
            def request(url, token=None):
                self.assertEqual(url, 'https://public.example/build.json')
                self.assertIsNone(token)
                if published is None:
                    raise OSError('Network unavailable')
                return json.dumps(published).encode()
            with patch.object(reconcile, 'ROOT', root), patch.object(reconcile, 'request', request):
                changed = reconcile.main(dry_run=dry_run)
            return changed, json.loads(path.read_text(encoding='utf8'))

    def test_dry_run_writes_no_marker_or_budget(self):
        self.assertEqual(self.run_case({}, True), (False, {}))

    def test_failed_live_check_writes_no_marker(self):
        self.assertEqual(self.run_case(None), (False, {}))

    def test_valid_change_writes_one_durable_request(self):
        changed, marker = self.run_case({})
        self.assertTrue(changed)
        self.assertEqual(marker['schemaVersion'], 2)
        self.assertEqual(len(marker['requests']), 1)

    def test_identical_output_writes_no_marker(self):
        self.assertEqual(self.run_case(CANDIDATE), (False, {}))
