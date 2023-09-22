import click

from oca_team_maintainer.generate import OcaTeamMaintainer


@click.command()
@click.option("--folder", required=True, help="Folder where configuration is stored")
@click.option("--token", required=True, prompt="Your github token")
@click.option(
    "--org", default="OCA", prompt="Your organization", help="The organizattion."
)
def generate(folder, org, token):
    OcaTeamMaintainer(folder, org, token)()


if __name__ == "__main__":
    generate()
