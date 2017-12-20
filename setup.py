#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(name="arbitools",
      version="0.9.9",
      description="Chess Arbiter Tools",
      long_description="Read README.md",
      license="GPL",
      author="David Gonzalez Gandara",
      author_email="mrrookes@member.fsf.org",
      url="https://github.com/mrrookes/arbitools/archive/v0.9.9.tar.gz",
      packages=['arbitools', 'tests'],
      package_data={'arbitools':['data/*']},
      install_requires=['xlwt', 'xlrd', 'lxml', 'Click'],
      #entry_points='''
      #    [console_scripts]
      #    arbitools_run=arbitools-run:arbitoolsrun
      #''',
      scripts=['arbitools-run.py', 'arbitools-standings.py', 'arbitools-update.py', 'arbitools-gui.py', 'arbitools-purge.py', 'arbitools-add.py']
)
