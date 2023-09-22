from setuptools import setup

install_requires = ["copier", "github3.py", "PyYAML", "click"]

tests_require = ["unitest"]


setup(
    name="oca_team_maintainer",
    version="0.0.1",
    description="Manage your Teams in Github",
    long_description="Manage your Teams in Github",
    author="Odoo Community Association",
    url="http://github.com/OCA/team-maintainer",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    # package_dir={"": ""},
    packages=["oca_team_maintainer", "oca_team_maintainer.tools"],
    include_package_data=True,
    license="LGPL-3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "oca-team-maintainer = oca_team_maintainer.tools.generate:generate",
        ]
    },
)
