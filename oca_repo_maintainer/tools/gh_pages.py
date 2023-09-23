# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""Script to generate gh pages
"""

from pathlib import Path

import yaml

INDEX_HEADER = """
OCA repositories
================
"""


class GHPageGenerator:
    def __init__(self, conf_dir, org, page_folder):
        self.conf_dir = conf_dir
        self.org = org
        with open("%s/global.yml" % self.conf_dir, "r") as f:
            self.global_conf = yaml.safe_load(f.read())

        with open("%s/psc.yml" % self.conf_dir, "r") as f:
            self.psc_conf = yaml.safe_load(f.read())

        with open("%s/repo.yml" % self.conf_dir, "r") as f:
            self.repo_conf = yaml.safe_load(f.read())
        self.page_folder = page_folder

    def run(self):
        # repo_index = self._generate_repo_index()
        # self.write(repo_index)
        self._generate_psc_page()
        self._generate_repo_page()

    def _generate_repo_page(self):
        section = ["Repositories", "============"]
        org = self.global_conf["org"]
        for repo_slug, data in self.repo_conf.items():
            repo_name = data["name"]
            if repo_name is None:
                continue
            section.append(repo_name)
            section.append("*" * len(repo_name))
            section.append("")
            section.append(f"https://github.com/{org}/{repo_slug}")
            section.append("")
            if data.get("psc", False):
                team_slug = data["psc"]
                team = self.psc_conf[team_slug]["name"]
                section.append(f"PSC: `{team} <teams.html#{team_slug}>`_")
                section.append("")
            if data.get("maintainers"):
                section.append("Members")
                section.append("-------")
                section.append("")
                for member in self._link_users(*data["maintainers"]):
                    section.append("* " + member)
                section.append("")

        content = "\n".join(section)
        self.write(content, Path("docsource/repos.rst"))

    def _generate_psc_page(self):
        section = ["Teams", "====="]
        for _psc_slug, data in self.psc_conf.items():
            psc_name = data["name"]
            section.append(psc_name)
            section.append("*" * len(psc_name))
            section.append("")
            section.append("Members")
            section.append("-------")
            section.append("")
            for member in self._link_users(*data["members"]):
                section.append("* " + member)
            section.append("")
            section.append("Representatives")
            section.append("---------------")
            section.append("")
            for member in self._link_users(*data["representatives"]):
                section.append("* " + member)
            section.append("")
        content = "\n".join(section)
        self.write(content, Path("docsource/teams.rst"))

    def _make_link(self, txt, href):
        return f"{txt} <{href}>"

    def _make_psc_path(self, psc_slug):
        return Path(f"docsource/{psc_slug}.rst")

    def _link_users(self, *users):
        return [f"`{x} <https://github.com/{x}>`_" for x in users]

    def write(self, content, path):
        with path.open("w") as fd:
            fd.write(content)
