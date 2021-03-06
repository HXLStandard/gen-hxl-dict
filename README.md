# Python script to generate HTML HXL hashtag dictionary

The [Humanitarian Exchange Language](http://hxlstandard.org) (HXL)
uses hashtags to add information to spreadsheets, API output, and
similar data using hashtags and attributes. The core schema defining
the hashtags and attributes is located at

https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit?usp=sharing

The normative output from this script is at

http://hxlstandard.org/standard/dictionary/

This script reads the core schema and uses it to generate
human-readable HTML markup for the [HXL Hashtag
Dictionary](http://hxlstandard.org/standard/dictionary/), which is
part of the HXL standard. This script is in use beginning with HXL
version 1.1.

Requires Python 3.

## Installation

It's strongly recommended to run this script inside a Python virtual
environment. To set up a Python 3 custom environment in most Linux
distros, try

  mkvirtualenv -p /usr/bin/python3 hxl-dict # or whatever you want to call it

To load dependencies before running, try

  workon hxl-dict # or whatever you called your Python virtual environment
  python setup.py develop

## Usage

  python gen-hxl-dict.py > docs/hxl-hashtags-and-attributes.html


Last updated 2017-11-27
