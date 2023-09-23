import click

from ..tools.manager import RepoManager


@click.command()
@click.option("--conf-dir", required=True, help="Folder where configuration is stored")
@click.option("--token", required=True, prompt="Your github token")
@click.option(
    "--org", default="OCA", prompt="Your organization", help="The organizattion."
)
def manage(conf_dir, org, token):
    RepoManager(conf_dir, org, token).run()


if __name__ == "__main__":
    manage()
