from superglue.environment.variables import (
    SUPERGLUE_S3_BUCKET,
    SUPERGLUE_IAM_ROLE
)


def test_default_s3_bucket() -> None:
    assert SUPERGLUE_S3_BUCKET == "some-bucket"


def test_iam_role() -> None:
    assert SUPERGLUE_IAM_ROLE == "some-iam-role"
