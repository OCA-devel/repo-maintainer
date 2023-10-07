# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""Script to generate gh pages
"""

from pathlib import Path

from .utils import ConfLoader

INDEX_HEADER = """
OCA repositories
================
"""


class GHPageGenerator:
    def __init__(self, conf_dir, org, page_folder):
        self.conf_dir = conf_dir
        self.conf_loader = ConfLoader(conf_dir)
        self.org = org
        self.conf_global = self.conf_loader.load_conf("global")
        self.conf_psc = self.conf_loader.load_conf("psc")
        self.conf_repo = self.conf_loader.load_conf("repo")
        self.page_folder = page_folder

    def run(self):
        # repo_index = self._generate_repo_index()
        # self.write(repo_index)
        self._generate_psc_pages()
        self._generate_repo_pages()

    def _repo_by_category(self):
        """Group repos by category.

        As you can have tons of repos let's organize them by category
        to generate pages by category.
        """
        res = {}
        for repo_slug, data in self.conf_repo.items():
            cat = data.get("category") or "Uncategorized"
            res.setdefault(cat, []).append((repo_slug, data))
        return res

    def _generate_repo_pages(self):
        """Generate one page per category."""
        org = self.conf_global["org"]
        repo_by_category = self._repo_by_category()
        for categ, repos in repo_by_category.items():
            header = categ
            section = [header, len(header) * "="]
            for repo_slug, data in repos:
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
                    team = self.conf_psc[team_slug]["name"]
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
                self.write(content, Path(f"docsource/{categ.lower()}.rst"))

        content = """
Repositories
============

.. toctree::
   :maxdepth: 1

"""
        categories = list(repo_by_category.keys())
        no_cat = "Uncategorized"
        if no_cat in categories:
            # move uncategorized repos at the end
            categories.remove(no_cat)
            categories.append(no_cat)

        for categ in categories:
            content += f"   {categ.lower()}\n"
        self.write(content, Path("docsource/repos.rst"))

    def _generate_psc_pages(self):
        section = ["Teams", "====="]
        for _psc_slug, data in self.conf_psc.items():
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
