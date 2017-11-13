#!/usr/bin/python

import sys
from setuptools import setup

if sys.version_info < (3, 2):
    raise SystemExit("gen-hxl-dict requires at least Python 3.2")

setup(name='gen-hxl-ict',
      version='0.1',
      description='Python script to generate HTML HXL hashtag dictionary.',
      author='David Megginson',
      author_email='contact@megginson.com',
      install_requires=['libhxl'],
)

