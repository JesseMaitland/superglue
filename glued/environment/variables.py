import os
import sys
from pathlib import Path
from dotenv import load_dotenv

program_name = Path(sys.argv[0]).parent.parts[-1]

if program_name == "pytest":
    load_dotenv(".test.env", override=True)
else:
    # load the environment file
    load_dotenv()

GLUED_S3_BUCKET = os.getenv("GLUED_S3_BUCKET")
GLUED_IAM_ROLE = os.getenv("GLUED_IAM_ROLE")

# for name validation
GLUED_JOB_PREFIX = os.getenv("GLUED_JOB_PREFIX", "")
GLUED_JOB_SUFFIX = os.getenv("GLUED_JOB_SUFFIX", "")

# keep this as we may want logging
GLUED_LOGGER_DIR = Path(os.getenv("GLUED_LOGGER_FILE", "./logs"))
GLUED_LOGGER_DIR.mkdir(exist_ok=True, parents=True)

