#!/usr/bin/env python

"""pip-check.

pip-check gives you a quick overview of all installed packages and their
update status. Under the hood it calls `pip list --outdated --format=columns`
and transforms it into a more user friendly table.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import shlex
import subprocess
import sys
from collections import OrderedDict

import terminaltables
from packaging.version import Version

# ------------------------------------------------------------------------------
# Settings
# ------------------------------------------------------------------------------

# The `pip` command to run. Normally `pip` but you can specify
# it using the `--cmd=pip` argument.
pip_cmd = "pip"

# The complete command to run to get a JSON list of outdated packages
pip_not_required_arg = "--not-required"
pip_user_arg = "--user"
pip_local_arg = "--local"
pip_outdated_cmd = "{cmd} list --outdated --retries=1 --disable-pip-version-check --format=json {notreq_arg} {user_arg} {local_arg}"
pip_current_cmd = "{cmd} list --uptodate --retries=1 --disable-pip-version-check --format=json {notreq_arg} {user_arg} {local_arg}"
uv_outdated_cmd = "{cmd} list --outdated --format=json {notreq_arg}"
uv_current_cmd = "{cmd} list --format=json {notreq_arg}"

# Some pip packages such as pycryptopp have ridiculous long version
# # 0.6.0.1206569328141510525648634803928199668821045408958
# which messes up the table. These are capped by default to 10 characters.
# Can be overridden with -f.
version_length = 10

err = sys.stderr.write
out = sys.stdout.write


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------


def split_command(cmd: str) -> list[str]:
    """Split a command string into a list of properly escaped and quoted substrings.

    This function takes a single command string as input, splits it into substrings,
    and ensures each substring is properly escaped and shell-quoted. It leverages
    the `shlex.split` method to perform parsing and tokenization.

    Args:
        cmd (str): The command string to be split and quoted.

    Returns:
        list[str]: A list of shell-quoted substrings derived from the input command.

    """
    return [shlex.quote(s) for s in shlex.split(cmd)]


def get_pip_version(options: argparse.Namespace) -> str:
    """Retrieve the version of pip by executing the provided pip command.

    This function runs the pip command specified in the options parameter to fetch
    the current installed pip version. If the command execution fails or does not
    return a version string, the process will terminate with an error.

    Arguments:
        options (argparse.Namespace): A namespace object that encompasses the
            configurations needed for the command execution. This includes pip
            command to use, additional arguments for specifying package scope,
            and other related options.

    Returns:
        str: The output of the executed pip command, which includes the pip version.

    Raises:
        subprocess.CalledProcessError: If the pip command fails during execution.
        SystemExit: If the pip command execution fails or does not return a valid
                    version string.

    """
    cmd = f"{options.pip_cmd} --version"

    try:
        cmd_response = subprocess.run(  # noqa: S603
            split_command(cmd), capture_output=True, check=True, text=True
        )
    except subprocess.CalledProcessError as e:
        err(f"The pip command did not succeed: {e.stderr}")
        sys.exit(1)

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
) -> dict:
    """Fetch and parses the package version information using pip command.

    This function executes a pip command to retrieve the package versions,
    either limited to outdated packages or including all packages based on the
    outdated_only flag. The command is constructed based on the provided options
    and executed using subprocess. Results are captured and parsed from JSON
    for further processing. Errors during execution, connection issues, or JSON
    parsing errors are handled, and appropriate error messages are displayed
    to the user. The program will exit with relevant status codes upon encountering
    errors.

    Arguments:
        options (argparse.Namespace): A namespace object that encompasses the
            configurations needed for the command execution. This includes pip
            command to use, additional arguments for specifying package scope,
            and other related options.
        outdated_only (bool): Optional flag to determine whether to fetch only
            outdated packages (default is True) or all package versions.

    Returns:
        dict: A dictionary containing package version details parsed from the
              pip command output.

    Raises:
        SystemExit: Raised when execution of the pip command fails, HTTP
                    connection issues are detected, or JSON parsing fails.

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

    try:
        cmd_response = subprocess.run(  # noqa: S603
            split_command(cmd), check=False, capture_output=True, text=True
        )

    except subprocess.CalledProcessError as e:
        err(
            "The pip command did not succeed: {stderr}\n".format(
                stderr=e.stderr.decode("utf-8")
            )
        )
        sys.exit(1)

    # The pip command exited with 0 but we have stderr content:
    if cmd_response.stderr and "NewConnectionError" in cmd_response.stderr:
        err(
            "\npip indicated that it has connection problems. "
            "Please check your network.\n"
        )
        sys.exit(1)

    cmd_response_string = cmd_response.stdout.strip()

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


def main() -> None:  # noqa: C901 PLR0912 PLR0915  # Ignore too complex warning
    """Parse command-line arguments and show package list.

    Provides functionality for displaying and categorizing installed Python packages
    along with their update statuses. The program supports options to filter
    packages, show update instructions, and display formatted tables. Package
    classifications include major updates, minor updates, unchanged, and unknown
    statuses.
    """
    parser = argparse.ArgumentParser(
        description="A quick overview of all installed packages "
        "and their update status. Supports `pip` or `uv pip`."
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
    options = parser.parse_args()

    # The pip check factory
    current_pip_version = get_pip_version(options)

    # --------------------------------------------------------------------------

    sys.stdout.write(f"Python {sys.version}\n")
    sys.stdout.write(f"{current_pip_version}\n")

    sys.stdout.write("\nLoading package versions...\n")

    sys.stdout.flush()

    # Unchanged Packages
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
            # Unable to parse the version into anything useful
            packages["unknown"].append(package)
            continue

        # If the current version is larger than the latest
        # (e.g. a pre-release is installed) put it into the unknown section.
        # Technically its 'unchanged' but I guess its better to have
        # pre-releases stand out more.
        if current > latest:
            packages["unknown"].append(package)
            continue

        # Current and latest package version is the same. If this happens,
        # it's likely a bug with the version parsing.
        if current == latest:
            packages["unchanged"].append(package)
            continue

        # Major upgrade (first version number)
        if current.major < latest.major:
            packages["major"].append(package)
            continue

        # Everything else is a minor update
        packages["minor"].append(package)

    table_data = OrderedDict()

    def cut_version(version: str) -> str:
        if not version or version == "Unknown":
            return version

        # Cut version to readable length
        if not options.show_long_versions and len(version) > version_length + 3:
            return f"{version[:version_length]}..."
        return version

    def columns(package_data: dict) -> list[str] | None:
        # Generate the columns for the table(s) for each package
        # Name | Current Version | Latest Version | pypi String

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

    # Table output class
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
        for label in ("major", "minor"):
            if packages[label]:
                out(
                    "\nTo update all {label} releases run:\n\n"
                    "  {pip_cmd} install --upgrade {user}{packages}\n".format(
                        label=label,
                        pip_cmd=options.pip_cmd,
                        user="--user " if options.show_user is True else "",
                        packages=" ".join([p["name"] for p in packages[label]]),
                    )
                )


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()
