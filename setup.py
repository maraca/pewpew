#!/usr/bin/python2.6
"""Setup file for AWS deploy script."""
__author__ = 'contact@martincozzi.com'

from setuptools import setup

setup(
    name='aws_deploy',
    version='0.1',
    description='Deploy to a bunch of AWS instances.',
    package_dir={'': 'src'},
    install_requires=[
        'boto',
        'GitPython',
        'python-gflags',
        ],
    entry_points={
        'console_scripts': [
            'deploy = deploy.tools:deploy',
            ],
        },
    zip_safe=False,
    )
