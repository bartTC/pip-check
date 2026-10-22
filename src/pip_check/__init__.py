#!/usr/bin/env python

"""
Show installed Python packages grouped by how far behind their latest release they are.

pip-check is a thin layer over `pip list --format=json` (or `uv pip list`).
It runs the list command once for outdated packages and, unless
`--hide-unchanged` is given, once more for up-to-date ones. It then sorts
the results into major, minor, unchanged and unknown updates and prints one
table per group.

Everything lives in this module and runs top to bottom from `main()`. The
helpers print an error and call `sys.exit()` instead of raising, because
nothing can recover from a failed pip command anyway.

Old Python versions (3.8+) are supported on purpose: people stuck on
outdated environments are the ones who need this tool to upgrade. Avoid
newer syntax and stdlib APIs.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from collections import OrderedDict
from importlib.metadata import version

import terminaltables
from packaging.version import Version

__version__ = version("pip-check")

# The `pip` command to run. Normally `pip` but you can specify
# it using the `--cmd=pip` argument. It's resolved via PATH, so it's whichever
# `pip` comes first there, not necessarily the one of the Python running
# pip-check.
pip_cmd = "pip"

# `pip list` command templates. `--retries=1` makes an offline run give up
# quickly instead of going through pip's default 5 retries, and
# `--disable-pip-version-check` skips pip's own self-update lookup.
pip_not_required_arg = "--not-required"
pip_user_arg = "--user"
pip_local_arg = "--local"
pip_outdated_cmd = "{cmd} list --outdated --retries=1 --disable-pip-version-check --format=json {notreq_arg} {user_arg} {local_arg}"
pip_current_cmd = "{cmd} list --uptodate --retries=1 --disable-pip-version-check --format=json {notreq_arg} {user_arg} {local_arg}"

# uv's `pip list` has no `--uptodate`, `--user` or `--local`. Without
# `--uptodate`, the "current" list contains *all* packages, outdated ones too.
uv_outdated_cmd = "{cmd} list --outdated --format=json {notreq_arg}"
uv_current_cmd = "{cmd} list --format=json {notreq_arg}"

# Some pip packages such as pycryptopp have ridiculous long version
# strings like 0.6.0.1206569328141510525648634803928199668821045408958
# which messes up the table. These are capped by default to 10 characters.
# Can be overridden with -f.
max_version_length = 10

err = sys.stderr.write
out = sys.stdout.write


def split_command(cmd: str) -> list[str]:
    """
    Turn a command string such as `uv pip list --outdated` into an argv list.

    `--cmd` accepts a whole command (`uv pip`, `/path/to/pip`), so the string
    is split with shell rules and passed to `subprocess.run` as a list, never
    through a shell. Splitting follows POSIX rules, so backslashes are treated
    as escapes, and those in Windows paths get dropped.

    Each token is also passed through `shlex.quote`. That leaves plain tokens
    untouched, but a token containing spaces or shell metacharacters gets
    wrapped in literal quotes, no longer matches a real path, and the command
    fails to start.
    """
    return [shlex.quote(s) for s in shlex.split(cmd)]


def run_pip(
    cmd: str, extra_args: list[str] | None = None
) -> subprocess.CompletedProcess[str]:
    """
    Run a pip command and return the finished process with its text output.

    `extra_args` are appended to the command as they are, without going
    through `split_command`. They come from the shell already split, and
    re-splitting or quoting them could mangle values such as index URLs.

    pip-check can't do anything useful once the pip command fails, so this
    prints the reason and exits with status 1 instead of raising. That covers
    a command that can't be started (a typo in `--cmd`, a missing or
    non-executable file) as well as a non-zero exit code, whose empty stdout
    would otherwise look like an empty package list. A pip option that pip
    doesn't know, passed through by the user, ends up here as well.

    Exit code 0 doesn't guarantee success, though. pip reports network
    problems only on stderr, so callers that need a working index connection
    have to check stderr themselves.
    """
    try:
        cmd_response = subprocess.run(  # noqa: S603
            split_command(cmd) + (extra_args or []),
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError as e:
        err(f"Unable to run the pip command `{cmd}`: {e.strerror}\n")
        sys.exit(1)

    if cmd_response.returncode != 0:
        err(f"The pip command did not succeed: {cmd_response.stderr}\n")
        sys.exit(1)

    return cmd_response


def get_pip_version(options: argparse.Namespace) -> str:
    """
    Return the version line of the pip or uv in use, e.g. `pip 25.0 from ...`.

    This is the first command pip-check runs, so it doubles as an early check
    that `--cmd` works at all. Any failure exits through `run_pip`. An empty
    response exits with status 1 as well, since a working pip always prints
    its version.
    """
    # `uv pip --version` is an error; uv reports its version via `uv --version`.
    # Replacing just "uv pip" keeps any path prefix, e.g. `/opt/bin/uv pip`.
    if "uv pip" in options.pip_cmd:
        cmd = f"{options.pip_cmd.replace('uv pip', 'uv')} --version"
    else:
        cmd = f"{options.pip_cmd} --version"

    cmd_response = run_pip(cmd)
    cmd_response_string = cmd_response.stdout.strip()

    if not cmd_response_string:
        err(
            "The pip command did not return a version string. "
            "Does `pip --version` work for you?"
        )
        sys.exit(1)

    return cmd_response_string


def get_package_versions(
    options: argparse.Namespace, *, outdated_only: bool = True
) -> list[dict]:
    """
    Run `pip list` and return its parsed JSON package list.

    With `outdated_only`, this lists packages that have a newer release on the
    index, each including a `latest_version`. Without it, it lists up-to-date
    packages, which only carry `name` and `version`. The command is treated
    as uv if it starts with `uv`. uv gets the same scope flags except `--user`
    and `--local`, which it doesn't have.

    Arguments given after `--` on the command line (`options.pip_args`) are
    appended to both variants. That's how pre-releases (`--pre`) and other
    indexes (`--extra-index-url`) get included. pip-check doesn't interpret
    them, so they have to be valid for the pip or uv in use: uv spells
    index options differently and has no `--pre` for `pip list`.

    Both variants look up every installed package on the index, which makes
    this the slow part of a run. A failing command, a connection problem or
    output that isn't JSON prints an error and exits with status 1.
    """
    if outdated_only:
        check_cmd = (
            uv_outdated_cmd if options.pip_cmd.startswith("uv") else pip_outdated_cmd
        )
    else:
        check_cmd = (
            uv_current_cmd if options.pip_cmd.startswith("uv") else pip_current_cmd
        )

    cmd = check_cmd.format(
        cmd=options.pip_cmd,
        notreq_arg=pip_not_required_arg if options.pip_not_required else "",
        user_arg=pip_user_arg if options.show_user else "",
        local_arg=pip_local_arg if options.show_local else "",
    )

    cmd_response = run_pip(cmd, options.pip_args)

    # pip doesn't fail when PyPI is unreachable: it logs retry warnings to
    # stderr, exits with 0 and prints `[]`, which would read as "all up to date".
    if cmd_response.stderr and "NewConnectionError" in cmd_response.stderr:
        err(
            "\npip indicated that it has connection problems. "
            "Please check your network.\n"
        )
        sys.exit(1)

    cmd_response_string = cmd_response.stdout.strip()

    # pip and uv print `[]` for an empty list, so this only triggers if the
    # command printed nothing at all.
    if not cmd_response_string:
        err("No outdated packages. \\o/")
        sys.exit(0)

    try:
        pip_packages = json.loads(cmd_response_string)
    except json.JSONDecodeError:
        err(
            "Unable to parse the version list from pip. "
            "Does `pip list --format=json` work for you?\n"
        )
        sys.exit(1)

    return pip_packages


def run(options: argparse.Namespace) -> None:  # noqa: PLR0912, PLR0915, C901
    """
    Collect package versions and print the update report.

    The Python and pip versions come first, which makes it easy to spot a
    `--cmd` that points at a different environment than expected. The
    "Loading" line is flushed before the slow pip calls start, so the user
    sees something happen.

    Outdated packages are grouped by comparing their installed and latest
    versions. A higher first version component is a major update, and any
    other increase is minor. Missing or unparseable versions go to "unknown",
    and so do installed versions newer than the latest release (usually
    pre-releases), so they stand out. The up-to-date list from pip makes up
    the "unchanged" group.

    Each non-empty group is printed as its own table, in the order major,
    minor, unchanged, unknown. With `--show-update`, outdated rows show an
    install command instead of the PyPI link, and the report ends with one
    upgrade command per group.
    """
    current_pip_version = get_pip_version(options)
    sys.stdout.write(f"Python {sys.version}\n")
    sys.stdout.write(f"{current_pip_version}\n")
    sys.stdout.write("\nLoading package versions...\n")
    sys.stdout.flush()

    # Unchanged Packages. `--uptodate` looks up every package on PyPI just like
    # `--outdated`, so skipping this with -H saves a second round of requests.
    unchanged = []
    if not options.hide_unchanged:
        unchanged = get_package_versions(options, outdated_only=False)

    packages = {
        "major": [],
        "minor": [],
        "unknown": [],
        "unchanged": unchanged,
    }

    # Fetch all outdated packages and sort them into major/minor/unknown.
    for package in get_package_versions(options, outdated_only=True):
        # No version info
        if "latest_version" not in package or "version" not in package:
            packages["unknown"].append(package)
            continue

        try:
            latest = Version(package["latest_version"])
            current = Version(package["version"])
        except ValueError:
            # Unable to parse the version into anything useful. Since packaging
            # 22 that's any non-PEP 440 version (e.g. "2004d"); its
            # InvalidVersion is a ValueError subclass.
            packages["unknown"].append(package)
            continue

        # If the current version is larger than the latest
        # (e.g. a pre-release is installed) put it into the unknown section.
        # Technically its 'unchanged' but I guess its better to have
        # pre-releases stand out more.
        if current > latest:
            packages["unknown"].append(package)
            continue

        # The current and latest package version is the same. If this happens,
        # it's likely a bug with the version parsing.
        if current == latest:
            packages["unchanged"].append(package)
            continue

        # Major upgrade (first version number). Bumps within 0.x (0.9 -> 0.10)
        # count as minor, even though those are often breaking.
        if current.major < latest.major:
            packages["major"].append(package)
            continue

        # Everything else is a minor update
        packages["minor"].append(package)

    table_data = OrderedDict()

    def cut_version(v: str | None) -> str | None:
        """
        Shorten very long version strings so they don't blow up the table.

        `--full-version` turns this off. `None` and "Unknown" pass through
        unchanged, so the caller can substitute its own placeholder.
        """
        if not v or v == "Unknown":
            return v

        # Cut version to readable length. The `+ 3` makes sure the cut version,
        # "..." included, is actually shorter than the original.
        if not options.show_long_versions and len(v) > max_version_length + 3:
            return f"{v[:max_version_length]}..."
        return v

    def columns(package_data: dict) -> list[str] | None:
        """
        Build one table row: name, installed version, latest version and a hint.

        The hint is the package's PyPI page or, with `--show-update`, the pip
        command that installs the latest version.
        """
        name = package_data.get("name")
        current_version = package_data.get("version")
        latest_version = package_data.get("latest_version")
        help_string = "https://pypi.python.org/pypi/{}".format(package_data["name"])

        if latest_version and options.show_update:
            help_string = "pip install {user}{name}=={version}".format(
                user="--user " if options.show_user is True else "",
                name=name,
                version=latest_version,
            )

        # Up-to-date packages have no `latest_version`, so the installed
        # version doubles as the latest one.
        return [
            name,
            cut_version(current_version) or "Unknown",
            cut_version(latest_version) or current_version or "Unknown",
            help_string,
        ]

    for key, label, _ in [
        ("major", "Major Release Update", "autored"),
        ("minor", "Minor Release Update", "autoyellow"),
        ("unchanged", "Unchanged Packages", "autogreen"),
        ("unknown", "Unknown Package Release Status", "autoblack"),
    ]:
        if packages[key]:
            if key not in table_data:
                table_data[key] = []

            (table_data[key].append([label, "Version", "Latest"]),)
            for line_package in packages[key]:
                table_data[key].append(columns(line_package))

    # SingleTable draws its lines with terminal escape sequences, which show up
    # as garbage like "(0x(B" in CI logs and other non-terminal output. -a avoids that.
    table_class = (
        terminaltables.AsciiTable if options.ascii_only else terminaltables.SingleTable
    )

    for data in table_data.values():
        out("\n")
        table = table_class(data)
        out(table.table)
        out("\n")
        sys.stdout.flush()

    if options.show_update:
        # The pass-through args are needed here too: without `--pre`, for
        # example, `pip install --upgrade` never picks the pre-release listed
        # above. Unlike for the pip calls, quoting is right here, because the
        # user pastes this into a shell.
        extra = f"{shlex.join(options.pip_args)} " if options.pip_args else ""
        for label in ("major", "minor"):
            if packages[label]:
                out(
                    "\nTo update all {label} releases run:\n\n"
                    "  {pip_cmd} install --upgrade {user}{extra}{packages}\n".format(
                        label=label,
                        pip_cmd=options.pip_cmd,
                        user="--user " if options.show_user is True else "",
                        extra=extra,
                        packages=" ".join([p["name"] for p in packages[label]]),
                    )
                )


def main() -> None:
    """
    Parse the command line and print the report.

    This is the `pip-check` console script's entry point, and `python -m
    pip_check` calls it too. `--version` exits before any pip command runs.
    Everything after the first `--` is split off before argparse runs and
    stored in `options.pip_args` for `pip list`. Ctrl-C during the pip calls, which are often slow, exits quietly with
    status 130 instead of printing a traceback.
    """
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] [-- PIP_ARGS ...]",
        description="A quick overview of all installed packages "
        "and their update status. Supports `pip` or `uv pip`.",
        epilog="Arguments after `--` are passed to `pip list` as they are, "
        "e.g. `pip-check -- --pre` to include pre-releases, or "
        "`pip-check -- --extra-index-url URL` to also check another index. "
        "With uv, use uv's options, e.g. `-- --index URL`. They are also added "
        "to the --show-update command.",
    )
    parser.add_argument(
        "-a",
        "--ascii",
        action="store_true",
        dest="ascii_only",
        default=False,
        help="Display as ASCII Table",
    )
    parser.add_argument(
        "-c",
        "--cmd",
        dest="pip_cmd",
        default=pip_cmd,
        help="The [uv] pip executable to run. E.g.: `/path/to/pip` or `uv pip`. Default: `pip`",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        dest="show_local",
        default=False,
        help="Show only virtualenv installed packages. (pip only)",
    )
    parser.add_argument(
        "-r",
        "--not-required",
        action="store_true",
        dest="pip_not_required",
        default=False,
        help="List only packages that are not dependencies of installed packages. (pip only)",
    )
    parser.add_argument(
        "-f",
        "--full-version",
        action="store_true",
        dest="show_long_versions",
        default=False,
        help="Show full version strings.",
    )
    parser.add_argument(
        "-H",
        "--hide-unchanged",
        action="store_true",
        dest="hide_unchanged",
        default=False,
        help='Do not show "unchanged" packages.',
    )
    parser.add_argument(
        "-u",
        "--show-update",
        action="store_true",
        dest="show_update",
        default=False,
        help="Show update instructions for updatable packages. (pip only)",
    )
    parser.add_argument(
        "-U",
        "--user",
        action="store_true",
        dest="show_user",
        default=False,
        help="Show only user installed packages. (pip only)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        dest="show_version",
        default=False,
        help="Show the version of pip-check and exit.",
    )

    # Everything after `--` goes to `pip list` as it is, so any pip option
    # works without pip-check having to mirror it. The split happens before
    # argparse, which would otherwise also accept stray words without `--`.
    argv = sys.argv[1:]
    pip_args = []
    if "--" in argv:
        separator = argv.index("--")
        argv, pip_args = argv[:separator], argv[separator + 1 :]

    options = parser.parse_args(argv)
    options.pip_args = pip_args

    if options.show_version:
        sys.stdout.write(f"pip-check version {__version__}\n")
        sys.exit(0)

    # Handled here rather than at the call site, so Ctrl-C exits quietly for
    # the `pip-check` console script and `python -m pip_check` alike.
    # 130 is 128 + SIGINT, the shell convention for "interrupted by Ctrl-C".
    try:
        run(options)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
