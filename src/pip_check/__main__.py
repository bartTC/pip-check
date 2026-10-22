"""
Run pip-check as `python -m pip_check`.

This works even when the `pip-check` console script isn't on PATH.
"""

from . import main

if __name__ == "__main__":
    main()
