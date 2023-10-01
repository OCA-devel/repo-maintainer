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


def safe_name(name):
    return name or " ".join([x.capitalize() for x in name.split("-")])


def prepare_psc(gh_org, conf_dir):
    dest_dir = conf_dir / "psc"
    if not dest_dir.exists():
        os.makedirs(dest_dir.as_posix())
    teams = gh_org.teams()
    teams_data = {}
    for team in teams:
        if team.slug in ["oca-contributors", "oca-members"]:
            continue
        team_data = {"name": safe_name(team.name), "representatives": [], "members": []}
        for member in team.members(role="member"):
            if member.login in ["oca-travis", "oca-transbot", "OCA-git-bot"]:
                continue
            team_data["members"].append(member.login)
        for member in team.members(role="maintainer"):
            if member.login in ["oca-travis", "oca-transbot", "OCA-git-bot"]:
                continue
            team_data["representatives"].append(member.login)
        teams_data[team.slug] = team_data

    for team_slug, team_data in teams_data.items():
        with open(dest_dir / f"{team_slug}.yml", "w") as f:
            yaml.dump({team_slug: team_data}, f)


def prepare_repo(gh_org, conf_dir):
    dest_dir = conf_dir / "repo"
    if not dest_dir.exists():
        os.makedirs(dest_dir.as_posix())
    repos_data = {}
    for repo in gh_org.repositories():
        if repo.name in (".github", "repo-maintainer", "repo-maintainer-conf"):
            continue
        psc = "board"
        try:
            for team in repo.teams():
                if team.slug not in ["board"]:
                    psc = team.slug
                    break
        except github3.exceptions.NotFoundError:
            pass
        name = safe_name(repo.description)
        repos_data[repo.name] = {
            "name": name,
            "psc": psc,
            "branches": [b.name for b in repo.branches()],
            "default_branch": repo.default_branch,
        }

    for repo_slug, repo_data in repos_data.items():
        with open(dest_dir / f"{repo_slug}.yml", "w") as f:
            yaml.dump({repo_slug: repo_data}, f)


@click.command()
@click.option(
    # FIXME: switch to OCA when ready
    "--org",
    default="OCA-devel",
    prompt="Your organization",
    help="The organizattion.",
)
@click.option("--conf-dir", required=True, help="Folder where configuration is stored")
@click.option(
    "--token", required=True, prompt="Your github token", envvar="GITHUB_TOKEN"
)
def generate(conf_dir, org, token):
    gh = github3.login(token=token)
    gh_org = gh.organization(org)
    conf_dir = pathlib.Path(conf_dir)
    prepare_psc(gh_org, conf_dir)
    prepare_repo(gh_org, conf_dir)


if __name__ == "__main__":
    generate()
