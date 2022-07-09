import os
from pathlib import Path
from dotenv import load_dotenv

# load the environment file
load_dotenv()

DEFAULT_S3_BUCKET = os.getenv("S3_BUCKET")
IAM_ROLE = os.getenv("IAM_ROLE")

GLUED_LOGGER_DIR = Path(os.getenv("GLUED_LOGGER_FILE", './logs'))
GLUED_LOGGER_DIR.mkdir(exist_ok=True, parents=True)
