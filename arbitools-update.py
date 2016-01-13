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
        
        listfile=''
        elolist=''
        method=''
        listdata=''
        inputfile=''
        
        try:
                opts, args = getopt.getopt(argv,"hvl:m:i:",["version","list=", "method=", "ifile="])
        except getopt.GetoptError:
                print('arbitools-update.py -l <list> -m <method> -i <inputfile>')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('usage: arbitools-update.py -l <list: fide, feda or fidefeda> -m <search method> -i <infile>')
                        sys.exit()

                elif opt in ("-l", "--list"):
                        elolist = arg
                        if elolist == '':
                                print("You have to select an elo list with option -l. You can choose fide, feda or fidefeda.")
                                sys.exit()

                        if elolist == 'feda':
                                if xlrd_present==True:
                                        listfile = "elo_feda.xls"
                                else:
                                        print("To search feda list you need to install xlrd module.")
                                        sys.exit()
                        if elolist == 'fidefeda':
                        
                                listfile = "FIDE-FEDA Vega.csv"
                        if elolist == 'fide':
                                if lxml_present==True:
                                        listfile = "players_list_xml.xml"
                                else:
                                        print("To search fide list you have to install lxml module.")
                                        sys.exit()


                elif opt in ("-m", "--method"):
                        method = arg
                        if method == 'name':
                                print("Searching players by name...")
                        elif method == 'idfide':
                                print("Searching players by ID FIDE...")
                        elif method == 'idfeda':
                                print("Searching players by ID FEDA...")
                        else:
                                print("I don't know this search method. Try name of idfide.")
                                sys.exit()
                elif opt in ("-i", "--ifile"):
                        inputfile = arg
                
                elif opt in ("-v", "--version"):
                        print('GNU Chess Arbiter')
                        print('Copyright 2015 David González Gándara')
                        print('License GPLv.3+ <http://www.gnu.org/licenses/gpl.htm>')
                        print('This is free software, you are free to change and distribute it.')
                        print('There is no WARRANTY, to the extent permitted by law.')
                        sys.exit()
                
        


        tournament = arbitools.Tournament()
        
        if listfile:
                print(listfile)
                listdata = tournament.get_list_data_from_file(elolist, listfile, method)
        else:
                print("No list specified")
        #print(listdata)
        tournament.get_tournament_data_from_file(inputfile)
        if inputfile.endswith('.fegaxa'):
                tournament.update_players_data_from_list_fegaxa(listdata)
        else:
                tournament.update_players_data_from_list(listdata, method, 1,1,1,1,1)
        tournament.output_to_file(inputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
