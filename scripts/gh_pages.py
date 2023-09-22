"""Script to generate gh pages
"""

import logging
from pathlib import Path

import utils

_logger = logging.getLogger("gh_pages")

OUTPUT = Path("docs/index.md")
PAGE_FOLDER = Path("docs")

INDEX_HEADER = """
# OCA repositories
"""


class GHPageGenerator:
    def __init__(self):
        self.output_path = OUTPUT
        self.page_folder = PAGE_FOLDER
        self.global_conf = utils.get_global_conf()
        self.psc_conf = utils.get_psc_conf()
        self.repo_conf = utils.get_repo_conf()

    def generate(self):
        repo_index = self._generate_repo_index()
        self.write(repo_index)
        self._generate_psc_pages()

    def _generate_repo_index(self):
        # TODO: generate index by repo
        # listing name, branches and psc names
        # PSC names link to psc page w/ members
        section = []
        for repo_name, data in self.repo_conf.items():
            if repo_name == ".github":
                continue
            if not data["name"]:
                _logger.error("Repo %s has no name", repo_name)
                continue
            section.append("## " + data["name"])
            section.append("Branches: " + ", ".join(data["branches"]))
            psc_slug = data["psc"]
            psc = self.psc_conf.get(psc_slug)
            link = self._make_link(
                psc["name"], self._make_psc_path(psc_slug).as_posix()
            )
            section.append("PSC: " + link)
            section.append("\n")
        return "\n".join([INDEX_HEADER, "\n" "\n".join(section)])

    def _generate_psc_pages(self):
        for psc_slug, data in self.psc_conf.items():
            psc_name = data["name"]
            section = []
            section.append("## " + psc_name)
            section.append("Members: " + self._link_users(*data["members"]))
            section.append(
                "Representatives: " + self._link_users(*data["representatives"])
            )
            content = "\n".join(section)
            self.write(content, self._make_psc_path(psc_slug))

    def _make_link(self, txt, href):
        return f"[{txt}]({href})"

    def _make_psc_path(self, psc_slug):
        return Path(f"docs/teams/{psc_slug}.md")

    def _link_users(self, *users):
        return ", ".join([f"@{x}" for x in users])

    def write(self, content, path=None):
        path = path or self.output_path
        with path.open("w") as fd:
            fd.write(content)


if __name__ == "__main__":
    generator = GHPageGenerator()
    generator.generate()
