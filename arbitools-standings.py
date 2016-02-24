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


from arbitools import arbitools
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
                opts, args = getopt.getopt(argv,"hvi:",["version", "ifile="])
        except getopt.GetoptError:
                print('arbitools-standings.py -i <inputfile>')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('usage: arbitools-standings.py -i <inputfile>')
                        sys.exit()
                elif opt in ("-i", "--ifile"):
                        inputfile = os.path.join(os.getcwd(), arg) #TESTING - seems to work
                 
                elif opt in ("-v", "--version"):
                        print('GNU Chess Arbiter Tools')
                        print('Copyright 2015 David González Gándara')
                        print('License GPLv.3+ <http://www.gnu.org/licenses/gpl.htm>')
                        print('This is free software, you are free to change and distribute it.')
                        print('There is no WARRANTY, to the extent permitted by law.')
                        sys.exit()
                
        


        tournament = arbitools.Tournament()
        
        
        #print(listdata)
        methods_list = ()
        methods_temp = []
        sort_by = ()
        sort_by_temp = []
        tournament.get_tournament_data_from_file(inputfile)
        configfilename = os.path.join(os.path.expanduser("~"), ".arbitools") #TODO set default options in case there is not configfile
        with open(configfilename) as configfile:
                lines = configfile.readlines()
                for line in lines:
                        linesplit = line.split(":")
                        if linesplit[0] == "Methods":
                                methods = linesplit[1].split(",")
                                for method in methods:
                                        methods_temp.append({'method': method.strip()})
                        elif linesplit[0] == "Sort":
                                sorts = linesplit[1].split(",")
                                for sort in sorts:
                                        sort_by_temp.append({'method': sort.strip()})
        methods_list=tuple(methods_temp)
        sort_by=tuple(sort_by_temp)
       
        
        if inputfile.endswith('.veg') or inputfile.endswith('.txt') or inputfile.endswith('.trfx') or inputfile.endswith('.TXT'):
                
                try:
                        tournament.standings_to_file(inputfile)
                except:
                        print("An error ocurred while writing standings to file")
                        pass
                
                try:
                        tournament.export_to_fide(inputfile)
                except:
                        print("An error ocurred while writing the trf file")
                        pass
                
                try:
                        listfile = ''
                        elolist = ''
                        if os.path.isfile(os.path.join(os.path.expanduser("~"), "custom_elo.csv")):
                                print("Writing FEDA report from custom_elo.csv")
                                listfile = os.path.join(os.path.expanduser("~"), "custom_elo.csv")
                                elolist = "custom"
                        elif os.path.isfile(os.path.join(os.path.expanduser("~"), "elo_feda.xls")):
                                print("Writing FEDA report from elo_feda.xls")
                                listfile = os.path.join(os.path.expanduser("~"), "elo_feda.xls")
                                elolist = "feda"
                        else:
                                print("I cannot write FEDA Rating Admin. No elo information. Copy in your personal folder elo_feda.xls or create custom_elo.csv")
                        if listfile != '':
                                listdata = tournament.get_list_data_from_file(elolist, listfile)
                                tournament.update_players_data_from_list(listdata, 1, 1, 1, 1, 1)
                                tournament.export_to_feda(inputfile)
                except:
                        print("An error ocurred while writing FEDA rating file")
                        pass

                try:
                        tournament.write_it3_report(inputfile)
                except:
                        print("An error ocurred while writing IT3 report")
        try:
            if methods_list:
                tournament.applyARPO(inputfile, methods_list, sort_by)
                
            else:
                tournament.applyARPO(inputfile, ({'method':'Name'}, {'method':'Points'}, {'method':'ARPO'}), ({'method':'Points'}, {'method': 'ARPO'}))
        except Exception:
                print("I cannot calculate ARPO for this file")
                pass
if __name__ == "__main__":
   main(sys.argv[1:])
