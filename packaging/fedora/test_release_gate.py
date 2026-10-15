"""Offline release-provenance decisions; no GitHub credentials or network."""
from copy import deepcopy
import unittest

from release_gate import WORKFLOW, eligible_pr, matching_run, successful_build


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.repository = 'owner/pure_live'
        self.pr = {
            'number': 7, 'merged_at': '2026-10-15T00:00:00Z',
            'merge_commit_sha': 'merged', 'head': {'sha': 'reviewed'},
            'base': {'ref': 'fedora', 'repo': {'full_name': self.repository}},
        }
        self.run = {
            'workflow_id': 10, 'path': WORKFLOW, 'event': 'pull_request',
            'status': 'completed', 'conclusion': 'success', 'head_sha': 'reviewed',
            'pull_requests': [deepcopy(self.pr)],
        }

    def test_build_job_itself_must_succeed(self):
        self.assertTrue(successful_build([{'name': 'build', 'status': 'completed', 'conclusion': 'success'}]))
        self.assertFalse(successful_build([]))
        for conclusion in ['skipped', 'failure', 'cancelled', None]:
            self.assertFalse(successful_build([{'name': 'build', 'status': 'completed', 'conclusion': conclusion}]))
        self.assertFalse(successful_build([{'name': 'other', 'status': 'completed', 'conclusion': 'success'}]))

    def test_exact_merged_pr_and_successful_head_are_accepted(self):
        self.assertTrue(eligible_pr(self.pr, self.repository, 'merged'))
        self.assertTrue(matching_run(self.run, self.pr, 10))

    def test_synthetic_merge_run_requires_exact_head_parent(self):
        self.run['head_sha'] = 'synthetic'
        self.assertFalse(matching_run(self.run, self.pr, 10))
        self.assertTrue(matching_run(self.run, self.pr, 10, ('base', 'reviewed')))
        self.assertFalse(matching_run(self.run, self.pr, 10, ('base', 'stale')))

    def test_stale_ci_head_is_rejected(self):
        self.run['head_sha'] = 'stale'
        self.run['pull_requests'][0]['head']['sha'] = 'stale'
        self.assertFalse(matching_run(self.run, self.pr, 10, ('base', 'reviewed')))

    def test_wrong_workflow_is_rejected(self):
        self.assertFalse(matching_run(self.run, self.pr, 11))
        self.run['path'] = '.github/workflows/unrelated.yml'
        self.assertFalse(matching_run(self.run, self.pr, 10))

    def test_wrong_base_or_repository_is_rejected(self):
        self.pr['base']['ref'] = 'master'
        self.assertFalse(eligible_pr(self.pr, self.repository, 'merged'))
        self.pr['base']['ref'] = 'fedora'
        self.assertFalse(eligible_pr(self.pr, 'other/pure_live', 'merged'))
        self.run['pull_requests'][0]['base']['ref'] = 'master'
        self.assertFalse(matching_run(self.run, self.pr, 10))

    def test_unmerged_pr_is_rejected(self):
        self.pr['merged_at'] = None
        self.assertFalse(eligible_pr(self.pr, self.repository, 'merged'))

    def test_direct_push_does_not_match_the_pr_merge_commit(self):
        self.assertFalse(eligible_pr(self.pr, self.repository, 'direct-push'))
        self.assertFalse(eligible_pr({}, self.repository, 'direct-push'))

    def test_failed_pending_or_non_pr_run_is_rejected(self):
        for field, value in [('conclusion', 'failure'), ('status', 'in_progress'), ('event', 'push')]:
            run = deepcopy(self.run)
            run[field] = value
            self.assertFalse(matching_run(run, self.pr, 10))

    def test_different_or_missing_pr_association_is_rejected(self):
        self.run['pull_requests'][0]['number'] = 8
        self.assertFalse(matching_run(self.run, self.pr, 10))
        self.run['pull_requests'] = []
        self.assertFalse(matching_run(self.run, self.pr, 10))


if __name__ == '__main__':
    unittest.main()
