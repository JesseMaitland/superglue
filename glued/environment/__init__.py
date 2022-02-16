import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_S3_BUCKET = os.getenv('S3_BUCKET')
IAM_ROLE = os.getenv('IAM_ROLE')
