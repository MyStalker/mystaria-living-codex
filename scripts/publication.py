"""Stable public-artifact identity and a conservative, shared release budget."""
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path


def digest(files):
    result = hashlib.sha256()
    for name, data in files:
        for value in (name.encode('utf8'), data):
            result.update(len(value).to_bytes(8, 'big'))
            result.update(value)
    return result.hexdigest()


def website_fingerprint(root):
    root = Path(root)
    paths = []
    for folder in ('assets', 'content'):
        paths.extend(p for p in (root / folder).rglob('*') if p.is_file())
    paths.extend(root / p for p in (
        'scripts/build.py', 'scripts/reading.py', 'scripts/sources.py',
        'scripts/math_render.py', 'scripts/validate.py', 'scripts/publication.py',
        'requirements.txt', 'requirements.lock', 'netlify.toml'))
    excluded = {'source-revisions.json', 'publishing-policy.json'}
    return digest((p.relative_to(root).as_posix(), p.read_bytes())
                  for p in sorted(set(paths)) if p.name not in excluded)


def public_fingerprint(stage, revisions):
    """Count page/search/download/asset changes, excluding provenance-only churn."""
    stage = Path(stage)
    commits = sorted({v['commit'] for v in revisions.values()})
    files = []
    for path in sorted(stage.rglob('*')):
        if not path.is_file() or path.name in {'build.json', 'validation.json'}:
            continue
        data = path.read_bytes()
        if path.suffix.lower() in {'.html', '.json', '.md', '.xml', '.txt'}:
            for commit in commits:
                data = data.replace(commit.encode(), b'SOURCE_REVISION')
                data = data.replace(commit[:12].encode(), b'SOURCE_SHORT_REVISION')
        files.append((path.relative_to(stage).as_posix(), data))
    return digest(files)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Release times must include a timezone')
    return parsed.astimezone(timezone.utc)


def decide(candidate, published, marker, policy, now, publish_now=False, retry=False):
    """Unknown state never implicitly authorizes spending."""
    if not policy.get('enabled', False):
        return False, 'Automatic publishing is held by publishing-policy.json.'
    if published is None:
        return False, 'Production status could not be verified; no release requested.'
    keys = ('publicContentSha256', 'websiteInputsSha256')
    if all(published.get(k) == candidate[k] for k in keys):
        return False, 'Public content and website implementation already match production.'
    if marker.get('schemaVersion') == 2:
        confirmed = published.get('publicationId') == marker.get('requestId')
        if not confirmed and not retry:
            return False, 'Previous release is unconfirmed; inspect Netlify, then explicitly retry.'
    dates = [timestamp(item['at']) for item in marker.get('requests', [])]
    if any(t > now for t in dates):
        raise ValueError('Release history contains a future timestamp')
    daily = sum(t > now - timedelta(days=1) for t in dates)
    monthly = sum(t > now - timedelta(days=30) for t in dates)
    if daily >= policy['maxRequestsPer24Hours']:
        return False, 'Release budget reached: maximum requests per rolling 24 hours.'
    if monthly >= policy['maxRequestsPer30Days']:
        return False, 'Release budget reached: maximum requests per rolling 30 days.'
    if dates and not publish_now and now - max(dates) < timedelta(hours=policy['minimumIntervalHours']):
        return False, 'Changes are batched until the minimum automatic release interval passes.'
    return True, 'Validated public changes are ready for one production release.'


def make_request(candidate, marker, now):
    import uuid
    history = [item for item in marker.get('requests', [])
               if timestamp(item['at']) > now - timedelta(days=120)]
    identifier = str(uuid.uuid4())
    at = now.isoformat()
    return dict(schemaVersion=2, requestId=identifier, requestedAt=at,
                publicContentSha256=candidate['publicContentSha256'],
                websiteInputsSha256=candidate['websiteInputsSha256'],
                revisions={k: v['commit'] for k, v in candidate['repositories'].items()},
                requests=history + [dict(id=identifier, at=at)])
