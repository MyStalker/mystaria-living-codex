"""One release queue for both upstream repositories and website implementation."""
import argparse
import json
import os
from datetime import datetime, timezone
from publication import decide, make_request
from sources import ROOT, request


def main(publish_now=False, retry=False, dry_run=False):
    config = json.loads((ROOT / 'content/public-manifest.json').read_text(encoding='utf8'))
    policy = json.loads((ROOT / 'content/publishing-policy.json').read_text(encoding='utf8'))
    candidate = json.loads((ROOT / 'dist/build.json').read_text(encoding='utf8'))
    marker_path = ROOT / 'content/source-revisions.json'
    marker = json.loads(marker_path.read_text(encoding='utf8')) if marker_path.exists() else {}
    try:
        published = json.loads(request(config['site']['url'] + '/build.json'))
    except Exception as exc:
        published = None
        print('Production verification unavailable: ' + type(exc).__name__)
    now = datetime.now(timezone.utc)
    allowed, reason = decide(candidate, published, marker, policy, now, publish_now, retry)
    result = 'Would request one release.' if allowed and dry_run else reason
    print(result)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf8') as handle:
            handle.write('## Codex publishing\n\n' + result + '\n\n'
                         + ('Dry run: no production request.\n' if dry_run else '')
                         + 'Limits: ' + str(policy['maxRequestsPer24Hours']) + ' requests / 24 hours; '
                         + str(policy['maxRequestsPer30Days']) + ' requests / 30 days.\n')
    if not allowed or dry_run:
        return False
    marker_path.write_text(json.dumps(make_request(candidate, marker, now), indent=2) + '\n', encoding='utf8')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish-now', action='store_true')
    parser.add_argument('--retry', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    main(args.publish_now, args.retry, args.dry_run)
