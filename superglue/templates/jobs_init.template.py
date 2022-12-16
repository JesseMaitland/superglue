import sys
from pathlib import Path

_JOBS_DIR = Path.cwd() / "jobs"
sys.path.append(_JOBS_DIR.as_posix())

