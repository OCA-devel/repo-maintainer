# Copyright 2024 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import sys

from .utils import ConfLoader

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])

_logger = logging.getLogger(__name__)


class ConfFileManager:
    """Update existing configuration files."""

    def __init__(self, conf_dir):
        self.conf_dir = conf_dir
        self.conf_loader = ConfLoader(self.conf_dir)
        self.conf_repo = self.conf_loader.load_conf(
            "repo", checksum=False, by_filepath=True
        )

    def add_branch(self, branch, default=True):
        """Add a branch to all repositories in the configuration."""
        for filepath, repo in self.conf_repo.items():
            for repo_data in repo.values():
                if branch not in repo_data["branches"]:
                    repo_data["branches"].append(branch)
                if default:
                    repo_data["default_branch"] = branch
            self.conf_loader.save_conf(filepath, repo)
            _logger.info("Branch %s added to %s.", branch, filepath.as_posix())
