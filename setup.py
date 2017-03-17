#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

data = ["data/*"]

setup(
    name='grive-indicator',
    version='1.0',
    url='https://github.com/LyzardKing/grive-indicator',
    author='Galileo Sartor',
    author_email='galileo.sartor@gmail.com',
    packages=find_packages(exclude=["tests*"]),
    package_data={'grive_indicator': data},
    data_files=[('/usr/share/applications', ['grive-indicator.desktop']),
                ('/usr/share/pixmaps/', ['web-google-drive.svg'])],
    entry_points={
        'console_scripts': [
            'grive-indicator = grive_indicator:main',
        ]
    }
)
