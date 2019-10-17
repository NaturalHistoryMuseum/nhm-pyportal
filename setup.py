# !/usr/bin/env python
# encoding: utf-8

import os

from setuptools import find_packages, setup

NAME = 'pyportal'
DESCRIPTION = ''
URL = 'https://github.com/NaturalHistoryMuseum/pyportal'
EMAIL = 'data@nhm.ac.uk'
AUTHOR = 'Natural History Museum'
VERSION = '0.1'

REQUIRED = ['requests']

readme = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')
try:
    with open(readme, 'r', encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
except TypeError:
    with open(readme, 'r') as f:
        LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    package_data={},
    include_package_data=True,
    entry_points='''
        [console_scripts]
        pyportal=pyportal.cli:cli
    ''',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
        ]
    )
