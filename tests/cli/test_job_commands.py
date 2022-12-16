# from io import StringIO
# from unittest.mock import patch, MagicMock
#
# import pytest
#
# from superglue.cli import job
#
#
# @patch("sys.stdout", new_callable=StringIO)
# @patch("superglue.cli.job.SuperGlueJob")
# @patch("superglue.cli.job.SuperGlueProject")
# def test_job_new_command(mock_glue_project: MagicMock, mock_superglue_job: MagicMock, mock_stdout: MagicMock) -> None:
#
#     expected_success_message = "created new glue job spam-eggs-beans"
#     mock_cmd = MagicMock()
#
#     # set return values
#     mock_cmd.name = "spam-eggs-beans"
#     mock_superglue_job.return_value.s3_script_path.return_value = "some-path"
#
#     with pytest.raises(SystemExit) as mock_exit:
#         job.new(mock_cmd)
#         assert mock_exit.called_once_with(0)
#
#         # assert glue project is created
#     assert mock_glue_project.return_value.called_once()
#
#     # assert superglue job created and methods called
#     assert mock_superglue_job.return_value.called_once()
#     assert mock_superglue_job.validate_name.called_once()
#     assert mock_superglue_job.create.called_once_with(
#         iam_role="some-iam-role", job_name="spam-eggs-beans", script_location="some-path"
#     )
#
#     assert mock_stdout.getvalue().rstrip() == expected_success_message
