"""Basic tests around pip-check."""

from __future__ import annotations

import nox

# uv-created venvs come without pip, so sessions that run pip-check against
# plain `pip` have to install it themselves.
nox.options.default_venv_backend = "uv"
nox.options.sessions = [
    "lint",
    "readme",
    "pip-check-test-py",
    "coverage",
]

# Keep in sync with the Python classifiers in pyproject.toml.
python_versions = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15"]


@nox.session(python=python_versions, name="pip-check-test-py")
def tests(session: nox.Session) -> None:
    """pip-check smoke tests."""
    # pip, so pip-check's default `pip` is this session's and not the host's;
    # uv for the `--cmd=uv pip` runs below.
    session.install("--upgrade", "pip", "uv")
    # Old pins guarantee rows in the update tables: Django and html5lib are
    # major updates, pyglet's dev release is a minor one.
    session.install("html5lib==0.999999999", "django==1.10", "pyglet==2.0.dev23")
    session.install(".")

    # silent=True makes run() return the output instead of only printing it.
    response = session.run("pip-check", silent=True)

    # Make sure, packages are actually listed
    assert "1.10" in response
    assert "0.999999999" in response
    assert "2.0.dev23" in response

    session.run("pip-check", "--help")
    session.run("pip-check", "--version")
    session.run(
        "pip-check",
        "--ascii",
        "--not-required",
        "--full-version",
        "--hide-unchanged",
        "--show-update",
    )
    session.run("pip-check", "--user")
    session.run("pip-check", "--local")

    # A missing pip executable must fail cleanly, not with a traceback.
    session.run("pip-check", "--cmd=pip-check-missing-pip", success_codes=[1])

    # Everything after `--` goes to `pip list`. --pre is issue #28, and an
    # option pip doesn't know proves the arguments actually arrive. A stray
    # word without `--` is still an argparse error (exit 2).
    session.run("pip-check", "--hide-unchanged", "--show-update", "--", "--pre")
    session.run("pip-check", "--", "--not-a-pip-option", success_codes=[1])
    session.run("pip-check", "stray-word", success_codes=[2])

    # The uv runs skip -r, -U and -l, which only work with pip.
    session.run("pip-check", "--cmd=uv pip")
    session.run("pip-check", "--cmd=uv pip", "--help")
    session.run(
        "pip-check", "--cmd=uv pip", "--ascii", "--full-version", "--hide-unchanged"
    )
    session.run(
        "pip-check",
        "--cmd=uv pip",
        "--hide-unchanged",
        "--",
        "--default-index",
        "https://pypi.org/simple",
    )


@nox.session
def coverage(session: nox.Session) -> None:
    """Run the final coverage report."""
    session.install("--upgrade", "coverage")
    # Editable, so the report points at src/ instead of a copy in site-packages.
    session.install("-e", ".")
    # Erase first, then --append, so the runs below add up to a single report.
    session.run("coverage", "erase")
    # No pip in this venv, so these runs inspect whichever pip comes first on
    # the host's PATH, and coverage numbers vary from machine to machine.
    session.run("coverage", "run", "--append", "-m", "pip_check")
    session.run("coverage", "run", "--append", "-m", "pip_check", "--version")
    session.run(
        "coverage",
        "run",
        "--append",
        "-m",
        "pip_check",
        "--ascii",
        "--not-required",
        "--full-version",
        "--hide-unchanged",
        "--show-update",
    )
    session.run("coverage", "report")
    session.run("coverage", "html")


@nox.session
def readme(session: nox.Session) -> None:
    """Readme Validation."""
    session.install("markdown-it-py")
    session.run("markdown-it", "README.md", "/dev/null", external=True)


@nox.session
def lint(session: nox.Session) -> None:
    """Ruff codebase linting and format check."""
    # ruff comes from the project's dev dependencies, not this session's venv,
    # so it's only on PATH when nox runs via `uv run nox`.
    session.run("ruff", "check", "src", "noxfile.py", external=True)
    session.run("ruff", "format", "--check", "src", "noxfile.py", external=True)
