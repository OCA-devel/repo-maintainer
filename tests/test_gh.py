import os
import unittest
import unittest.mock

import github3

from oca_repo_maintainer.tools.manager import RepoManager


class TestGH(unittest.TestCase):
    def test_gh(self):
        print(os.getcwd())
        with unittest.mock.patch.object(github3, "login"):
            manager = RepoManager(os.getcwd() + "/conf", "dev", "ghp_123", True)
            manager.run()
