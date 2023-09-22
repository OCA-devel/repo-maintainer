import os
import unittest
import unittest.mock

import github3

from oca_team_maintainer.generate import OcaTeamMaintainer


class TestGH(unittest.TestCase):
    def test_gh(self):
        print(os.getcwd())
        with unittest.mock.patch.object(github3, "login"):
            OcaTeamMaintainer(os.getcwd() + "/conf", "dev", "ghp_123", True)()
