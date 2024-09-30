
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
* add new branches to existing YAML conf


## Available tools

* ``oca-repo-manage`` used to automatically maintain repositories based on YAML conf (see OCA conf below)
* ``oca-repo-pages`` used to automatically generate repo inventory docs from the same YAML conf
* ``oca-repo-add-branch`` used to manually add new branches to existing conf

## I can use it on my own organization?

Yes, you can. You just add the repo on your organization, add a secret called ORG_TOKEN on you secrets and modify the secrets with your information.

## OCA configuration

https://github.com/OCA/repo-maintainer-conf


## Bootstrap

You can use the script `scripts/bootstrap_data.py` to generate the conf out of existing repos. Run it with `--help` to see the options.

# Usage

## Manage repos

This action is normally performed via GH actions in the conf repo. You should not run it manually.

Yet, here's the command:


    oca-repo-manage --org $GITHUB_REPOSITORY_OWNER --token ${{secrets.GIT_PUSH_TOKEN}} --conf-dir ./conf

## Generate docs

This action is normally performed via GH actions in the conf repo. You should not run it manually.

Yet, here's the command:

    oca-repo-pages --org $GITHUB_REPOSITORY_OWNER --conf-dir conf --path docsource

## Add new branches to all repos

This action has to be performed manually when you need a new branch to be added to all repos in your conf.
Eg: when a new Odoo version is released.

Go to the conf repo on your file system and run this:

    oca-repo-add-branch --conf-dir ./conf/ --branch 18.0

Review, stage all the changes, commit and open a PR.

You can prevent this tool to edit a repo by adding ``manual_branch_mgmt`` boolean flag to repo's conf.

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
