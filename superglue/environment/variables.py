import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# TODO: There has to be something better than this hack
program_name = Path(sys.argv[0]).parent.parts[-1]

if program_name == "pytest":
    load_dotenv(".test.env", override=True)
else:
    # load the environment file
    env_path = Path.cwd() / ".env"
    load_dotenv(env_path.as_posix())


SUPERGLUE_S3_BUCKET = os.getenv("SUPERGLUE_S3_BUCKET")
SUPERGLUE_IAM_ROLE = os.getenv("SUPERGLUE_IAM_ROLE")

# For simple account validation
try:
    SUPERGLUE_AWS_ACCOUNT = int(os.getenv("SUPERGLUE_AWS_ACCOUNT"))
except TypeError:
    SUPERGLUE_AWS_ACCOUNT = None

# keep this as we may want logging
SUPERGLUE_LOGGER_DIR = Path(os.getenv("SUPERGLUE_LOGGER_FILE", "./logs"))


def validate_environment() -> None:

    if not SUPERGLUE_S3_BUCKET:
        raise EnvironmentError("SUPERGLUE_S3_BUCKET not set in environment")

    if not SUPERGLUE_IAM_ROLE:
        raise EnvironmentError("SUPERGLUE_IAM_ROLE not set in environment")
