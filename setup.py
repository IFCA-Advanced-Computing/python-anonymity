import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

VERSION = "0.0.1"
PACKAGE_NAME = "python-anonymity"
AUTHOR = "CSIC"
URL = "https://github.com/python-anonymity"  # TODO Añadir el enlace final
LICENSE = "Apache License"
DESCRIPTION = "Library which offers anonymization techniques and metrics to anonymize tabular datasets"
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")
LONG_DESC_TYPE = "text/markdown"

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    url=URL,
    install_requires=requirements,
    license=LICENSE,
    packages=setuptools.find_packages(),
    include_package_data=True,
)
