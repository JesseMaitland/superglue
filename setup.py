from setuptools import setup, find_packages
from pathlib import Path

__version__ = '0.0.0'


def get_requirements() -> str:
    req_path = Path.cwd() / 'requirements' / "distribution.txt"
    return req_path.read_text()


setup(
    name='glued',
    version=__version__,
    author='Jesse Maitland',
    discription='A cli tool to do some pretty rad stuff!',
    include_package_data=True,
    install_requires=get_requirements(),
    packages=find_packages(exclude=('tests*', 'venv')),
    entry_points={'console_scripts': ['glued = glued.__main__:main']},
    python_requires='>=3.8'
)
