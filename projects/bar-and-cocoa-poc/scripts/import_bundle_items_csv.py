#!/usr/bin/env python3
"""Regenerate data/real_inventory.json from a ShopiCoda CSV export."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bundle_csv import main  # noqa: E402

if __name__ == "__main__":
    main(sys.argv[1:])
