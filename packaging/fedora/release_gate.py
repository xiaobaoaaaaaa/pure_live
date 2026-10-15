"""Fail closed unless this release push came from an exactly checked Fedora PR.

Run only from the merged fedora commit with read-only permissions. Publication
has its own job and token; PR code never runs with that write token.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


WORKFLOW = '.github/workflows/fedora-rpm.yml'


def eligible_pr(pr, repository, commit):
    return (
        pr.get('merged_at') is not None
        and pr.get('merge_commit_sha') == commit
        and pr.get('base', {}).get('ref') == 'fedora'
        and pr.get('base', {}).get('repo', {}).get('full_name') == repository
        and bool(pr.get('head', {}).get('sha'))
    )


def matching_run(run, pr, workflow_id, parents=()):
    if not (
        run.get('workflow_id') == workflow_id
        and run.get('path') == WORKFLOW
        and run.get('event') == 'pull_request'
        and run.get('status') == 'completed'
        and run.get('conclusion') == 'success'
    ):
        return False
    head = pr['head']['sha']
    associated = any(
        item.get('number') == pr['number']
        and item.get('head', {}).get('sha') == head
        and item.get('base', {}).get('ref') == 'fedora'
        for item in run.get('pull_requests', [])
    )
    # Some GitHub run responses identify the synthetic PR merge commit. Accept
    # it only with both the exact associated PR head and its Git parent link.
    return associated and (run.get('head_sha') == head or (len(parents) == 2 and head in parents))


def main():
    repository = os.environ['GH_REPO']
    commit = os.environ['SOURCE_COMMIT']
    token = os.environ['GH_TOKEN']
    root = f'https://api.github.com/repos/{repository}/'

    def get(path):
        request = Request(root + path, headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'pure-live-fedora-release-gate',
        })
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    prs = get(f'commits/{commit}/pulls?per_page=100')
    candidates = [pr for pr in prs if eligible_pr(pr, repository, commit)]
    if not candidates:
        raise SystemExit('Release gate rejected: push is not a merged Fedora PR commit.')
    workflow = get('actions/workflows/fedora-rpm.yml')
    if workflow.get('path') != WORKFLOW:
        raise SystemExit('Release gate rejected: unexpected workflow path.')
    for pr in candidates:
        page = 1
        while True:
            query = urlencode({
                'event': 'pull_request', 'status': 'success',
                'created': '>=' + pr['created_at'], 'per_page': 100, 'page': page,
            })
            runs = get(f'actions/workflows/{workflow["id"]}/runs?{query}')['workflow_runs']
            for run in runs:
                parents = ()
                # Avoid a commit lookup unless the PR-head association matches.
                if run.get('head_sha') != pr['head']['sha'] and any(
                    item.get('number') == pr['number'] and item.get('head', {}).get('sha') == pr['head']['sha']
                    for item in run.get('pull_requests', [])
                ):
                    parents = tuple(item['sha'] for item in get(f'commits/{run["head_sha"]}')['parents'])
                if matching_run(run, pr, workflow['id'], parents):
                    evidence = f'PR #{pr["number"]}, head {pr["head"]["sha"]}, successful run {run["html_url"]}'
                    print('Release gate approved: ' + evidence)
                    if summary := os.environ.get('GITHUB_STEP_SUMMARY'):
                        with open(summary, 'a') as output:
                            output.write('Release provenance: ' + evidence + '\n')
                    return
            if len(runs) < 100:
                break
            page += 1
    raise SystemExit('Release gate rejected: no successful Fedora RPM PR run for the exact merged PR head.')


if __name__ == '__main__':
    main()
