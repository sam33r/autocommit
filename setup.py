from setuptools import setup, find_packages

# Read in the README for the long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ai-commit-gen",
    version="0.6",
    packages=find_packages(),
    scripts=["ai_commit_gen.py"],
    install_requires=[
        "litellm",
        "keyring",
    ],
    description="A binary to generate commit messages using generative models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "ai-commit-gen=ai_commit_gen:main",
        ],
    },
)
