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
    # FIXME: switch to OCA when ready
    "--org",
    default="OCA",
    prompt="Your organization",
    help="The organizattion.",
)
@click.option("--force", is_flag=True, default=False)
def manage(conf_dir, org, token, force):
    RepoManager(conf_dir, org, token, force=force).run()


if __name__ == "__main__":
    manage()
