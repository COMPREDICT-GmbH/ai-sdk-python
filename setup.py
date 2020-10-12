import os
from setuptools import setup, find_packages


this_dir = os.path.dirname(__file__)

with open(os.path.join(this_dir, "README.md"), "rb") as fo:
    long_description = fo.read().decode("utf8")

with open(os.path.join(this_dir, 'requirements.txt')) as fo:
    requirements = fo.read().splitlines()

dev_requirements = [
    "flake8==3.8.3",
    'coverage==4.5.1'
]

setup(
    # Application name:
    name="COMPREDICT-AI-SDK",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="Ousama Esbel",
    author_email="esbel@compredict.de",

    # Packages
    packages=find_packages(),

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/compredict/ai-sdk-python",

    license="MIT",
    description="Connect Python applications with COMPREDICT AI Core.",
    keywords=["COMPREDICT", "AI", "SDK", "API", "rest"],
    long_description_content_type="text/markdown",
    long_description=long_description,

    # Dependent packages (distributions)
    install_requires=requirements,
    extras_require={
            'dev': dev_requirements
        }
)
