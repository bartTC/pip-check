.. image:: https://travis-ci.org/bartTC/pip-check.svg?branch=master
    :target: https://travis-ci.org/bartTC/pip-check

-----

=========
pip-check
=========

pip-check gives you a quick overview of all installed packages and their
update status. Under the hood it calls ``pip list --outdated --format=columns``
and transforms it into a more user friendly table.

.. important:: Requires ``pip`` Version 9 or higher!

.. image:: https://d.pr/i/ZDPuw5.png


Installation::

    pip install pip-check

Usage::

    $ pip-check -h
    usage: pip-check [-h] [-a] [-c PIP_CMD] [-l] [-r] [-f] [-H] [-u] [-U]

    A quick overview of all installed packages and their update status.

    optional arguments:
      -h, --help            show this help message and exit
      -a, --ascii           Display as ASCII Table
      -c PIP_CMD, --cmd PIP_CMD
                            The pip executable to run. Default: `pip`
      -l, --local           Show only virtualenv installed packages.
      -r, --not-required    List only packages that are not dependencies of
                            installed packages.
      -f, --full-version    Show full version strings.
      -H, --hide-unchanged  Do not show "unchanged" packages.
      -u, --show-update     Show update instructions for updatable packages.
      -U, --user            Show only user installed packages.

Testing::

    $ pip install tox tox-pyenv
    $ tox

Recommeded Similar Tools
------------------------

- `pip-date`_ - Show the installation or modification times of all your pip packages
- `pip-chill`_ - Lists only the dependencies (or not) of installed packages

.. _pip-date: https://github.com/E3V3A/pip-date
.. _pip-chill: https://github.com/rbanffy/pip-chill

Changelog
---------

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
