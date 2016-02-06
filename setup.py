#!/usr/bin/env python

from distutils.core import setup

setup(name="arbitools",
      version="0.9",
      description="Chess Arbiter Tools",
      license="GPL",
      author="David Gonzalez Gandara",
      author_email="mrrookes@member.fsf.org",
      url="http://www.ourenxadrez.org/arbitools.htm",
      packages=['arbitools', 'tests'],
      package_data={'arbitools':['data/*']},
      scripts=['arbitools-standings.py', 'arbitools-update.py', 'arbitools-gui.py', 'arbitools-purge.py', 'arbitools-add.py']
)
