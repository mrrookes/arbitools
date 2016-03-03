#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(name="arbitools",
      version="0.95",
      description="Chess Arbiter Tools",
      license="GPL",
      author="David Gonzalez Gandara",
      author_email="mrrookes@member.fsf.org",
      url="http://www.ourenxadrez.org/arbitools.htm",
      packages=['arbitools', 'tests'],
      package_data={'arbitools':['data/*']},
      install_requires={'xlwt', 'xlrd', 'lxml', 'Click'},
      #entry_points='''
      #    [console_scripts]
      #    arbitools_run=arbitools-run:arbitoolsrun
      #''',
      scripts=['arbitools-run.py', 'arbitools-standings.py', 'arbitools-update.py', 'arbitools-gui.py', 'arbitools-purge.py', 'arbitools-add.py']
)
