"""Python Helper Modules."""
from setuptools import setup, find_namespace_packages
import pathlib


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="ron",
    install_requires=[],
    packages=find_namespace_packages(include=["ron.*"]),
    version="0.0.1",
    description="Python Helper Modules",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ronaldocpontes/python-notebooks",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={"": ["data/*.*"],},
    extras_require={"dev": ["pytest", "tox"]},
)
