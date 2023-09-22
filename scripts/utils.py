from pathlib import Path

import yaml

conf_path = Path("conf")


def get_global_conf():
    with open(conf_path / "global.yml", "r") as f:
        return yaml.safe_load(f.read())


def get_psc_conf():
    with open(conf_path / "psc.yml", "r") as f:
        return yaml.safe_load(f.read())


def get_repo_conf():
    with open(conf_path / "repo.yml", "r") as f:
        return yaml.safe_load(f.read())
