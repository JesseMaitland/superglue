import sys
from pathlib import Path

for path in Path.cwd().joinpath("modules").iterdir():
    sys.path.append(path.as_posix())

sys.path.append(Path.cwd().joinpath("jobs").as_posix())
