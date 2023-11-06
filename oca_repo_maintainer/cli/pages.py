# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import click

from ..tools.gh_pages import GHPageGenerator


@click.command()
@click.option("--conf-dir", required=True, help="Folder where configuration is stored")
@click.option("--path", required=True, help="Folder where pages must be generated")
@click.option(
    # FIXME: switch to OCA when ready
    "--org",
    default="OCA",
    prompt="Your organization",
    help="The organizattion.",
)
def pages(conf_dir, org, path):
    GHPageGenerator(conf_dir, org, path).run()


if __name__ == "__main__":
    pages()
