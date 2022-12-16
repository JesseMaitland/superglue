import sys
from pathlib import Path
_MODULES_DIR = Path.cwd() / "modules"

for zipfile in _MODULES_DIR.glob("**/*.zip"):
    sys.path.append(zipfile.as_posix())

