from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grid.bootstrap import seed_required_grid_data
from grid.grid import GridServer


def main() -> None:
    """Seed the in-memory grid database and print a summary."""
    grid = GridServer()
    result = seed_required_grid_data(grid)

    print("Grid database seeded successfully.")
    print(f"Providers: {len(result['providers'])}")
    print(f"Franchises: {len(result['franchises'])}")
    print(f"Users: {len(result['users'])}")
    print("\nSample credentials for testing:")
    print(json.dumps(result["users"], indent=2))


if __name__ == "__main__":
    main()
