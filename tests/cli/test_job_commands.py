from io import StringIO
from unittest.mock import patch, MagicMock
from superglue.cli import job


@patch("sys.stdout", new_callable=StringIO)
@patch("superglue.cli.job.Template")
@patch("superglue.cli.job.SuperGlueJob")
@patch("superglue.cli.job.TemplateController")
@patch("superglue.cli.job.SuperGlueProject")
def test_job_new_command(
        mock_glue_project: MagicMock,
        mock_template_controller: MagicMock,
        mock_superglue_job: MagicMock,
        mock_jinja_template: MagicMock,
        mock_stdout: MagicMock
) -> None:

    expected_success_message = "created new glue job config with name spam-eggs-beans"
    mock_cmd = MagicMock()
    mock_cmd.name = "spam-eggs-beans"
    job.new(mock_cmd)

    # assert that all objects are created
    assert mock_template_controller.return_value.called_once()
    assert mock_glue_project.return_value.called_once()
    assert mock_superglue_job.return_value.called_once()

    # assert template content was called
    assert mock_template_controller.get_template_content.called_once_with("job_config.template.yml")

    assert mock_stdout.getvalue().rstrip() == expected_success_message