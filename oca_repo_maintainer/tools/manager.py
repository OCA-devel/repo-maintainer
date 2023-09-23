# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


import logging
import shutil
import subprocess
import sys
import tempfile
from subprocess import CalledProcessError

import copier
import github3
import yaml
from github3.exceptions import NotFoundError

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])

_logger = logging.getLogger(__name__)


def check_call(cmd, cwd, log_error=True, extra_cmd_args=False, env=None):
    if extra_cmd_args:
        cmd += extra_cmd_args
    cp = subprocess.run(
        cmd,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=env,
    )
    if cp.returncode and log_error:
        _logger.error(
            f"command {cp.args} in {cwd} failed with return code {cp.returncode} "
            f"and output:\n{cp.stdout}"
        )
    cp.check_returncode()


class RepoManager:
    """Setup and update repositories and teams."""

    def __init__(self, conf_dir, org, token, test=False):
        self.test = test
        self.conf_dir = conf_dir
        self.token = token
        self.org = org
        self.gh = github3.login(token=token)
        self.gh_org = self.gh.organization(org)
        with open("%s/global.yml" % self.conf_dir, "r") as f:
            self.conf_data = yaml.safe_load(f.read())

        with open("%s/psc.yml" % self.conf_dir, "r") as f:
            self.psc_data = yaml.safe_load(f.read())

        with open("%s/repo.yml" % self.conf_dir, "r") as f:
            self.repositories_data = yaml.safe_load(f.read())
        self.new_repo_template = self.conf_data.get("template")

    def create_branch(self, repo, gh_repo, version):
        try:
            clone_dir = tempfile.mkdtemp()
            copier.run_copy(
                self.new_repo_template,
                clone_dir,
                defaults=True,
                unsafe=True,
                data={
                    "repo_name": repo,
                    "repo_slug": repo,
                    "repo_description": repo,
                    "odoo_version": version,
                },
            )
            check_call(
                ["git", "init"],
                cwd=clone_dir,
            )
            self._setup_user(clone_dir)
            check_call(
                ["git", "add", "-A"],
                cwd=clone_dir,
            )
            check_call(
                ["git", "commit", "-m", "Initial commit"],
                cwd=clone_dir,
            )
            check_call(
                ["git", "checkout", "-b", version],
                cwd=clone_dir,
            )
            check_call(
                ["git", "remote", "add", "origin", gh_repo.url],
                cwd=clone_dir,
            )
            check_call(
                [
                    "git",
                    "remote",
                    "set-url",
                    "--push",
                    "origin",
                    f"https://{self.token}@github.com/{self.org}/{repo}",
                ],
                cwd=clone_dir,
            )
            if not self.test:
                check_call(
                    ["git", "push", "origin", "HEAD"],
                    cwd=clone_dir,
                )
        except CalledProcessError:
            _logger.error("Something failed when the new repo was being created")
            raise
        finally:
            shutil.rmtree(clone_dir)

    def _setup_user(self, clone_dir):
        """Ensure user is properly configured on current repo."""
        gh_user = self.gh.me()
        try:
            name = subprocess.check_output("git config user.name".split(" ")).strip()
        except CalledProcessError:
            name = None
        if not name:
            check_call(
                ["git", "config", "user.name", gh_user.name or gh_user.login],
                cwd=clone_dir,
            )
        try:
            email = subprocess.check_output("git config user.email".split(" ")).strip()
        except CalledProcessError:
            email = None
        if not email:
            check_call(
                ["git", "config", "user.name", gh_user.name or gh_user.login],
                cwd=clone_dir,
            )

    def _process_psc(self):
        for team, data in self.psc_data.items():
            _logger.info("Generating team %s" % team)
            try:
                gh_team = self.gh_org.team_by_name(team)
            except NotFoundError:
                gh_team = self.gh_org.create_team(team, privacy="closed")
            members = data.get("members", []) + self.conf_data["maintainers"]
            representatives = data.get("representatives", [])
            done_members = []
            done_representatives = []
            for member in gh_team.members(role="member"):
                if member.login not in members:
                    if member.login not in representatives:
                        _logger.info("Revoking membership for %s" % member.login)
                        gh_team.revoke_membership(member.login)
                else:
                    done_members.append(member.login)
            for member in gh_team.members(role="maintainer"):
                if member.login not in representatives:
                    if member.login not in members:
                        _logger.info("Revoking membership for %s" % member.login)
                        gh_team.revoke_membership(member.login)
                else:
                    done_representatives.append(member.login)
            for member in members:
                if member not in done_members:
                    _logger.info("Adding membership to %s" % member)
                    gh_team.add_or_update_membership(member, role="member")
            for member in representatives:
                if member not in done_representatives:
                    _logger.info("Adding membership to %s" % member)
                    gh_team.add_or_update_membership(member, role="maintainer")

    def _process_org(self):
        repositories = self.gh_org.repositories()
        repo_keys = [repo.name for repo in repositories]
        gh_admin_team = self.gh_org.team_by_name(self.conf_data.get("owner"))
        gh_maintainer_teams = [
            self.gh_org.team_by_name(maintainer_team)
            for maintainer_team in self.conf_data.get("team_maintainers")
        ]
        team_repos = {}
        for repo, repo_data in self.repositories_data.items():
            if repo not in repo_keys:
                gh_repo = self.gh_org.create_repository(
                    repo, repo, team_id=gh_admin_team.id
                )
                for gh_maintainer_team in gh_maintainer_teams:
                    gh_maintainer_team.add_repository(
                        "{}/{}".format(self.org, repo), "admin"
                    )
                repo_branches = []
            else:
                gh_repo = self.gh.repository(self.org, repo)
                repo_branches = [branch.name for branch in gh_repo.branches()]
            if repo_data["psc"] not in team_repos:
                gh_team = self.gh_org.team_by_name(repo_data["psc"])
                team_repos[repo_data["psc"]] = {
                    "team": gh_team,
                    "repos": [repo.name for repo in gh_team.repositories()],
                }
            if repo not in team_repos[repo_data["psc"]]["repos"]:
                team_repos[repo_data["psc"]]["team"].add_repository(
                    "{}/{}".format(self.org, repo), "push"
                )
            for member in repo_data.get("maintainers", []):
                gh_repo.add_collaborator(member)
            for branch in repo_data.get("branches"):
                if str(branch) not in repo_branches:
                    self.create_branch(repo, gh_repo, str(branch))

    def run(self):
        self._process_psc()
        self._process_org()
