#!/usr/bin/env python3
"""SnapSolve entry point."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.main import App


def main() -> None:
    App().run()


if __name__ == "__main__":
    main()
