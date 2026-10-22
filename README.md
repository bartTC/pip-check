[![Testsuite](https://github.com/bartTC/pip-check/actions/workflows/test.yml/badge.svg)](https://github.com/bartTC/pip-check/actions/workflows/test.yml)
[![PyPi Version](https://img.shields.io/pypi/v/pip-check
)](https://pypi.org/project/pip-check/)
![Monthly Downloads](https://img.shields.io/pypi/dm/pip-check
)

# pip-check

pip-check gives you a quick overview of all installed packages and their
update status. Under the hood it calls `pip list --outdated --format=json`
and transforms it into a more user-friendly table.

pip-check also supports uv, or pip at any location. Pass the `pip`
command using `--cmd`:

```
pip-check -c pip3
pip-check -c ".venv/bin/pip"
pip-check -c "uv pip"
```

![Screenshot of pip-check in action](https://d.pr/i/ZDPuw5.png)

## Installation:

```
pip install pip-check
```
    
Or Install the last version that runs on Python 2.7 or 3.4:

```
pip install pip-check==2.5.2
```  

## Usage:

```bash
$ pip-check -h
usage: pip-check [options] [-- PIP_ARGS ...]

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
  --version             Show the version of pip-check and exit.

Arguments after `--` are passed to `pip list` as they are, e.g. `pip-check -- --pre` to include pre-releases, or `pip-check -- --extra-index-url URL` to also check another index. With uv, use uv's
options, e.g. `-- --index URL`. They are also added to the --show-update command.
```

## Pre-releases and other package indexes:

Everything after `--` is passed to `pip list` unchanged, so pip-check can use
any of pip's options:

```
pip-check -- --pre                                        # include pre-releases
pip-check -- --extra-index-url https://my.index/simple    # also check another index
pip-check -- --index-url https://mirror.example/simple    # check a mirror instead of PyPI
pip-check -c "uv pip" -- --index https://my.index/simple  # uv uses its own option names
```

The same arguments are added to the upgrade command that `--show-update`
prints, so e.g. a listed pre-release actually gets installed. uv's `pip list`
has no pre-release option, so `--pre` only works with pip.

pip's own configuration applies as well, so a `pip.conf` or environment
variables such as `PIP_PRE=1` or `PIP_EXTRA_INDEX_URL` work without `--`.

## Local Development

pip-check uses `uv` for local development.

```
uv sync         # Create a .venv and install dependencies
uv build        # Build distribution packages
```

### Releasing:

Releases are published to PyPI by GitHub Actions. Bump `version` in
`pyproject.toml`, add the CHANGELOG entry, then push a matching tag:

```bash
$ git tag v3.3 && git push origin v3.3
```

The Publish workflow checks that the tag matches the project version, runs
the full test suite and uploads the package using PyPI Trusted Publishing.

### Testing:

Test against a variation of Python versions:

```bash
$ uv run nox
```

## Recommended Similar Tools

- [pip-date](https://github.com/E3V3A/pip-date) - Show the installation or modification times of all your pip packages
- [pip-chill](https://github.com/rbanffy/pip-chill) - Lists only the dependencies (or not) of installed packages
