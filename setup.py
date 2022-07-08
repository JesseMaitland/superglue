from setuptools import setup, find_packages

__version__ = '0.0.0'

setup(
    name='glued',
    version=__version__,
    author='Jesse Maitland',
    discription='A cli tool to do some pretty rad stuff!',
    include_package_data=True,
    packages=find_packages(exclude=('tests*', 'venv')),
    entry_points={'console_scripts': ['glued = glued.__main__:main']},
    python_requires='>=3.8'
)
