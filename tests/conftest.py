import sys
from pathlib import Path

ACTIONS_DIR = Path(__file__).resolve().parent.parent / ".github" / "actions"
sys.path[:0] = [str(ACTIONS_DIR / "validate"), str(ACTIONS_DIR / "build-zone")]
