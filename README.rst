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

    $ pip-check

    # If your terminal does not support the table lines,
    # you can show an ASCII table
    $ pip-check --ascii

    # You can specify the pip executable
    $ pip-check --cmd=pip3

    # List only packages that are not dependencies of installed packages.
    $ pip-check --not-required

    # Some packages have ridiculous long versions. To admire them:
    $ pip-check --full-version

    # Do not show packages where their version is up to date:
    $ pip-check --hide-unchanged

    # Show the pip command to update all major/minor packages
    $ pip-check --show-update

Changelog
---------

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
