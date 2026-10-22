# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

The project uses `uv` for environment management and `nox` (with the uv venv backend) as the test runner.

```bash
uv sync                                  # Create .venv and install dev deps (nox, ruff)
uv run pip-check                         # Run the CLI from the working tree
uv run python -m pip_check               # Same, via __main__.py

uv run nox                               # Everything CI runs: lint, readme, smoke tests on 3.8–3.15, coverage
uv run nox -s lint                       # ruff check + ruff format --check on src and noxfile.py
uv run nox -s pip-check-test-py-3.12     # Smoke tests on a single Python version
uv run nox -s readme                     # Validate README.md parses as Markdown
uv run nox -s coverage                   # Coverage report (+ htmlcov/)
uv run nox -l                            # List sessions

uv build                                 # Build sdist + wheel
uvx uv-publish                           # Publish to PyPI
```

## Testing model

There is no unit test suite. `noxfile.py` holds the only tests: smoke tests that run the installed CLI end to end. The `pip-check-test-py-*` session installs deliberately old, pinned packages (`django==1.10`, `html5lib==0.999999999`, `pyglet==2.0.dev23`) so the major/minor/unknown tables all have rows. It then asserts that those version strings appear in the output and runs the CLI with combinations of flags, under both plain `pip` and `--cmd="uv pip"`. These sessions need network access, because pip queries PyPI.

When you add or change a CLI flag, add it to the flag combinations in both the `tests` and `coverage` sessions.

## Architecture

The whole tool lives in `src/pip_check/__init__.py`; `main()` is the console-script entry point.

Flow: `main()` parses args, then `run()` does the rest:
1. `get_pip_version()` prints the pip/uv version.
2. `get_package_versions(outdated_only=False)` loads the "unchanged" list. This step is skipped with `-H`.
3. `get_package_versions(outdated_only=True)` gets the outdated packages.
4. Each outdated package is classified with `packaging.version.Version` into `major`, `minor`, `unknown` (unparseable versions, or installed version newer than latest, e.g. pre-releases) or `unchanged`.
5. One `terminaltables` table is printed per non-empty category: `SingleTable`, or `AsciiTable` with `-a`.

Both helpers run pip through `run_pip()`, which prints the error and exits when the command can't start or returns non-zero. They parse `--format=json` output and call `sys.exit()` instead of raising.

**Pass-through arguments:** everything after the first `--` is split off `sys.argv` before argparse runs and stored in `options.pip_args`. It's appended verbatim (without `split_command()`) to both `pip list` calls, and shell-quoted into the `-u` upgrade command. pip-check doesn't validate it: a wrong option fails through `run_pip()`.

**pip vs. uv:** the command templates at the top of the module are separate for pip (`pip_*_cmd`) and uv (`uv_*_cmd`). The uv templates drop `--user`, `--local`, `--retries` and `--disable-pip-version-check`, and since uv has no `--uptodate`, the uv "current" list is a plain `uv pip list`. Flags that only work with pip say "(pip only)" in their help text. The code detects uv in two different ways: `get_package_versions` checks `pip_cmd.startswith("uv")`, while `get_pip_version` checks `"uv pip" in pip_cmd` and rewrites the command to `uv --version`. Keep both in mind when you touch uv handling.

## Conventions and gotchas

- **Old Python support is deliberate.** People on outdated Pythons need this tool to upgrade their code. Don't drop versions or raise `requires-python` (`>=3.8`; ruff infers its target from it). Keep `from __future__ import annotations` and avoid syntax or stdlib APIs from newer versions.
- **`pyproject.toml` must stay parseable by old pip.** pip < 19.3 only understands TOML 0.4, so use no dotted keys and write tables out in full. Otherwise building from the sdist fails on old setups.
- **Dependency lower bounds are about correctness**, not freshness (e.g. `packaging>=20.0` is needed for `Version.major`). Only raise them when the code really needs a newer API.
- **The sdist uses an explicit include list** (`[tool.hatch.build.targets.sdist]`). Any new file needed to build or test from the sdist has to be added there.
- **Ruff runs with `lint.select = ["ALL"]`** and only a few ignores. Justified exceptions use inline `# noqa: <CODE>` (e.g. `S603` on subprocess calls, `PLR0912`/`C901` on `run()`). Public functions have full docstrings.
- **The version is defined only in `pyproject.toml`.** `__version__` is read at import time via `importlib.metadata.version("pip-check")`, so the package must be installed (`uv sync`) for imports to work.
- **The PyPI long description is README.md plus CHANGELOG.md**, joined by `hatch-fancy-pypi-readme`. Both must stay valid Markdown. Changelog entries use the format `vX.Y (YYYY-MM-DD):` followed by bullet points.
- **The README's "Usage" block mirrors `pip-check -h`.** Update it when you change flags.
- **The Python versions in `pyproject.toml` classifiers and `python_versions` in `noxfile.py` should stay in sync.**
