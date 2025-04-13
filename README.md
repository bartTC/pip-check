# pip-check

pip-check gives you a quick overview of all installed packages and their
update status. Under the hood it calls `pip list --outdated --format=columns`
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
```

## Local Development

pip-check uses `uv` for local development.

```
$ pip install -U uv
uv sync     # Create a .venv and install dependencies
uv build    # Build distribution packages
uv publish  # Publish on Pypi
```

### Testing:

Test against a variation of Python versions:

```bash
$ uv run nox
```

## Recommended Similar Tools

- [pip-date](https://github.com/E3V3A/pip-date) - Show the installation or modification times of all your pip packages
- [pip-chill](https://github.com/rbanffy/pip-chill) - Lists only the dependencies (or not) of installed packages
