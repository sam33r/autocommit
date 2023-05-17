from setuptools import setup, find_packages

# Read in the README for the long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ai-commit-gen",
    version="0.3",
    packages=find_packages(),
    scripts=["ai-commit.py"],
    install_requires=[
        "openai",
        "keyring",
        "argparse",
    ],
    description="A binary to generate commit messages or commits using generative models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "ai-commit-gen=ai-commit:main",  # This allows the user to run 'autocommit' from the command line to execute your script
        ],
    },
)
