from setuptools import setup, find_packages

# Read in the README for the long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ai-commit-gen",
    version="0.1",
    packages=find_packages(),
    scripts=["ai-commit.py"],
    install_requires=[
        "openai",
        "keyring",
        "argparse",
    ],
    description="A binary to generate commit messages or commits using generative models."
    long_description=long_description,
    long_description_content_type="text/markdown",
)
