"""CLI entry point: python travel_planner.py --date YYYY-MM-DD."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from travel_planner.cli import main  # noqa: E402


if __name__ == "__main__":
    main()

