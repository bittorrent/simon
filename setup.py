#!/usr/bin/env python

import os

from setuptools import setup, find_packages


def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read()

setup(
    name='simon',
    version='0.0',
    description='Judge your code',
    url='https://github.com/bittorrent/simon',
    long_description=read_file('README.md'),
    author='BitTorrent Inc.',
    author_email='live-eng@bittorrent.com',
    package_data={'': ['data/bin/*']},
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'simon=simon.__main__:main'
        ]
    },
    install_requires=[
        'appdirs',
        'pyyaml',
        'jinja2',
    ]
)
