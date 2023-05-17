from setuptools import setup, find_packages

setup(
    name='autocommit',  # This is the name of your PyPI-package.
    version='0.1',  # Update the version number for new releases
    packages=find_packages(),  # This will include all sub-packages
    scripts=['autocommit.py'],  # The name of your script
    install_requires=[  # Add any other dependencies your script needs
        'openai',
        'keyring',
        'argparse',
        'subprocess',  # This is part of the standard library, so you don't need to include it
    ],
)
