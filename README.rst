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

Changelog
---------

v2.4.1 (master)
    - Cleanup of the entire codebase.
    - Added tests for Python 3.7 and 3.8.

v2.4 (2019-07-23):
    - Added support to only show packages from the ``user`` or ``local``
      package namespace.

v2.3.3 (2018-02-19):
    - Visual fixes around ``--show-update``

v2.3.2 (2018-02-18):
    - New ``--show-update`` argument.
    - Fixed ``--full-versions`` argument.
    - Minor UI improvements.

v2.1 (2018-02-18):
    - Complete new architecture. It now calls ``pip`` directly and parses
      it output which should be more reliable.
    - It's also using distutils for the version comparision now, which is
      more reliable as well.
    - Lots of features and bug fixes.

v0.2 (2016-02-09):
    - Fixes issues with older pip versions.
    - Truncates extremly long version numbers.

v0.1 (2016-02-06):
    - Very first version, and yet with very limited features.
