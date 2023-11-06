
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/repo-maintainer&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/repo-maintainer/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/repo-maintainer/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/repo-maintainer/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/repo-maintainer/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/repo-maintainer/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/repo-maintainer)
[![Translation Status](https://translation.odoo-community.org/widgets/repo-maintainer-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/repo-maintainer-16-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Repo maintainer

This tool allows to manage repositories and teams via via YAML configuration.
Features:

* create/update repositories
* create/update teams and roles
* create/update branches

## I can use it on my own organization?

Yes, you can. You just add the repo on your organization, add a secret called ORG_TOKEN on you secrets and modify the secrets with your information.

## OCA configuration

https://github.com/OCA/repo-maintainer-conf


## Bootstrap

You can use the script `scripts/bootstrap_data.py` to generate the conf out of existing repos.

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
