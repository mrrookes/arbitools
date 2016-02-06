#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

#Copyright 2015 David González Gándara
#This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import arbitools
import os
import sys, getopt
import csv
import unicodedata
try:
	from lxml import etree
	lxml_present=True
except:
	lxml_present=False
try:
	import xlrd
	xlrd_present=True
except ImportError:
	xlrd_present=False

def main(argv):

        inputfile=''
        addfile=''
        
        try:
                opts, args = getopt.getopt(argv,"hvi:a:",["version", "ifile=", "addfile="])
        except getopt.GetoptError:
                print('arbitools-add.py -i <infile> -a <addfile>')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('usage: arbitools-add.py -i <inputfile> -a <addfile>')
                        sys.exit()

                elif opt in ("-i", "--ifile"):
                        inputfile = arg
                elif opt in ("-a", "--addfile"):
                        addfile = arg
                
                elif opt in ("-v", "--version"):
                        print('GNU Chess Arbiter Tools')
                        print('Copyright 2015 David González Gándara')
                        print('License GPLv.3+ <http://www.gnu.org/licenses/gpl.htm>')
                        print('This is free software, you are free to change and distribute it.')
                        print('There is no WARRANTY, to the extent permitted by law.')
                        sys.exit()
                
        


        tournament = arbitools.Tournament()
        
        tournament.get_tournament_data_from_file(inputfile)
        tournament.add_players_data_from_file(addfile)
        tournament.output_to_file(inputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
