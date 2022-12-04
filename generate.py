import yaml
import github3
import sys
from github3.exceptions import NotFoundError
import logging
import tempfile
import subprocess
import copier
import shutil
from subprocess import CalledProcessError

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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


org = sys.argv[1]
token = sys.argv[2]
version = sys.argv[3]
admin_team = sys.argv[4]
maintainer_teams = ["core-maintainers"]
# maintainer_teams = []
new_repo_template = "git+https://github.com/OCA/oca-addons-repo-template"

with open("psc.yml", "r") as f:
    psc_data = yaml.safe_load(f.read())

with open("repo.yml", "r") as f:
    repositories_data = yaml.safe_load(f.read())

gh = github3.login(token=token)
gh_org = gh.organization(org)
repositories = gh_org.repositories()
repo_keys = [repo.name for repo in repositories]
for team, data in psc_data.items():
    _logger.info("Generating team %s" % team)
    try:
        gh_team = gh_org.team_by_name(team)
    except NotFoundError:
        gh_team = gh_org.create_team(team, privacy="closed")
    members = data.get("members", [])
    representatives = data.get("representatives", [])
    update_members = []
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
team_repos = {}
gh_admin_team = gh_org.team_by_name(admin_team)
gh_maintainer_teams = [gh_org.team_by_name(maintainer_team) for maintainer_team in maintainer_teams]
for repo, repo_data in repositories_data.items():
    if repo not in repo_keys:
        gh_repo = gh_org.create_repository(
            repo, repo, team_id=gh_admin_team.id
        )
        for gh_maintainer_team in gh_maintainer_teams:
            gh_maintainer_team.add_repository("%s/%s" % (org, repo), "admin")
        try:
            clone_dir = tempfile.mkdtemp()
            copier.run_auto(
                new_repo_template,
                clone_dir,
                defaults=True,
                data={
                    "repo_name": repo,
                    "repo_slug": repo,
                },
            )
            check_call(
                ["git", "init"],
                cwd=clone_dir,
            )
            gh_user = gh.me()
            check_call(
                ["git", "config", "user.name", gh_user.name or gh_user.login], cwd=clone_dir
            )
            email = gh_user.email
            if not email:
                for gh_mail in gh.emails():
                    if gh_mail.primary:
                        email = gh_mail.email
                        break
            check_call(
                ["git", "config", "user.email", email], cwd=clone_dir
            )
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
                    f"https://{token}@github.com/{org}/{repo}",
                ],
                cwd=clone_dir,
            )
            check_call(
                ["git", "push", "origin", "HEAD"],
                cwd=clone_dir,
            )
        except CalledProcessError as e:
            _logger.error("Something failed when the new repo was being created")
            raise
        finally:
            shutil.rmtree(clone_dir)
    else:
        gh_repo = gh.repository(org, repo)
    if repo_data["psc"] not in team_repos:
        gh_team = gh_org.team_by_name(repo_data["psc"])
        team_repos[repo_data["psc"]] = {"team": gh_team, "repos": [repo.name for repo in gh_team.repositories()]}
    if repo not in team_repos[repo_data["psc"]]["repos"]:
        team_repos[repo_data["psc"]]["team"].add_repository("%s/%s" % (org, repo), "push")
    for member in repo_data.get("maintainers", []):
        gh_repo.add_collaborator(member)
