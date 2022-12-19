from jobs.{{job}}.main import main
from typing import Callable

try:
    from jobs.{{job}}.py import *
except ImportError:
    pass

def test_job_{{job}}_main_is_callable() -> None:
    assert isinstance(main, Callable)
