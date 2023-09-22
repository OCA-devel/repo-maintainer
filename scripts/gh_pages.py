"""Script to generate gh pages
"""

import logging
from pathlib import Path

import utils

_logger = logging.getLogger("gh_pages")

OUTPUT = Path("docsource/index.rst")
PAGE_FOLDER = Path("docsource")

INDEX_HEADER = """
OCA repositories
================
"""


class GHPageGenerator:
    def __init__(self):
        self.output_path = OUTPUT
        self.page_folder = PAGE_FOLDER
        self.global_conf = utils.get_global_conf()
        self.psc_conf = utils.get_psc_conf()
        self.repo_conf = utils.get_repo_conf()

    def generate(self):
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

    def write(self, content, path=None):
        path = path or self.output_path
        with path.open("w") as fd:
            fd.write(content)


if __name__ == "__main__":
    generator = GHPageGenerator()
    generator.generate()
