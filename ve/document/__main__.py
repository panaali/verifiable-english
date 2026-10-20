"""`python -m ve.document`, as `python -m` ran the module `ve/document.py` before AR-16a. Importing it (as
`pkgutil.walk_packages` does) runs nothing."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
