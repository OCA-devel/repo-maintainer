# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""Script to bootstrap configuration files.

You must run this once to generate configuration files
out of existing OCA repos.
"""
import os
import pathlib

import click
import github3
import yaml

TOKEN = os.getenv("GITHUB_TOKEN")


def safe_name(repo):
    name = repo.description or repo.name
    return " ".join([x.capitalize() for x in name.split("-")])


def is_valid_branch(string):
    try:
        return float(string)
    except ValueError:
        return False


def prepare_psc(gh_org, conf_dir, whitelist=None):
    dest_dir = conf_dir / "psc"
    if not dest_dir.exists():
        os.makedirs(dest_dir.as_posix())
    teams = gh_org.teams()
    by_category = {}
    for team in teams:
        if team.slug in ["oca-contributors", "oca-members"]:
            continue
        if whitelist and not any([team.slug.startswith(x) for x in whitelist]):
            continue
        print("Processing team", team.slug)
        team_data = {"name": safe_name(team), "representatives": [], "members": []}
        for member in team.members(role="member"):
            if member.login in ["oca-travis", "oca-transbot", "OCA-git-bot"]:
                continue
            team_data["members"].append(member.login)
        for member in team.members(role="maintainer"):
            if member.login in ["oca-travis", "oca-transbot", "OCA-git-bot"]:
                continue
            team_data["representatives"].append(member.login)

        category_slug = team.slug.split("-")[0]
        if category_slug not in by_category:
            by_category[category_slug] = {}
        by_category[category_slug][team.slug] = team_data

    for category_slug, teams_data in by_category.items():
        with open(dest_dir / f"{category_slug}.yml", "w") as f:
            yaml.dump(teams_data, f)


def prepare_repo(gh_org, conf_dir, whitelist=None):
    dest_dir = conf_dir / "repo"
    if not dest_dir.exists():
        os.makedirs(dest_dir.as_posix())
    by_category = {}
    teams = []
    for repo in sorted(gh_org.repositories(), key=lambda x: x.name):
        if repo.name in (".github", "repo-maintainer", "repo-maintainer-conf"):
            continue
        if whitelist and not any([repo.name.startswith(x) for x in whitelist]):
            continue
        print("Processing repo", repo.name)
        psc = "board"
        psc_rep = "board"
        try:
            for team in repo.teams():
                if "core" in team.slug:
                    continue
                if "maintainers" in team.slug and "representative" not in team.slug:
                    psc = team.slug
                    teams.append(psc)
                    continue
                if "maintainers" in team.slug and "representative" in team.slug:
                    psc_rep = team.slug
                    teams.append(psc_rep)
                    continue
        except github3.exceptions.NotFoundError:
            pass
        name = safe_name(repo)
        branches = [b.name for b in repo.branches() if is_valid_branch(b.name)]
        category = repo.name.split("-")[0].capitalize()
        category_slug = category.lower()
        if category_slug not in by_category:
            by_category[category_slug] = {}
        by_category[category_slug][repo.name] = {
            "name": name,
            "category": category,
            "psc": psc,
            "psc_rep": psc_rep,
            "branches": branches,
            "default_branch": repo.default_branch,
        }

    for category_slug, repos in by_category.items():
        with open(dest_dir / f"{category_slug}.yml", "w") as f:
            yaml.dump(repos, f)

    return dict(teams=teams)


@click.command()
@click.option(
    # FIXME: switch to OCA when ready
    "--org",
    default="OCA",
    prompt="Your organization",
    help="The organizattion.",
)
@click.option("--conf-dir", required=True, help="Folder where configuration is stored")
@click.option(
    "--token", required=True, prompt="Your github token", envvar="GITHUB_TOKEN"
)
@click.option("--repo-whitelist", envvar="REPO_WHITELIST")
def generate(conf_dir, org, token, repo_whitelist=None):
    gh = github3.login(token=token)
    gh_org = gh.organization(org)
    conf_dir = pathlib.Path(conf_dir)
    if repo_whitelist:
        repo_whitelist = [x.strip() for x in repo_whitelist.split(",")]
    repo_result = prepare_repo(gh_org, conf_dir, whitelist=repo_whitelist)
    team_whitelist = None
    if repo_whitelist:
        team_whitelist = repo_result["teams"]
    prepare_psc(gh_org, conf_dir, whitelist=team_whitelist)


if __name__ == "__main__":
    generate()
