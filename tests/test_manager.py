# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
from unittest import TestCase, mock

from oca_repo_maintainer.tools.manager import RepoManager

from .common import conf_path, vcr


class TestManager(TestCase):
    def setUp(self):
        self.org = "OCA-devel"
        # IMPORTANT: when you want to record or update cassettes
        # you  must replace this token w/ a real one
        # before running tests.
        # SUPER IMPORTANT: after you do that,
        # replace the real token everywhere before staging changes
        self.token = "ghp_fake_test_token"
        self.manager = RepoManager(conf_path.as_posix(), self.org, self.token)

    def test_init(self):
        self.assertEqual(self.manager.org, self.org)
        self.assertEqual(self.manager.token, self.token)
        self.assertEqual(
            self.manager.conf_global,
            {
                "owner": "board",
                "template": "git+https://github.com/OCA/oca-addons-repo-template",
                "team_maintainers": [],
                "maintainers": [],
            },
        )
        self.assertEqual(
            self.manager.conf_psc,
            {
                "test-team-1": {
                    "name": "Test team 1",
                    "members": ["simahawk"],
                    "representatives": ["simahawk"],
                },
                "test-team-2": {
                    "name": "Test team 2",
                    "members": ["simahawk", "etobella"],
                    "representatives": ["etobella"],
                },
            },
        )
        self.assertEqual(
            self.manager.conf_repo,
            {
                "test-repo-1": {
                    "name": "Test repo 1",
                    "description": "Repo used to run real tests on oca-repo-manage tool.",
                    "psc": "test-team-1",
                    "maintainers": [],
                    "default_branch": "16.0",
                    "branches": ["16.0", "15.0"],
                },
                "test-repo-2": {
                    "name": "Repository 2",
                    "description": "Repo used to run real tests on oca-repo-manage tool.",
                    "psc": "test-team-2",
                    "maintainers": ["user3"],
                    "branches": ["13.0", "12.0"],
                },
            },
        )
        self.assertEqual(
            self.manager.new_repo_template, self.manager.conf_global["template"]
        )

    @vcr.use_cassette("setup_gh")
    def test_setup_gh(self):
        self.manager._setup_gh()
        self.assertTrue(self.manager.gh)
        self.assertEqual(
            self.manager.gh_org.url, "https://api.github.com/orgs/OCA-devel"
        )

    def test_process_psc(self):
        with vcr.use_cassette("setup_gh"):
            self.manager._setup_gh()
        with vcr.use_cassette("process_psc") as cassette:
            self.manager._process_psc()
        # check reques to get existing team
        expected_requests = (
            # check the 1st team that already exists
            {
                "url": "https://api.github.com/orgs/OCA-devel/teams/test-team-1",
                "method": "GET",
            },
            # get members
            {
                "url": "https://api.github.com/organizations/119798021/team/8630739/members?role=member&per_page=100",  # noqa
                "method": "GET",
            },
            # get maintainers
            {
                "url": "https://api.github.com/organizations/119798021/team/8630739/members?role=maintainer&per_page=100",  # noqa
                "method": "GET",
            },
            # set simahawk as member
            {
                "url": "https://api.github.com/organizations/119798021/team/8630739/memberships/simahawk",  # noqa
                "method": "PUT",
                "body": {"role": "member"},
            },
            # get team 2 which does NOT exist
            {
                "url": "https://api.github.com/orgs/OCA-devel/teams/test-team-2",  # noqa
                "method": "GET",
            },
            # create team
            {
                "url": "https://api.github.com/orgs/OCA-devel/teams",
                "method": "POST",
                "body": {
                    "name": "test-team-2",
                    "repo_names": [],
                    "maintainers": [],
                    "permission": "pull",
                    "privacy": "closed",
                },
            },
            # get members
            {
                "url": "https://api.github.com/organizations/119798021/team/8630747/members?role=member&per_page=100",  # noqa
                "method": "GET",
            },
            # get maintainers
            {
                "url": "https://api.github.com/organizations/119798021/team/8630747/members?role=maintainer&per_page=100",  # noqa
                "method": "GET",
            },
            # set simahawk as member
            {
                "url": "https://api.github.com/organizations/119798021/team/8630747/memberships/simahawk",  # noqa
                "method": "PUT",
                "body": {"role": "member"},
            },
            # set etobella as member
            {
                "url": "https://api.github.com/organizations/119798021/team/8630747/memberships/etobella",  # noqa
                "method": "PUT",
                "body": {"role": "member"},
            },
            # set etobella as maintainer
            {
                "url": "https://api.github.com/organizations/119798021/team/8630747/memberships/etobella",  # noqa
                "method": "PUT",
                "body": {"role": "maintainer"},
            },
        )
        for req, expected in zip(cassette.requests, expected_requests):
            for k in ("url", "method"):
                self.assertEqual(getattr(req, k), expected[k])
            if expected.get("body"):
                self.assertEqual(json.loads(req.body), expected["body"])
        with vcr.use_cassette("process_repositories") as cassette:
            with mock.patch.object(RepoManager, "push_branch"):
                self.manager._process_repositories()
