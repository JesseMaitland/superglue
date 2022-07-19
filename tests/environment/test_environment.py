import os
from unittest.mock import patch, MagicMock
from glued.environment.variables import GLUED_S3_BUCKET, GLUED_IAM_ROLE


# @patch('glued.environment.variables.load_dotenv')
# def test_load_dotenv_called(patched_load_dotenv: MagicMock) -> None:
#     from glued.environment.variables import DEFAULT_S3_BUCKET, IAM_ROLE
#     patched_load_dotenv.assert_called_once()


def test_default_s3_bucket() -> None:
    assert GLUED_S3_BUCKET == "foo-bar-bucket"


def test_iam_role() -> None:
    assert GLUED_IAM_ROLE == "some-iam-role"
