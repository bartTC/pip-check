=========
pip-check
=========

Gives you a quick overview of all installed packages and their update status.
Very much like ``pip list -o`` but with colors. Inspired by `npm-check`_ though
lacks most of its features (yet).

Requires ``pip`` Version 6 or higher.

.. _npm-check: https://www.npmjs.com/package/npm-check

.. image:: http://d.pr/i/1e7wJ.png

Installation and Usage
----------------------

::

    $ pip install pip-check
    $ pip-check

Changelog
---------

v0.2 (2016-02-09):
    - Fixes issues with older pip versions.
    - Truncates extremly long version numbers.

v0.1 (2016-02-06):
    - Very first version, and yet with very limited features.
