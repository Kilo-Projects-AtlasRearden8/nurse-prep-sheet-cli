"""Entry point for `python -m nurse_prep_sheet`."""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
