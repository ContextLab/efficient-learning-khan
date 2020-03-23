# -*- coding: utf-8 -*-
from setuptools import setup

NAME = "khan_helpers"
VERSION = "0.0.1"
AUTHOR = "Paxton Fitzpatrick, Contextual Dynamics Lab"
AUTHOR_EMAIL = "contextualdynamics@gmail.com"
URL = "https://github.com/ContextLab/efficient-learning-khan"
DOWNLOAD_URL = URL
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.6"
DESCRIPTION = "Helper classes and functions for reproducing the analyses"

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    python_requires=PYTHON_REQUIRES,
    description=DESCRIPTION
)
