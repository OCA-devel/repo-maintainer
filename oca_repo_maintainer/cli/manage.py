# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import click

from ..tools.manager import RepoManager


@click.command()
@click.option("--conf-dir", required=True, help="Folder where configuration is stored")
@click.option(
    "--token", required=True, prompt="Your github token", envvar="GITHUB_TOKEN"
)
@click.option(
    "--org",
    default="OCA",
    prompt="Your organization",
    help="The organizattion.",
)
def manage(conf_dir, org, token):
    RepoManager(conf_dir, org, token).run()


if __name__ == "__main__":
    manage()
