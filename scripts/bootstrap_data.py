# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""Script to bootstrap configuration files.

You must run this once to generate configuration files
out of existing OCA repos.
"""

import github3
import yaml

TOKEN = ""  # Fill this with your token

gh = github3.login(token=TOKEN)

oca = gh.organization("OCA")


def safe_name(name):
    return name or " ".join([x.capitalize() for x in name.splt("-")])


teams = oca.teams()
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


with open("../conf/psc.yml", "w") as f:
    yaml.dump(teams_data, f)


repos_data = {}
for repo in oca.repositories():
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
    }

with open("../conf/repo.yml", "w") as f:
    yaml.dump(repos_data, f)
