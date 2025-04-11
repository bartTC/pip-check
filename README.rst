.. image:: https://travis-ci.org/bartTC/pip-check.svg?branch=master
    :target: https://travis-ci.org/bartTC/pip-check

-----

=========
pip-check
=========

pip-check gives you a quick overview of all installed packages and their
update status. Under the hood it calls ``pip list --outdated --format=columns``
and transforms it into a more user friendly table.

pip-check also supports uv, or pip at any location. Pass the `pip`
command using ``--cmd``::

    pip-check -c pip
    pip-check -c ".venv/bin/pip"
    pip-check -c "uv pip"

.. image:: https://d.pr/i/ZDPuw5.png

Installation::

    pip install pip-check

The last version that runs on Python 2.7 or 3.4 is v2.5.2. Install it with::

    pip install pip-check==2.5.2

Usage::

    $ pip-check -h
    usage: __init__.py [-h] [-a] [-c PIP_CMD] [-l] [-r] [-f] [-H] [-u] [-U]

    A quick overview of all installed packages and their update status. Supports `pip` or `uv pip`.

    options:
      -h, --help            show this help message and exit
      -a, --ascii           Display as ASCII Table
      -c, --cmd PIP_CMD     The [uv] pip executable to run. E.g.: `/path/to/pip` or `uv pip`. Default: `pip`
      -l, --local           Show only virtualenv installed packages. (pip only)
      -r, --not-required    List only packages that are not dependencies of installed packages. (pip only)
      -f, --full-version    Show full version strings.
      -H, --hide-unchanged  Do not show "unchanged" packages.
      -u, --show-update     Show update instructions for updatable packages. (pip only)
      -U, --user            Show only user installed packages. (pip only)

Testing:

Test against a variation of Python versions::

    $ pip install tox tox-pyenv
    $ tox

Test against your current Python version::

    $ python setup.py test

Recommeded Similar Tools
------------------------

- `pip-date`_ - Show the installation or modification times of all your pip packages
- `pip-chill`_ - Lists only the dependencies (or not) of installed packages

.. _pip-date: https://github.com/E3V3A/pip-date
.. _pip-chill: https://github.com/rbanffy/pip-chill

Changelog
---------

v3.0 (2025-04-11):

- Added support for ``uv``. Use ``--cmd="uv pip"`` to utilize uv.

v2.10 (2025-04-11):

- Resolve the issue of missing line breaks when no packages are found.
- Test against Python 3.13.

v2.9 (2024-09-01):

- Show current Python and pip version upon load.
- Test against Python 3.12.

v2.8.1 (2022-11-06):

- Fixes issue with packages not correctly sorted into "Major" category.

v2.8 (2022-11-06):

- Added support for Python 3.11.
- Replaced deprecated "distutils" with "packaging" module.

v2.7 (2021-11-16):

- Drop support for Python 2.7, 3.4 and 3.5
- Added support for Python 3.9 and 3.10.
- Removed 'colorclass' as a dependency and with that the shell argument
  `--disable-colors`.

v2.6 (2019-12-12):

- Requires Python 3.5 or higher.
- Command error is shown if pip exits with a status code 1 (or larger).
- Error message is shown if pip is not able to load packages in case of
  network problems.
- Update instructions will now add ``--user`` in case the pip-check command
  should only show user packages as well.

v2.5.2 (2019-08-08):

- This is the last version that runs on Python 2.7. Install it with
  ``pip install pip-check==2.5.2``
- Windows color fixes.

v2.5.1 (2019-08-08):

- Windows script fixes.

v2.5 (2019-08-08):

- A more robust installation that installs pip-check as a proper console script.
- Added new ``--disable-colors`` argument.
- Added tests for Python 3.7 and 3.8.
- Fixed Syntax warning happening with no outdated packages.
- Cleanup of the entire codebase.

v2.4 (2019-07-23):

- Added support to only show packages from the ``user`` or ``local`` package
  namespace.

v2.3.3 (2018-02-19):

- Visual fixes around ``--show-update``

v2.3.2 (2018-02-18):

- New ``--show-update`` argument.
- Fixed ``--full-versions`` argument.
- Minor UI improvements.

v2.1 (2018-02-18):

- Complete new architecture. It now calls ``pip`` directly and parses it output
  which should be more reliable.
- It's also using distutils for the version comparision now, which is more
  reliable as well.
- Lots of features and bug fixes.

v0.2 (2016-02-09):

- Fixes issues with older pip versions.
- Truncates extremly long version numbers.

v0.1 (2016-02-06):

- Very first version, and yet with very limited features.
