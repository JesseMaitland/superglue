from superglue.environment.variables import GLUED_S3_BUCKET, GLUED_IAM_ROLE, GLUED_JOB_SUFFIX, GLUED_JOB_PREFIX


def test_default_s3_bucket() -> None:
    assert GLUED_S3_BUCKET == "some-bucket"


def test_iam_role() -> None:
    assert GLUED_IAM_ROLE == "some-iam-role"


def test_glued_prefix() -> None:
    assert GLUED_JOB_PREFIX == "some_prefix__"


def test_glued_suffix() -> None:
    assert GLUED_JOB_SUFFIX == "some_suffix__"
