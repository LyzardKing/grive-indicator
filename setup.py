#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup, find_packages

data = ["data/*"]

icons = []
for dirpath, dirnames, filenames in os.walk("icons/"):
    relpath = dirpath[len("icons/"):]
    if relpath and filenames:
        icons.append((sys.prefix + "/share/icons/hicolor/" + relpath, [os.path.join(dirpath, x) for x in filenames]))

setup(
    name='grive-indicator',
    version='19.06',
    url='https://github.com/LyzardKing/grive-indicator',
    maintainer='Galileo Sartor',
    maintainer_email='galileo.sartor@gmail.com',
    description='Linux Gtk indicator to sync Google Drive via Grive',
    packages=find_packages(exclude=["tests*"]),
    package_data={'grive_indicator': data},
    data_files=[
        ('lib/python3/dist-packages/grive_indicator', ['grive_indicator/version']),
        (sys.prefix + '/share/applications', ['grive_indicator/data/grive-indicator.desktop'])] +
         + icons,
    entry_points={
        'console_scripts': [
            'grive-indicator = grive_indicator:main',
        ]
    }
)
