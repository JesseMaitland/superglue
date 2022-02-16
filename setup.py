from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(
    name='glued',
    version=VERSION,
    author='Jesse Maitland',
    discription='A cli tool to do some pretty rad stuff!',
    include_package_data=True,
    packages=find_packages(exclude=('tests*', 'venv')),
    entry_points={'console_scripts': ['glued = glued.__main__:main']},
    python_requires='>=3'
)
