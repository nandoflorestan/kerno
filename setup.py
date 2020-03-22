#!/usr/bin/env python3

"""Installer for kerno."""

from sys import version_info

# http://peak.telecommunity.com/DevCenter/setuptools#developer-s-guide
# from distutils.core import setup
from setuptools import setup, find_packages

if version_info[:2] < (3, 6):
    raise RuntimeError("Kerno requires Python 3.6+")

with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

setup(
    url="https://github.com/nandoflorestan/kerno",
    name="kerno",
    author="Nando Florestan",
    version="0.4.0",
    license="MIT",
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#using-find-packages
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    author_email="nandoflorestan@gmail.com",
    description="Framework for the application service layer, "
    "approximating Uncle Bob Martin's Clean Architecture.",
    long_description=long_description,
    zip_safe=False,
    test_suite="tests",
    install_requires=["bag>=3.0", "reg==0.11"],
    keywords=[
        "pyramid",
        "sqlalchemy",
        "service layer",
        "action",
        "Clean Architecture",
    ],
    classifiers=[  # https://pypi.org/pypi?:action=list_classifiers
        # "Development Status :: 3 - Alpha",
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Pyramid",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
