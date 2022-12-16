# from io import StringIO
# from unittest.mock import patch, MagicMock
# from superglue.cli.version import print_version, __version__
#
#
# @patch("sys.stdout", new_callable=StringIO)
# def test_version_number_is_printed(patched_stout: MagicMock) -> None:
#     print_version(MagicMock())
#     assert patched_stout.getvalue().rstrip() == __version__
