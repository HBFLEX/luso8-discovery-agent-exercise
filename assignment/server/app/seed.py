"""
Load seed-dataset into memory
Author: Happy Banda
"""

import json
from pathlib import Path
from typing import Final

_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "leads_seed.json"

def _load() -> list[dict]:
    with _SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)

SEED_LEADS: Final[list[dict]] = _load()

