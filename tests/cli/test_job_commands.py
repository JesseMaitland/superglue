from io import StringIO
from unittest.mock import patch, MagicMock
from superglue.cli import job


@patch("sys.stdout", new_callable=StringIO)
@patch("superglue.cli.job.SuperGlueJob")
@patch("superglue.cli.job.SuperGlueProject")
def test_job_new_command(
        mock_glue_project: MagicMock,
        mock_superglue_job: MagicMock,
        mock_stdout: MagicMock
) -> None:

    expected_success_message = "created new glue job config with name spam-eggs-beans"
    mock_cmd = MagicMock()
    mock_cmd.name = "spam-eggs-beans"
    job.new(mock_cmd)

    # assert that all objects are created
    assert mock_glue_project.return_value.called_once()
    assert mock_superglue_job.return_value.called_once()

    assert mock_stdout.getvalue().rstrip() == expected_success_message
