from superglue.environment.variables import SUPERGLUE_S3_BUCKET, SUPERGLUE_IAM_ROLE, SUPERGLUE_JOB_SUFFIX, SUPERGLUE_JOB_PREFIX


def test_default_s3_bucket() -> None:
    assert SUPERGLUE_S3_BUCKET == "some-bucket"


def test_iam_role() -> None:
    assert SUPERGLUE_IAM_ROLE == "some-iam-role"


def test_glued_prefix() -> None:
    assert SUPERGLUE_JOB_PREFIX == "some_prefix__"


def test_glued_suffix() -> None:
    assert SUPERGLUE_JOB_SUFFIX == "some_suffix__"
