##---------------------arbitools-------------------------
#Collection of python functions for typical tasks of Chess Arbiters.
#The class Tournament offers useful properties and methods for Chess
#Tournament Management


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

import os
import pkg_resources
import sys
import csv
import unicodedata
import time
from collections import namedtuple
from operator import itemgetter
from itertools import dropwhile, compress
import arbitools.PyRP
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
try:
        import xlwt
        xlwt_present=True
except ImportError:
        xlwt_present=False
class Tournament:

        def __init__(self):
                        
                self.info={'TOURNAMENT_NAME':' ', 'CITY':' ', 'FED':' ', 'BEGIN_DATE':' ', 'END_DATE':' ', 'ARBITER':' ', 'DEPUTY':' ', 'TIEBREAKS':' ', 'NUMBER_OF_ROUNDS':' ', 'CURRENT_ROUND':' ', 'NUMBER_OF_PLAYERS':' ', 'NUMBER_OF_RATED_PLAYERS':' ', 'NUMBER_OF_TEAMS':' ', 'TYPE_OF_TOURNAMENT':' ', 'ALLOTED_TIME':' ', 'DATES': ' '}
                self.standings=[]
                self.dates=[]
                self.teamnames = []
                self.teamsmembers = []
                self.purged = False

                self.players_data = []
                self.crosstable = []
                self.players_to_purge = []
                self.indexes_to_purge = []

                self.typeoffile = ''  
                
                #The following variables store information of .veg files.
                self.header=''
                self.vegaheader=[]
                self.playerscolor=[]
                self.playersopponent=[]
                self.playersfloater=[]
                self.roundresults=[]
                self.codepairing=[]


                self.headeroutputvega='' #This variable communicates the function that reads the file and the one that writes it. I have to make it cleaner by building the header again from the tournament data in the write function.
                self.restofvega=[]
                self.restofvegaoutput=[]
                
        ##########################################################################
        #Output players_data, tournament info or both to a file (.veg, .csv, .txt)
        ##########################################################################      
        def output_to_file(self, inputfile):
                outputfile = ''
                if self.players_data == '':
                        print("I don't have anything to write in the file")
                        sys.exit()
                inputfilesplit = inputfile.split('.')#Separate file name and extension.
                outputfiletxt=inputfilesplit[0]+'_updated'+'.txt' #The name for the .txt file. #WARNING-paths can contain "."
                if inputfile.endswith('.csv') or inputfile.endswith('.xls'):
                        outputfile=inputfilesplit[0]+'_updated'+'.csv'#Get the name for the updated file.
                elif inputfile.endswith('.veg'):
                        outputfile=inputfilesplit[0]+'_updated'+'.veg'
                elif inputfile.endswith('.txt'):
                        self.export_to_fide(inputfile)
                elif inputfile.endswith('.TXT'):
                        self.export_to_fide(inputfile)
                elif inputfile.endswith('.trf'):
                        self.export_to_fide(inputfile)
                elif inputfile.endswith('.fegaxa'):
                        self.export_to_fegaxa(inputfile)
                else:
                        print("I don't have a filter for this file format.")
                if inputfile.endswith('.csv') or inputfile.endswith('.veg') or inputfile.endswith('xls'):
                        with open(outputfile, 'w') as csvoutputfile:
                                writer = csv.DictWriter(csvoutputfile, fieldnames=self.header, delimiter=';')
                                if inputfile.endswith('.csv') or inputfile.endswith('.xls'):
                                        writer.writeheader()
#This code is for .veg and .csv only. I have to write the code for .txt
                                try:
                                        if inputfile.endswith('.veg'):
                                                csvoutputfile.writelines(self.vegaheader)
                                                csvoutputfile.writelines(self.headeroutputvega)
                                        players_data_veg = self.players_data
                                        for player in players_data_veg:
                                                if "POINTS" in player:
                                                        del player['POINTS']
                                                if "RANK" in player:
                                                        del player['RANK']
                                        writer.writerows(players_data_veg)
                                        if inputfile.endswith('.veg'):
                                                csvoutputfile.writelines(self.restofvega)
                                        print('File '+outputfile+' created.')

                                except csv.Error as e:
                                        sys.exit('file %s, line %d: %s' % (inputfile, DictWriter.line_num, e))
                        if inputfile.endswith('.veg'):
                                new_name=inputfilesplit[0]+'_old'+'.veg'
                                print('Renaming '+inputfile+'. Now the name is: '+new_name)
                                os.rename(inputfile, new_name)
                                os.rename(outputfile, inputfile)
                return

        #######################################################################################
        #Export to Fegaxa database format
        #######################################################################################
        def export_to_fegaxa(self, inputfile):
                inputfilesplit = inputfile.split('.')
                outputfilepath = os.path.join(os.getcwd(),inputfilesplit[0])
                outputfile = outputfilepath+'_updated'+'.fegaxa' #TESTING


                print_to_xls = False #dictionaries are not sorted, so writing to xls is difficult
                if print_to_xls == True and xlwt_present == True:
                        workbook = xlwt.Workbook()
                        
                        sheet = workbook.add_sheet("Jugadores")
                        for col_index, cell_value in enumerate(self.header):
                                sheet.write(0, col_index, cell_value)
                        columns = list(self.players_data[0].keys())
                        for i, row in enumerate(self.players_data):
                                for j, col in enumerate(columns):
                                        adjust = i+1
                                        sheet.write(adjust, j, row[col])
                                        #print(row)
                        workbook.save("prueba_outputfile.xls")
                        print('File '+' xls'+' created.')
                else:
                        print("I could not write in .xls format, you will have to transform it manually") 
                        with open(outputfile, 'w') as csvoutputfile:
                                writer = csv.DictWriter(csvoutputfile, fieldnames=self.header, delimiter=';')
                                writer.writeheader()
                                try:
                                        writer.writerows(self.players_data)
                                        print('File '+outputfile+' created.')
                                except csv.Error as e:
                                        sys.exit('file %s, line %d: %s' % (inputfile, DictWriter.line_num, e))
                return
        #####################################################################################################
        #Export to FEDA Admin format
        ####################################################################################################
        def export_to_feda(self, inputfile):
                #if inputfile.startswith('FIDE'):
                #        inputfile = inputfile[5:]
                inputfilesplit = inputfile.split('.') #WARNING there may be more "."
                outputfiletxt = inputfilesplit[0]+"_RatingAdmin.txt"#IMPROVE THE NAME OF THE FILE. SPLIT THE PATH AND ADD THE PREFIX
                with open(outputfiletxt, 'w') as txtoutputfile:
                        txtoutputfile.write('localid;initial_ranking;Name;Sex;country;birthdate;W;N;Rc\n')
                        for i, j in enumerate(self.players_data):
                               idnat = j['IDNAT'] # need to get idnat from list file
                               ranking = str(i+1) # in order to have "normal" numbers
                               name = j['NAME']
                               if j['G'] == 'f':
                                       sex = 'Ff'
                               else:
                                       sex = "M "
                               country = j['COUNTRY']
                               birthday = j['BIRTHDAY']
                               points = 0.0
                               numberofratedopponents = 0
                               elosum = 0
                               rc = "   0" #need to get average rating of opponents
                               #print(j['NAME'])
                               #print(self.playersopponent[i])
                               opponentssplit = self.playersopponent[i].split(' ') #opponents are stored in a string
                               resultssplit = self.roundresults[i].split(' ')
                               for number, opponent in enumerate(opponentssplit):
                                       #print(opponent)#testing
                                       index = int(opponent)-1
                                       if len(self.players_data[index]['ELONAT']) > 1 and opponent != "0000" and opponent != ' ':
                                               
                                               #print(j['NAME']+j['ELONAT']) #testing
                                               #lets apply the 400 elo point difference rule.
                                               if j['ELONAT'] == ' ' or j['ELONAT'] == '':
                                                   j['ELONAT'] = 0

                                               elodif = int(j['ELONAT']) - int(self.players_data[index]['ELONAT'])
                                               #print(elodif) #testing
                                               if abs(elodif) >= 400:
                                                   #difference = abs(elodif) - 400
                                                   #print(difference) # testing
                                                   if int(self.players_data[index]['ELONAT']) > int(j['ELONAT']) and int(j['ELONAT']) > 0:
                                                       eloadjust = int(j['ELONAT']) + 400
                                                   elif int(self.players_data[index]['ELONAT']) < int(j['ELONAT']) and int(j['ELONAT']) >0:
                                                       eloadjust = int(j['ELONAT']) - 400
                                                   elif int(j['ELONAT']) == 0:
                                                       eloadjust = int(self.players_data[index]['ELONAT'])                                                         
                                                       
                                               else:
                                                   eloadjust = int(self.players_data[index]['ELONAT'])
                                               #print(eloadjust) #testing
                                               elosum += eloadjust
                                               numberofratedopponents += 1
                                               #print( self.roundresults[number])#testing
                                               if resultssplit[number] == '1' or resultssplit[number] == '+':
                                                       points += 1
                                               elif resultssplit[number] == '=':
                                                       points += 0.5
                               if numberofratedopponents > 0:
                                       rc = round(elosum/numberofratedopponents)
                               if len(idnat) < 10:
                                       extra = 10-len(idnat)
                                       idnat = idnat+" "*extra
                               txtoutputfile.write(idnat+';')
                               if len(ranking) < 4:
                                       extra = 4-len(ranking)
                                       ranking = " "*extra+ranking
                               txtoutputfile.write(ranking+';')
                               if len(name) < 34:
                                       extra = 34-len(name)
                                       name = name+" "*extra
                               txtoutputfile.write(name+";")
                               txtoutputfile.write(sex+";")
                               txtoutputfile.write(country+";")
                               if len(birthday) == 4: #this means the date is just the year
                                       birthday = birthday[2:]+"-"+"00"+"-"+"00"
                               elif len(birthday) == 10: #in case the date has day and month
                                       if "-" in birthday:
                                               birthdaysplit = birthday.split("-")
                                               for part in birthdaysplit:
                                                       if len(part) == 4: #locate the year
                                                               birthday = part[2:]+"-"+"00"+"-"+"00"
                                       elif "." in birthday:
                                               birthdaysplit = birthday.split(".")
                                               for part in birthdaysplit:
                                                       if len(part) == 4:
                                                               birthday = part[2:]+"-"+"00"+"-"+"00"
                                       elif "/" in birthday:
                                               birthdaysplit = birthday.split("/")
                                               for part in birthdaysplit:
                                                       if len(part) == 4:
                                                               birthday = part[2:]+"-"+"00"+"-"+"00"
                               txtoutputfile.write(birthday+";")
                               if len(str(points)) < 4:
                                       extra = 4-len(str(points))
                                       points = " "*extra+str(points)
                               txtoutputfile.write(str(points)+";")
                               if len(str(numberofratedopponents)) == 1:
                                       numberofratedopponents = " "+str(numberofratedopponents)
                               txtoutputfile.write(str(numberofratedopponents)+";")#Number of rated games here
                               txtoutputfile.write(str(int(rc)))
                               txtoutputfile.write("\n")
        #########################################################################################
        #Export to FIDE trf file format (Krause)
        #########################################################################################
        def export_to_fide(self, inputfile):
                inputfilesplit = inputfile.split('.')
                outputfiletxt=inputfilesplit[0]+'_export'+'.txt' #The name for the .txt file.
                with open(outputfiletxt, 'w') as txtoutputfile:
                        txtoutputfile.write("012 "+self.info['TOURNAMENT_NAME'])
                        txtoutputfile.write("022 "+self.info['CITY'])
                        txtoutputfile.write("032 "+self.info['FED'])
                        txtoutputfile.write("042 "+self.info['BEGIN_DATE'])
                        txtoutputfile.write("052 "+self.info['END_DATE'])
                        txtoutputfile.write("062 "+self.info['NUMBER_OF_PLAYERS'])
                        txtoutputfile.write("072 "+self.info['NUMBER_OF_RATED_PLAYERS'])#Number of rated players.
                        if self.info['NUMBER_OF_RATED_PLAYERS'] == ' ':
                                txtoutputfile.write("\n")#Write a return carrier in case the variable is empty.
                        txtoutputfile.write("082 "+self.info['NUMBER_OF_TEAMS'])#Number of teams.
                        if self.info['NUMBER_OF_TEAMS'] == ' ':
                                txtoutputfile.write("\n")#Write a return carrier in case the variable is empty.
                        txtoutputfile.write("092 "+self.info['TYPE_OF_TOURNAMENT'])#Type of tournament.
                        if self.info['TYPE_OF_TOURNAMENT'] == ' ':
                                txtoutputfile.write("\n")#Write a return carrier in case the variable is empty.
                        txtoutputfile.write("102 "+self.info['ARBITER'])
                        if self.info['ARBITER'] == ' ':
                                txtoutputfile.write("\n")#Write a return carrier in case the variable is empty.
                        txtoutputfile.write("112 "+self.info['DEPUTY'])
                        if self.info['DEPUTY'] == ' ':
                                txtoutputfile.write("\n")#Write a return carrier in case the variable is empty.
                        txtoutputfile.write("122 "+self.info['ALLOTED_TIME'])
                        if self.info['ALLOTED_TIME'] == ' ':
                                txtoutputfile.write("\n")#Write a return carrier in case the variable is empty.
                        dates = "132"+" "*87#We need spaces until position 92. Maybe there is a better way of doing this...
                        dates = dates+self.info['DATES']
                        txtoutputfile.write(dates)
                        #if self.info['DATES'] == ' ':
                        txtoutputfile.write("\n")
                        count = 1
                        countplayer = 1
                        for player in self.players_data:
                                
                                countstr = ''
                                titlestr=''
                                namestr=''
                                elostr=''
                                idfidestr = ''
                                birthdaystr = ''
                                pointsstr = ''
                                rankstr = ''
                                roundsstr = ''
                                if len(str(count)) < 4:
                                        extra = 4-len(str(count))
                                        countstr = " "*extra+str(countplayer)
                                if len(player['TITLE']) == 2:
                                        titlestr = " "+player['TITLE']
                                elif player['TITLE'] == '':
                                        titlestr = "   "
                                else:
                                        titlestr = player['TITLE']
                                if len(player['NAME']) < 33:
                                        extra = 33-len(player['NAME'])
                                        namestr = player['NAME']+" "*extra
                                elif len(player['NAME']) >= 33:
                                        namestr = player['NAME'][:33]
                                if len(player['ELOFIDE']) < 4:
                                        extra = 4-len(player['ELOFIDE'])
                                        elostr = " "*extra+player['ELOFIDE']
                                else:
                                        elostr = player['ELOFIDE']
                                if len(player['IDFIDE']) < 11:
                                        extra = 11-len(player['IDFIDE'])
                                        idfidestr = " "*extra+player['IDFIDE']
                                else:
                                        idfidestr = player['IDFIDE']
                                if len(player['BIRTHDAY']) < 10:
                                        extra = 10-len(player['BIRTHDAY'])
                                        birthdaystr = player['BIRTHDAY']+" "*extra
                                else:
                                        birthdaystr = player['BIRTHDAY']
                                
                                if len(player['POINTS']) < 4:
                                        extra = 4-len(player['POINTS'])
                                        pointsstr = " "*extra+player['POINTS']
                                else:
                                        pointsstr = player['POINTS']
                                if len(player['RANK']) < 4:
                                        extra = 4-len(player['RANK'])
                                        rankstr = " "*extra+player['RANK']
                                else:
                                        rankstr = player['RANK']
                                #print(self.playersopponent[count-1])#testing
                                playersopponentsplit = self.playersopponent[count-1].split(' ')
                                playerscolorsplit = self.playerscolor[count-1].split(' ')
                                roundresultssplit = self.roundresults[count-1].split(' ')
                                offset = 0
                                opponent = ''
                                color = ''
                                result = ''
                                for i in range(len(playersopponentsplit)):
                                        if len(playersopponentsplit[i]) < 4: #fill with extra spaces to fill the space
                                                extra = 4-len(playersopponentsplit[i])
                                                opponent = " "*extra+playersopponentsplit[i]
                                        else:
                                                opponent = playersopponentsplit[i]
                                        color = playerscolorsplit[i]
                                        result = roundresultssplit[i]
                                        roundsstr = roundsstr+"  "+opponent+" "+color+" "+result
                                        offset += 10
                                playerdata = "001 "+countstr+" "+player['G']+titlestr+" "+namestr+" "+elostr+" "+player['COUNTRY']+" "+idfidestr+" "+birthdaystr+" "+pointsstr+" "+rankstr+roundsstr
                                txtoutputfile.write(playerdata+"\n")
                                count += 1
                                countplayer += 1

                                #purging a file makes it not work in FIDE
                                #if self.purged == True and count in self.indexes_to_purge: #if the player was purged, skip one
                                #        countplayer += 1
                                #        continue
                        if len(self.teamnames)>0:
                                for i in range(len(self.teamnames)):
                                        teamdata = "013 "+self.teamnames[i]
                                        for member in self.teamsmembers[i]: #fill with extra spaces to fill the space
                                                if len(member)<4:
                                                        extra = 4-len(member)
                                                        member=" "*extra+member
                                                teamdata = teamdata+" "+member
                                        txtoutputfile.write(teamdata+"\n")
                                        #print(self.teamnames[i])
                                        #print(self.teamsmembers[i])
                                        
                #print(self.indexes_to_purge)
                return
        ######################################################################################################
        # write IT3 report
        ######################################################################################################
        def write_it3_report(self, inputfile):
                tex_template = []
                if inputfile.startswith('FIDE'):
                        inputfile = inputfile[5:]
                inputfilesplit = inputfile.split('.')
                outputfile = inputfile+"_IT3"+".tex" #TESTING
                with open(pkg_resources.resource_filename(__name__, "data/it3.tex")) as it3texfile: #TESTING - SLASHES ARE A PROBLEM FOR CROSSPLATFORM... FIX THIS
                        tex_template = it3texfile.read()
                #Now, lets insert the data of the tournament in the tex template
                
                #name of the tournament
                position = tex_template.find("NAME OF THE TOURNAMENT")
                positionend = position+22 #length of the text to replace
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+self.info['TOURNAMENT_NAME'].rstrip()+tex_template[positionend:] 
                
                #starting date
                position = tex_template.find("STARTDATE")
                positionend = position+9
                
                tex_template = tex_template[:position]+self.info['BEGIN_DATE'].rstrip()+tex_template[positionend:]
                
                #ending date
                position = tex_template.find("ENDDATE")
                positionend = position+7 
                tex_template = tex_template[:position]+self.info['END_DATE'].rstrip()+tex_template[positionend:]

                
                #masters
                gm = 0
                gmsfromhost = 0
                gmsfeds = []
                im = 0
                imsfeds = []
                imsfromhost = 0
                fm = 0
                fmsfeds = []
                fmsfromhost = 0
                wgm = 0
                wgmsfeds = []
                wgmsfromhost = 0
                wim = 0
                wimsfeds = []
                wimsfromhost = 0
                wfm = 0
                wfmsfeds = []
                wfmsfromhost = 0
                hostfed = "ESP" #Change this for other countries
                ratedfeds = []
                unratedfeds = []
                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
                numratedplayers = int(self.info['NUMBER_OF_RATED_PLAYERS'])
                numratedfeds = 0
                numunratedfeds = 0
                unratedfeds = []
                ratedplayersfromhost = 0
                ratedplayersfromother = 0
                unratedplayersfromhost = 0
                unratedplayersfromother = 0
                for player in self.players_data:
                        if player['TITLE'] == 'GM':
                                gm += 1
                        elif player['TITLE'] == 'IM':
                                im += 1
                        elif player['TITLE'] == 'FM':
                                fm += 1
                        elif player['TITLE'] == 'WGM':
                                wgm += 1
                        elif player['TITLE'] == 'WIM':
                                wim += 1
                        elif player['TITLE'] == 'WFM':
                                wfm += 1
                        # count federations of players
                        if player['COUNTRY'] not in ratedfeds and len(player['ELOFIDE']) > 3:
                                ratedfeds.append(player['COUNTRY'])
                                numratedfeds += 1
                        if player['COUNTRY'] not in gmsfeds and player['TITLE'] =="GM":
                                gmsfeds.append(player['COUNTRY'])
                        if player['COUNTRY'] not in imsfeds and player['TITLE'] =="IM":
                                imsfeds.append(player['COUNTRY'])
                        if player['COUNTRY'] not in fmsfeds and player['TITLE'] =="FM":
                                fmsfeds.append(player['COUNTRY'])
                        if player['COUNTRY'] not in wgmsfeds and player['TITLE'] =="WGM":
                                wgmsfeds.append(player['COUNTRY'])
                        if player['COUNTRY'] not in wimsfeds and player['TITLE'] =="WIM":
                                wimsfeds.append(player['COUNTRY'])
                        if player['COUNTRY'] not in wfmsfeds and player['TITLE'] =="WFM":
                                wfmsfeds.append(player['COUNTRY'])
                                
                        if player['COUNTRY'] not in unratedfeds and len(player['ELOFIDE']) < 3:
                                unratedfeds.append(player['COUNTRY'])
                                numunratedfeds += 1
                        

                        if player['COUNTRY'] == "ESP" and len(player['ELOFIDE']) > 3:
                                ratedplayersfromhost += 1
                        elif player['COUNTRY'] =="ESP" and len(player['ELOFIDE']) < 3:
                                unratedplayersfromhost += 1
                        #masters
                        if player['COUNTRY'] =="ESP" and player['TITLE'] == "GM":
                                gmsfromhost += 1
                        elif player['COUNTRY'] =="ESP" and player['TITLE'] == "IM":
                                imsfromhost += 1
                        elif player['COUNTRY'] =="ESP" and player['TITLE'] == "FM":
                                fmsfromhost += 1
                        elif player['COUNTRY'] =="ESP" and player['TITLE'] == "WGM":
                                wgmsfromhost += 1
                        elif player['COUNTRY'] =="ESP" and player['TITLE'] == "WIM":
                                wimsfromhost += 1
                        elif player['COUNTRY'] =="ESP" and player['TITLE'] == "WFM":
                                wfmsfromhost += 1

                #number of rated players
                position = tex_template.find("Rated&")
                position = position+7
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+self.info['NUMBER_OF_RATED_PLAYERS'].rstrip()+tex_template[position:]
                
                increment = len(self.info['NUMBER_OF_RATED_PLAYERS'].rstrip())
                position = position+increment+22 #21 is the spaced occupied by latex codes \bfseries\normalsize plus 1 space
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(numratedfeds)+tex_template[position:]

                increment = len(str(numratedfeds).rstrip())
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(ratedplayersfromhost)+tex_template[position:]
                
                increment = len(str(ratedplayersfromhost).rstrip())
                ratedplayersfromother = numratedplayers-ratedplayersfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(ratedplayersfromother)+tex_template[position:]

                #number of unrated players
                position = tex_template.find("Unrated&")
                position = position+9
                unrated = int(self.info['NUMBER_OF_PLAYERS']) - int(self.info['NUMBER_OF_RATED_PLAYERS'])
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(unrated).rstrip()+tex_template[position:]
                
                increment = len(str(unrated).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(numunratedfeds)+tex_template[position:]

                increment = len(str(numunratedfeds).rstrip())
                position = position+increment+1+23 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(unratedplayersfromhost)+tex_template[position:]

                increment = len(str(unratedplayersfromhost).rstrip())
                unratedplayersfromother = unrated-unratedplayersfromhost
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(unratedplayersfromother)+tex_template[position:]
            
                #GMs
                position = tex_template.find("GM")
                position = position+4
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(gm).rstrip()+tex_template[position:]

                increment = len(str(gm).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(len(gmsfeds))+tex_template[position:]

                increment = len(str(len(gmsfeds)))
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(gmsfromhost)+tex_template[position:]

                increment = len(str(gmsfromhost))
                gmsfromother = gm-gmsfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(gmsfromother)+tex_template[position:]
                
                #IMs
                position = tex_template.find("IM")
                position = position+4
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(im).rstrip()+tex_template[position:]
 
                increment = len(str(im).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(len(imsfeds))+tex_template[position:]

                increment = len(str(len(imsfeds)))
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(imsfromhost)+tex_template[position:]

                increment = len(str(imsfromhost))
                imsfromother = im-imsfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(imsfromother)+tex_template[position:]

                #FMs
                position = tex_template.find("FM")
                position = position+4
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(fm).rstrip()+tex_template[position:]
                
                increment = len(str(fm).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(len(fmsfeds)).rstrip()+tex_template[position:]

                increment = len(str(len(fmsfeds)))
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(fmsfromhost).rstrip()+tex_template[position:]

                increment = len(str(fmsfromhost))
                fmsfromother = fm-fmsfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(fmsfromother)+tex_template[position:]

                #WGMs
                position = tex_template.find("WGM")
                position = position+5
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wgm).rstrip()+tex_template[position:]
                
                increment = len(str(wgm).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(len(wgmsfeds)).rstrip()+tex_template[position:]

                increment = len(str(len(wgmsfeds)))
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wgmsfromhost).rstrip()+tex_template[position:]

                increment = len(str(wgmsfromhost))
                wgmsfromother = wgm-wgmsfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wgmsfromother)+tex_template[position:]

                #WIMs
                position = tex_template.find("WIM")
                position = position+5
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wim).rstrip()+tex_template[position:]
                
                increment = len(str(wim).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(len(wimsfeds)).rstrip()+tex_template[position:]

                increment = len(str(len(wimsfeds)))
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wimsfromhost).rstrip()+tex_template[position:]

                increment = len(str(wimsfromhost))
                wimsfromother = wim-wimsfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wimsfromother)+tex_template[position:]

                #WFMs
                position = tex_template.find("WFM")
                position = position+5
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wfm).rstrip()+tex_template[position:]

                increment = len(str(wfm).rstrip())
                position = position+increment+1+21 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(len(wfmsfeds)).rstrip()+tex_template[position:]

                increment = len(str(len(wfmsfeds)))
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wfmsfromhost).rstrip()+tex_template[position:]

                increment = len(str(wfmsfromhost))
                wfmsfromother = wfm-wfmsfromhost
                position = position+increment+1+22 #21 is the spaced occupied by latex codes \bfseries\normalsize
                tex_template = tex_template[:position]+"\\bfseries\\normalsize "+str(wfmsfromother)+tex_template[position:]


                with open(outputfile, "w") as csvoutputfile:
                        print("Writing It3 report...")
                        csvoutputfile.write(tex_template)
                command = "pdflatex "+outputfile
                try:
                        os.system(command)
                except:
                        print("I could not render the pdf. Is it pdflatex installed in the system?")
                        pass


        ######################################################################################################
        #print standings to file
        ######################################################################################################
        def standings_to_file(self, inputfile):
                inputfilestrip = inputfile.split('.')
                outputfilepath = os.path.join(os.getcwd(),inputfilestrip[0])
                outputfile = outputfilepath+"_standings.txt" #TESTING
                outputfileTeX = outputfilepath+"_standings.tex" #TESTING
                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
                currentround = 0
                if self.info['CURRENT_ROUND'] != '' and self.info['CURRENT_ROUND'] != ' ':
                        currentround = int(self.info['CURRENT_ROUND'])
                #tex_header = []
                #tex_middle = []
                #playerspoints = []
                if inputfile.endswith('.veg'):
                                                    
                        for i in range(0, numberofplayers):
                                #print(self.players_data[i]['POINTS'])
                                line = {'NAME':self.players_data[i]['NAME'], 'POINTS':self.players_data[i]['POINTS']}
                                #print("I'm here"+str(line))#testing
                                self.standings.append(line)
                if inputfile.endswith('.txt') or inputfile.endswith('.trfx') or inputfile.endswith('.TXT') or inputfile.endswith('.trf'):
                        for i in range(0, numberofplayers):
                                line = {'NAME':self.players_data[i]['NAME'], 'POINTS':self.players_data[i]['POINTS']}
                                #print(line)#testing
                                self.standings.append(line)
                newlist = sorted(self.standings, key=itemgetter('POINTS'), reverse=True)        
                #print("puntos: "+str(playerspoints))#testing
#Writing the text file
                with open(outputfile, 'w') as csvoutputfile:
                        print("Writing standings to .txt file...")
                        csvoutputfile.write(self.info['TOURNAMENT_NAME']+"\n")
                        csvoutputfile.write("Standings\n\n")
                        csvoutputfile.write("NAME\t\t\t\t\tPOINTS\n")
                        for i in range(0, len(newlist)):
                                tabspace = " "
                                tabspacelen = 39-len(newlist[i]['NAME'])
                                
                                for j in range(0, tabspacelen):
                                        
                                        tabspace = tabspace+" "
                                line = newlist[i]['NAME']+tabspace+str(newlist[i]['POINTS'])
                                csvoutputfile.write(line)
                                csvoutputfile.write("\n")
                                
#Writing the LaTeX file
                print("Writing standings to .tex file...")
                textemplatepath = pkg_resources.resource_filename(__name__, 'data/tex_header.txt')
                with open(textemplatepath) as texheaderfile: #TESTING
                        tex_header = texheaderfile.read()
                textemplatepath = pkg_resources.resource_filename(__name__, 'data/tex_middle.txt')
                with open(textemplatepath) as texmiddlefile:
                        tex_middle = texmiddlefile.read()
                with open(outputfileTeX, 'w') as csvoutputfile:
                        csvoutputfile.write(tex_header)
                        tournamentname = self.info['TOURNAMENT_NAME'].strip()
                        csvoutputfile.write("\n\\lhead{ \\LARGE \\bfseries "+tournamentname+"}")
                        csvoutputfile.write(tex_middle)
                        csvoutputfile.write("\n\n")
                        csvoutputfile.write("\\begin{tabbing}")
                        csvoutputfile.write("\\bfseries Name \\hspace{5cm} \\= \\bfseries Points \\\\")
                        for i in range(0, len(newlist)):
                                 line = newlist[i]['NAME']+"\\> "+str(newlist[i]['POINTS'])+"\\\\"
                                 csvoutputfile.write(line)
                                 csvoutputfile.write("\n\n")
                        csvoutputfile.write("\\end{tabbing}")
                        csvoutputfile.write("\\end{document}")
                
                
                command = "pdflatex "+outputfileTeX
                try:
                        os.system(command)
                except:
                        print("I could not render the pdf. Is it pdflatex installed in the system?")
                        pass

        ####################################################################################################
        #Apply recursive tiebreaks to standings using Julio Gonzalez and Carlos Diaz library
        ###################################################################################################
        def applyARPO(self, inputfile, methods_list, sort_by):
                lines = []#This is the list PyRP takes. We have to fill it with the players and tournament info.
                             
                for i in range(0, len(self.players_data)):
                        opponents = self.playersopponent[i].split(' ')
                        colors = self.playerscolor[i].split(' ')
                        results = self.roundresults[i].split(' ')
                        
                                                
                        line = [i+1, i+1, self.players_data[i]['TITLE'], self.players_data[i]['NAME'], self.players_data[i]['ELOFIDE'], self.players_data[i]['COUNTRY']]
                        current_round = 0
                        if self.info['CURRENT_ROUND'] != ' ' and self.info['CURRENT_ROUND'] != '':
                                current_round = int(self.info['CURRENT_ROUND'])
                        for j in range(0, current_round-1):
                                if j < len(opponents):
                                        line.append(opponents[j])
                                        line.append(colors[j])
                                        if results[j] == "+":
                                                line.append("1")#We put 1s in the +s. This is not correct, I'll change it in the future.
                                        elif results[j] == "-":
                                                line.append("0")
                                        elif results[j] == "=":
                                                line.append("x")#The symbol for draw in the TRF file is =. We replace that with x, which is what ARPO takes.
                                        else:
                                                line.append(results[j])
                                
                        line.append(self.players_data[i]['POINTS'].strip())
                        line.append("0")#I should put the real performance here. But it seems irrelevant.
                        #The following code tries to manage the players without opponents, that make ARPO crash
                        #opponentsOK = False
                        
                        #for opponent in opponents:
                        #        if opponent != '0000':
                        #                opponentsOK = True #Say OK if the player has real opponents.
                        #if opponentsOK == True:
                        #        lines.append(line)
                        #else:
                        #        alternative_line =  [i+1, i+1, self.players_data[i]['TITLE'], self.players_data[i]['NAME'], self.players_data[i]['ELOFIDE'], self.players_data[i]['COUNTRY']]
                        #        for j in range(0, int(self.info['CURRENT_ROUND'])-1):
                        #                if j < len(opponents):
                        #                        alternative_line.append(str(j))
                        #                        alternative_line.append("w")
                        #                        alternative_line.append("0")
                        #        alternative_line.append(self.players_data[i]['POINTS'].strip())
                        #        lines.append(alternative_line)
                        lines.append(line)
                #print(lines)#testing
                index_rounds = []
                roundcount = 6
                limit = current_round*3+6
                while roundcount <= current_round*3:
                        index_rounds.append(roundcount)
                        roundcount += 3
                
                
                RPtournament = PyRP.Tournament.load("testing.txt") #Load a Tournament object, from PyRP library, not arbitools
                #Now, let's fill the properties. The method load is supposed to do so, but I have to adjust the working of PyRP to arbitools.
                
                RPtournament._names = [line[3] for line in lines]
                #print(RPtournament._names)#testing
#fill the property "opponents" -- doesn't work properlyyet.
                RPtournament._opponents = [RPtournament._calculate_opponents(line, index_rounds) for line in lines]
                #print(RPtournament._opponents)#testing
                RPtournament._number_of_opponents = [len(opps) for opps in RPtournament._opponents]
                #print(RPtournament._number_of_opponents)#testing
                RPtournament._did_not_play = [name for name, opps in zip(RPtournament._names, RPtournament._number_of_opponents) if opps == 0]
                RPtournament._names = list(compress(RPtournament._names, RPtournament._number_of_opponents))
                #print(RPtournament._names)#testing
                RPtournament._elos = [RPtournament._calculate_elo(line[4], 1400) for line in compress(lines, RPtournament._number_of_opponents)]
                index_points = 3+current_round*3 #I don't really understand why 3+ and not 5+, since there are 5 fields and then the fields for the rounds.
                
                RPtournament._points = [RPtournament._calculate_points(line[index_points], draw_character="x") for line in compress(lines, RPtournament._number_of_opponents)]
                
                RPtournament._played_points = [RPtournament._calculate_played_points(line, index_rounds, "x") for line in compress(lines, RPtournament._number_of_opponents)]
                RPtournament._number_of_opponents = list(compress(RPtournament._number_of_opponents, RPtournament._number_of_opponents))
                
                RPtournament._number_of_rounds = len(index_rounds)
                #print(RPtournament._points)#testing
                #print(self.info['NUMBER_OF_PLAYERS'])#testing
                #print(self.players_data)#testing
                inputfilesplit = inputfile.split('.')
                outputfilepath = os.path.join(os.getcwd(),inputfilesplit[0])
                outputfile = outputfilepath+"_ARPO.csv" #TESTING
                RPtournament.run(methods_list = methods_list, output_file = outputfile, sort_by=sort_by)
                
                
                return

        ######################################################################################################
        #Read a elo list and get the players data for fegaxa database
        #
        #This is a special function for fegaxa database, because the header of the file is different to the
        #"normal" FEDA format
        ######################################################################################################
        def update_players_data_from_list_fegaxa(self, listfile_rows):
                                        
                becareful = []
                count = 0
                updated = 0
                nombrecompleto = []
                listfilerowsplit = []
                errors = []
                for row in self.players_data:
                        for listfilerow in listfile_rows:
                                nombrecompleto = row['Apellidos']+', '+row['Nombre']
                                #print(listfilerow['IDNAT']+'-'+row['codigoFEDA'])
                                
                                if listfilerow['IDFIDE'] != ' ' and listfilerow['IDFIDE'] != '' and listfilerow['IDFIDE'] != '0' and listfilerow['IDFIDE']==row['codigoFIDE']:
                                        #print('Updating data from: '+nombrecompleto+'...'+'idfide')
                                        if listfilerow['ELOFIDE'] != ' ':
                                                row['EloFIDE']=listfilerow['ELOFIDE']
                                        if listfilerow['NAME'] != ' ' and listfilerow['NAME'] != '':
                                                listfilerowsplit = listfilerow['NAME'].split(",")
                                                try:
                                                        row['Apellidos'] = listfilerowsplit[0].strip()
                                                        row['Nombre'] = listfilerowsplit[1].strip()
                                                except:
                                                        errors.append("Error procesing: apellidos: "+row['Apellidos']+", nombre: "+row['Nombre'])
                                                        pass
                                        if listfilerow['ELONAT'] != ' ' and listfilerow['ELONAT'] != '':
                                                row['EloFEDA']=listfilerow['ELONAT']
                                        updated += 1
                                
                                elif listfilerow['IDNAT'] != '' and listfilerow['IDNAT'] != '0' and listfilerow['IDNAT']==row['codigoFEDA']:
                                        #print('Updating data from: '+nombrecompleto+'...'+'idfeda')
                                        if listfilerow['ELONAT'] != ' ':
                                                row['EloFEDA']=listfilerow['ELONAT']
                                        updated += 1

                                elif listfilerow['NAME']==nombrecompleto and len(str(row['codigoFIDE']))<5:
                                        #print('Updating data from: '+nombrecompleto+'...'+'name')
                                        becareful.append(nombrecompleto)
                                        if listfilerow['ELOFIDE'] != ' ':
                                                row['EloFIDE']=listfilerow['ELOFIDE']
                                        if listfilerow['IDFIDE'] != ' ':
                                                row['codigoFIDE'] = listfilerow['IDFIDE']
                                        if listfilerow['ELONAT'] != ' ' and listfilerow['ELONAT'] != '':
                                                row['EloFEDA']=listfilerow['ELONAT']
                                        if listfilerow['IDNAT'] != ' ' and row['codigoFEDA'] == '':
                                                row['codigoFEDA'] = listfilerow['IDNAT']
                                        updated += 1
                        count += 1
                        print("\r"+str(count)+" players searched", end="")
                print("\r"+str(count)+" players searched")
                print(str(updated)+" players updated")
                logfilepath = os.path.join(os.getcwd(),"arbitools-report.log")
                with open(logfilepath, 'a') as logfile: #TESTING
                        logfile.write("\nFile updated report: "+time.strftime("%d/%m/%Y-%H:%M:%S")+"\n")
                        logfile.write(str(count)+" players searched\n")
                        logfile.write(str(updated)+" players updated\n")
                        logfile.write("Be careful with:"+str(becareful)+". They have been updated by their names. There may be errors.")
                        logfile.write("\n"+str(errors))
                        logfile.write("\n")
                        logfile.write(self.players_to_purge)
                        logfile.write("did not play")
                return


        ##################################################################################################################
        #Read a elo list and get the players data. The argument listfile_rows comes from the get_list_data_from_file
        #method
        #################################################################################################################
        def update_players_data_from_list(self, listfile_rows, fide, feda, idfide, idfeda, name):
                becareful = []
                count = 0
                updated = 0
                errors = []
                for row in self.players_data:
                        for listfilerow in listfile_rows:
                                if listfilerow['IDFIDE'] != ' ' and listfilerow['IDFIDE'] != '' and listfilerow['IDFIDE'] != '0' and listfilerow['IDFIDE']==row['IDFIDE']:
                                        #print('Updating data from: '+row['NAME']+'...')
                                                #if listfilerow['IDFIDE'] != ' ' and idfide == 1:
                                                #        row['IDFIDE']=listfilerow['IDFIDE']
                                        if listfilerow['ELOFIDE'] != ' ' and fide == 1:
                                                row['ELOFIDE']=listfilerow['ELOFIDE']
                                        if listfilerow['ELONAT'] != '' and listfilerow['ELONAT'] != ' ' and feda == 1:
                                                row['ELONAT']=listfilerow['ELONAT']
                                        if listfilerow['IDNAT'] != '' and listfilerow['IDNAT'] != ' ' and idfeda == 1:
                                                row['IDNAT']=listfilerow['IDNAT']
                                        if listfilerow['KFIDE'] != ' ':
                                                row['KFIDE']=listfilerow['KFIDE']
                                        if listfilerow['NAME'] != ' ' and name == 1:
                                                row['NAME']=listfilerow['NAME']
                                        updated += 1
                                elif listfilerow['IDNAT'] != '' and listfilerow['IDNAT']==row['IDNAT']:
                                        #print('Updating data from: '+row['NAME']+'...')
                                        if listfilerow['ELONAT'] != ' ' and feda == 1:
                                                row['ELONAT']=listfilerow['ELONAT']
                                        #if listfilerow['IDNAT'] != ' ' and idfeda == 1:
                                        #       row['IDNAT']=listfilerow['IDNAT']
                                        updated += 1
                                
                                elif listfilerow['NAME']==row['NAME'] and row['ELOFIDE'] == "0" and row['IDNAT'] == "0":
                                        #print('Updating data from: '+row['NAME']+'...')
                                        becareful.append(row['NAME'])
                                        if listfilerow['IDFIDE'] != ' ' and idfide == 1:
                                                row['IDFIDE']=listfilerow['IDFIDE']
                                        if listfilerow['ELOFIDE'] != ' ' and fide == 1:
                                                row['ELOFIDE']=listfilerow['ELOFIDE']
                                        if listfilerow['ELONAT'] != ' ' and feda == 1:
                                                row['ELONAT']=listfilerow['ELONAT']
                                        if listfilerow['IDNAT'] != ' ' and idfeda == 1:
                                                row['IDNAT']=listfilerow['IDNAT']
                                        if listfilerow['KFIDE'] != ' ':
                                                row['KFIDE']=listfilerow['KFIDE']
                                        updated += 1
                        
                        count += 1
                        print("\r"+str(count)+" players searched", end="")
                print("\r"+str(count)+" players searched")
                print(str(updated)+" updates done")
                with open(os.path.join(os.getcwd(), "arbitools-report.log"), 'a') as logfile:
                        logfile.write("\nFile updated report: "+time.strftime("%d/%m/%Y-%H:%M:%S")+"\n")
                        logfile.write(str(count)+" players searched\n")
                        logfile.write(str(updated)+" updates done\n")
                        logfile.write("Be careful with:"+str(becareful)+". They have been updated by their names. There may be errors.")
                        logfile.write("\n"+str(errors))
                        #print(row)#testing

        ################################################################################################################
        #Get data from a list (fide, feda, fidefeda) and return the data in listfilerows.
        #By default, this function will use "custom_elo.csv"
        #
        #If you want to combine international and national elo, it is recommended to create a file called
        # "custom_elo.csv" in the following way:
        #
        #1. Download players_list_xml.xml from www.fide.com and the elo list from www.feda.org (for Spain)
        #2. Create a database of the players of interest for us (for example, from our country) with the typical FEDA
        #   header making sure the FIDE and FEDA codes are correct.
        #3. Update the recently created database from the FIDE list we downloaded with
        #   "arbitools-update.py -i <our_database.csv> -l fide"
        #4. Update the file obtained in step 3 with the FEDA list by:
        #   "arbitools-update.py -i <our_database_updated.csv> -l feda
        #5. Reanme the file you got from step 4 to "custom_elo.csv"
        ################################################################################################################
        def get_list_data_from_file(self, elolist, filename):
                listfile_rows=[]
                #This code is for Jesus Mena FIDE-FEDA file. This file is really useful but contain some errors,
                #because of the differences between officila FIDE elo and FEDA elo lists
                if elolist == 'fidefeda':
                        with open (filename) as csvupdatefile:
                                print('Reading data from FIDE-FEDA file...')
                                if not csvupdatefile:
                                        print("I cannot find"+filename)
                                        sys.exit()
                                reader=csv.DictReader(csvupdatefile, delimiter=';')
                                try:
                                        for row in reader:
                                                new_row=row
                                                listfile_rows.append(new_row)#we use this lines as they are, because is the same format this program uses.
                                        #print(listfile_rows)
                                        return listfile_rows
                                        
                                except csv.Error as e:
                                        sys.exit('file %s, line %d: %s' % (inputfile, DictReader.lin_num, e))
                #Now the code in case of updating from FEDA list. Remember to rename the file downloade to
                #"elo_feda.xls"
                elif elolist == 'feda' and xlrd_present == True:
                        print("Using FEDA file...")
                        workbook = xlrd.open_workbook(filename)
                        worksheet = workbook.sheet_by_index(0)
                        count = 0
                        for i in range(4, worksheet.nrows):
                                cell = ''.join(c for c in unicodedata.normalize('NFD', worksheet.cell_value(i, 1)) if unicodedata.category(c) != 'Mn') #This removes diacritics.
                                
                                if ',' in cell:
                                        cell = cell.split(',')#To separate first and last name
                                        lastnamesplit = cell[0].split(" ")#In case the surname has more than one word

                                        lastname = lastnamesplit[0].capitalize()#We leave only the first capital in the Surname
                                        firstname = cell[1].strip()#sometimes there is a blank space at the end of the name that we have to remove
                                        firstnamesplit = firstname.split(' ')
                                        firstname = firstnamesplit[0].capitalize()
                                        if len(lastnamesplit)>1:
                                                for j in range(1, len(lastnamesplit)):
                                                        lastname = lastname+' '+lastnamesplit[j].capitalize()
                                        if len(firstnamesplit)>1:
                                                for j in range(1, len(firstnamesplit)):
                                                        firstname = firstname+' '+firstnamesplit[j].capitalize()
                                        
                                        name=lastname+", "+firstname#Lastly, join everything in the variable name.
                                        
                
                                elif '.' in cell:  #I detected some mistakes in the file feda, some names are separated with a dot from the surnames, instead of using a comma.
                                        cell = cell.split('.')#Separate first and last name.
                                        lastname = cell[0].capitalize()
                                        firstname = cell[1].strip()
                                        firstname=firstname.capitalize()
                                        name = lastname+", "+firstname
                
                                else:
                                        name = cell

                                elonat = str(int(worksheet.cell_value(i, 3)))
                                idnat = str(int(worksheet.cell_value(i, 0)))
                                
                                new_row={'NAME': name, 'G': ' ', 'IDFIDE': ' ', 'ELOFIDE': ' ', 'COUNTRY': ' ', 'TITLE': ' ', 'ELONAT': elonat, 'KFIDE': ' ', 'CLUB': ' ', 'BIRTHDAY': ' ', 'KNAT': '0', 'IDNAT': idnat}
                                listfile_rows.append(new_row)
                                count += 1
                                print("\r"+str(count)+" players", end="")
                        print("\nFinished reading Elo list")
                        return listfile_rows
                #This is the code for the official FIDE elo list
                elif elolist == 'fide' and lxml_present == True:
                        try:
                                print('Reading data from FIDE list... Please be patient, is a very large file. It can take REALLY long...')
                                doc = etree.parse(filename)
                                if not doc:
                                        print("I cannot find "+filename)
                                        sys.exit()
                                root = doc.getroot()
                                count = 0
                                filtered = 0
                                name = ''
                                birthday = ''
                                sex = ''
                                title = ''
                                idfide= ''
                                rating = ''
                                k = ''
                                new_row = {}
                                nombrecompleto="" 
                                codigofide=""
                                codigofeda=""
                                for player in root:
                                        name = player.find('name').text
                                        country = player.find('country').text
                                        birthday = player.find('birthday').text
                                        sex = player.find('sex').text
                                        title = player.find('title').text
                                        idfide = player.find('fideid').text
                                        rating = player.find('rating').text
                                        k = player.find('k').text

                                        
                                        for row in self.players_data:#This file is too large, it is better to fill listfile only with players present in the tournament
                                                if self.typeoffile == "fegaxa":
                                                        nombrecompleto = row['Apellidos']+', '+row['Nombre'] #se o ficheiro e fegaxa
                                                        codigofide = row['codigoFIDE']
                                                        codigofeda = row['codigoFEDA']
                                                elif self.typeoffile == "fide" or self.typeoffile == "trf" or self.typeoffile== "csv" or self.typeoffile=="xls":
                                                        nombrecompleto = row['NAME']
                                                        codigofide = row['IDFIDE']
                                                if name == nombrecompleto or idfide == codigofide:
                                                        new_row={'NAME': name, 'G': sex, 'IDFIDE': idfide, 'ELOFIDE': rating, 'COUNTRY': country, 'TITLE': title, 'ELONAT': '', 'KFIDE': k, 'CLUB': '', 'BIRTHDAY': birthday, 'KNAT': '0', 'IDNAT': ''}
                                                        listfile_rows.append(new_row)
                                                        filtered += 1
                                        count += 1
                                        print("\r"+str(count)+" players", end="")
                                root.clear()
                                del root
                                del doc
                                print("\nFinished reading Elo list ("+str(filtered)+" filtered)") 
                                return listfile_rows

                        except etree.XMLSyntaxError:
                                print('XML parsing error.')
                                exit(1)
                elif elolist == "custom":
                        with open (filename) as csvupdatefile:
                                print('Reading data from custom elo file...')
                                if not csvupdatefile:
                                        print("I cannot find"+filename)
                                        sys.exit()
                                reader=csv.DictReader(csvupdatefile, delimiter=';')
                                try:
                                        for row in reader:
                                                new_row = row
                                                listfile_rows.append(new_row)
                                        return listfile_rows
                                except csv.Error as e:
                                        sys.exit('file %s, line %d: %s' % (inputfile, DictReader.lin_num, e))
                        
#Use the data taken from the file to fill the property crosstable. I'm not using this function. Maybe it is better to remove it from the class.
        def fill_crosstable(self):
                
                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
                numberofrounds = int(self.info['NUMBER_OF_ROUNDS'])
                for i in range(0, numberofplayers-1):
                        
                        self.crosstable[i].update({'NAME':self.playersdata[i]['NAME']})
                        for j in range(0, numberofrounds-1):
                                 nameofround = "round"+str(j+1)
                                 opponent = self.playeropponent[i].split(" ")
                                 self.crosstable[i].update({nameround:opponent[j]})
                                 

        ################################################################################################
        #Open a .csv, .txt or .veg and get the players data.
        ################################################################################################
        def get_tournament_data_from_file(self, filename):
                
                with open(filename) as csvfile:
                        #First the stuff for trf FIDE files
                        if filename.endswith('.txt') or filename.endswith('.TXT') or filename.endswith('.trf') or filename.endswith('.trfx'):
                                print("FIDE format file")
                                self.typeoffile = "trf"
                                line=' '
                                players_index = 0
                                numberofrounds = 0
                                playercount = 0
                                
                                while line:
                                        line = csvfile.readline()
                                        firstblock = line[0:3]
                                        if firstblock == "012":
                                                info = line[4:]
                                                self.info['TOURNAMENT_NAME'] = info
                                                #print(info)
                                        if firstblock == "022":
                                                info = line[4:]
                                                self.info['CITY'] = info
                                                #print(info)
                                        if firstblock == "032":
                                                info = line[4:]
                                                self.info['FED'] = info
                                                #print(info)
                                        if firstblock == "042":
                                                info = line[4:]
                                                self.info['BEGIN_DATE'] = info
                                                #print(info)
                                        if firstblock == "052":
                                                info = line[4:]
                                                self.info['END_DATE'] = info
                                                #print(info)
                                        if firstblock == "062":
                                                info = line[4:]
                                                self.info['NUMBER_OF_PLAYERS'] = info
                                                #print(info)
                                        if firstblock == "072":
                                                info = line[4:]
                                                self.info['NUMBER_OF_RATED_PLAYERS'] = info
                                        if firstblock == "082":
                                                info = line[4:]
                                                self.info['NUMBER_OF_TEAMS'] = info
                                        if firstblock == "092":
                                                info = line[4:]
                                                self.info['TYPE_OF_TOURNAMENT'] = info
                                        if firstblock == "102":
                                                info = line[4:]
                                                self.info['ARBITER'] = info
                                                #print(info)
                                        if firstblock == "112":
                                                info = line[4:]
                                                self.info['DEPUTY'] = info
                                        if firstblock == "122":
                                                info = line[4:]
                                                self.info['ALLOTED_TIME'] = info
                                        if firstblock == "022":
                                                info = line[4:]
                                                self.info['CITY'] = info
                                                #print(info)
                                        if firstblock == "132": #Round dates information
                                                offset = 0
                                                while 1:
                                                        date = line[91+offset:99+offset]
                                                        offset += 10
                                                        if not date:
                                                                break
                                                        self.dates.append(date.strip())
                                                        self.info['DATES'] = self.info['DATES']+date.strip()+"  "
                                                        numberofrounds += 1                                               
                                                self.info['NUMBER_OF_ROUNDS'] = numberofrounds-1 #This is not correct, but the info is not always available in this file format and we need to fill the variable.
                                                self.info['CURRENT_ROUND'] = numberofrounds-1
                                                if self.info['CURRENT_ROUND'] < 0:
                                                        self.info['CURRENT_ROUND'] = 0
                                        if firstblock == "001": #Players information
                                                sex = line[9].strip()
                                                title = line[10:13].strip()
                                                name = line[14:47].strip()
                                                fide = line[48:52].strip()
                                                fed = line[53:56].strip()
                                                idfide = line[57:68].strip()
                                                birthday = line[69:79].strip()
                                                points = line[80:84].strip()
                                                rank = line[85:89].strip()
                                                roundblock = ' '
                                                offset = 0
                                                numberofrounds = 0 #This variable is to count the number of rounds. This data is not in the TRF format.
                                                
                                                playersopponent_temp = ''
                                                playerscolor_temp = ''
                                                playersresults_temp = ''
                                                didnotplay = True
                                                
                                                for i in range(1, len(self.dates)):
                                                       
                                                       opponent = line[91+offset:95+offset].strip()
                                                       color = line[96+offset:97+offset].strip()
                                                       
                                                       result = line[98+offset:99+offset].strip()
                                                       
                                                       offset += 10
                                                       if not opponent: #Fill empty rounds with data
                                                              playersopponent_temp = playersopponent_temp+" 0000"
                                                              playerscolor_temp = playerscolor_temp+" -"
                                                              playersresults_temp = playersresults_temp+" 0"
                                                       else: #If there is data, use the actual data
                                                              playersopponent_temp = playersopponent_temp+" "+opponent.strip()
                                                              playerscolor_temp = playerscolor_temp+" "+color.strip()
                                                              if color.strip() == "w" or color.strip() == "b":
                                                                      didnotplay = False
                                                              playersresults_temp = playersresults_temp+" "+result.strip()
                                                       
                                                if didnotplay == True:
                                                       self.players_to_purge.append(name)    
                                                new_row={'NAME': name, 'G': sex, 'IDFIDE': idfide, 'ELOFIDE': fide, 'COUNTRY': fed, 'TITLE': title, 'BIRTHDAY': birthday, 'POINTS':points, 'RANK':rank, 'IDNAT':"0", 'ELONAT':'0'}
                                        
                                                self.playersopponent.append(playersopponent_temp.strip())
                                                #print(playersopponent_temp.strip())#testing
                                                self.playerscolor.append(playerscolor_temp.strip())
                                                self.roundresults.append(playersresults_temp.strip())
                                                

                                                #print(new_row)
                                                self.players_data.append(new_row)
                                                players_index += 1
                                                playercount += 1
                                        if firstblock == "013": #Teams information, have to check
                                                info = line[4:35] #I am not sure of this, trf specification says 36, but it works
                                                self.teamnames.append(info)
                                                #get the players for each team
                                                offset = 0
                                                teammembers = []
                                                while 1:
                                                        member = line[36+offset:40+offset]
                                                        offset += 5
                                                        if not member:
                                                                break
                                                        teammembers.append(member.strip())
                                                self.teamsmembers.append(teammembers)
         
                                if len(self.players_to_purge) > 0:
                                        print(self.players_to_purge, end='')
                                        print("did not play")
                        #Now for the files from Vega. They announced a new xml format. TODO
                        if filename.endswith('.veg'):
                                self.typeoffile = "veg"
                                print(".veg file. Don't worry, I won't touch the original. It will be backed up.")

                                #Read the header of the .veg file
                                #for i in range(12):#Reserve the first lines of the .veg file. It is where the tournament info is.
                                line = csvfile.readline()#read the first line in the .veg file. That's the header.
                                self.vegaheader.append(line)
                                line = csvfile.readline()#read the second line. It's the tournament's name.
                                self.vegaheader.append(line)
                                self.info['TOURNAMENT_NAME'] = line
                                line = csvfile.readline()#Line 3. The city's name.
                                self.vegaheader.append(line)
                                self.info['CITY'] = line
                                line = csvfile.readline()#Line 4. Federation.
                                self.vegaheader.append(line)
                                self.info['FED'] = line
                                line = csvfile.readline()#Line 5. The end and begin dates. We have to split them in order to store them.
                                self.vegaheader.append(line)
                                endandstartdates = line.split(',')
                                self.info['BEGIN_DATE'] = endandstartdates[0].strip()+"\n"
                                self.info['END_DATE'] = endandstartdates[1].strip()+"\n"
                                line = csvfile.readline()#Line 6. Arbiter.
                                self.vegaheader.append(line)
                                self.info['ARBITER'] = line
                                line = csvfile.readline()#line 7. Points for draw. I'm not using this one right now.
                                self.vegaheader.append(line)
                                #Add here the code to include this in the tournament info dictionary
                                line = csvfile.readline()#Line 8. Tiebreaks
                                self.vegaheader.append(line)
                                self.info['TIEBREAKS'] = line
                                line = csvfile.readline()#Line 9. Round info. I will store the number of rounds only.
                                self.vegaheader.append(line)
                                roundinfo = line.split(" ")
                                self.info['NUMBER_OF_ROUNDS'] = roundinfo[0]
                                self.info['CURRENT_ROUND'] = int(roundinfo[2])
                                line = csvfile.readline()#Line 10. Unused by the moment.
                                self.vegaheader.append(line)
                                line = csvfile.readline()# Line 11. Unused by the moment. 
                                self.vegaheader.append(line)
                                line = csvfile.readline()# Line 12. Number of players.
                                self.vegaheader.append(line)
                                self.info['NUMBER_OF_PLAYERS'] = line
                                self.info['NUMBER_OF_TEAMS'] = "0\n"
                                self.info['TYPE_OF_TOURNAMENT'] = "Individual: Swiss System Dutch\n"
                                headerline=csvfile.readline()#This is the line with the names of the fields.
                                csvfile.seek(0)#Reset the file pointer.
                                lines = csvfile.readlines()[12:]#Read from 12th line, where the players data is.
                                self.headeroutputvega = headerline


                        #Now we store the players data in a dictionary
                                #The first one is the line with the names of the fields. It is also the header for the csv output.
                                self.header = lines[0].split(';')
                                
                                for i in range(14):
                                        self.header[i] = self.header[i].strip()#Remove the spaces we don't need.
                                
                                csvfile.seek(0)
                                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
                                endofrange = 13+numberofplayers #Calculate where the players data end.
                                lines = csvfile.readlines()[13:endofrange] #Read the lines where the players data is.
                                
                                numberofratedplayers = 0
                                for line in lines:
                                        if line[2] != '' and line[2] != "0" and line[2] != " ":
                                                numberofratedplayers +=1
                                self.info['NUMBER_OF_RATED_PLAYERS'] = str(numberofratedplayers)+"\n"
                        #Lastly, we read the .veg file to the end.

                                
                                csvfile.seek(0)
                                
                                endofrangenext = endofrange+numberofplayers+1 #The next jump is again the number of players plus a title line. The information here is the players colors.
                                restofvegapointer = csvfile.readlines()[endofrange:endofrangenext]#Jump to the end of the players data.
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)

                                        linesplit = restofvegapointer[i].strip().split(' ') #Split the string, remove the name of the player and some extra spaces in order to store just the information that is useful.
                                        while True:
                                                try:
                                                        linesplit.remove("")
                                                except ValueError:
                                                        break
                                        for j in range(len(linesplit)):
                                                if linesplit[j] == "-1":
                                                        linesplit[j] = "b"
                                                if linesplit[j] == "1":
                                                        linesplit[j] = "w"
                                                if linesplit[j] == "0":
                                                        linesplit[j] = "-"
                                        del linesplit[0]#We don't need the first part. It's the players number.
                                      
                                        #add the code to put W and B
                                        if i > 0:  #We don't need the first line of this block. It's a comment.
                                                line = " ".join(linesplit).strip()
                                                #print(line)
                                                self.playerscolor.append(line) #Store the data.
                                
                                
                                
                                csvfile.seek(0)
                                endofrange = endofrangenext+numberofplayers+1 #Next jump. Players opponents.
                                restofvegapointer = csvfile.readlines()[endofrangenext:endofrange]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)

                                        linesplit = restofvegapointer[i].strip().split(' ') #Split the strig, remove the name of the player and some extra spaces in order to store just the information that is useful.
                                        while True:
                                                try:
                                                        linesplit.remove("")
                                                except ValueError:
                                                        break
                                        for j in range(len(linesplit)):
                                                if linesplit[j] == "0":
                                                        linesplit[j] = "0000"

                                        del linesplit[0]
                                                                           
                                        if i > 0:
                                                line = " ".join(linesplit)
                                                #print(line)#testing
                                                self.playersopponent.append(line.strip()) #We store the data in the property.

                                csvfile.seek(0)
                                endofrangenext = endofrange+numberofplayers+1
                                restofvegapointer = csvfile.readlines()[endofrange:endofrangenext]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)

                                        linesplit = restofvegapointer[i].strip().split() #Split the strig, remove the name of the player and some extra spaces in order to store just the information that is useful.
                                        while True:
                                                try:
                                                        linesplit.remove("")
                                                except ValueError:
                                                        break
                                        del linesplit[0]
                                        

                                        if i > 0:
                                                line = " ".join(linesplit)
                                                self.playersfloater.append(line.strip()) 


                                
                                csvfile.seek(0)
                                endofrange = endofrangenext+numberofplayers+1
                                restofvegapointer = csvfile.readlines()[endofrangenext:endofrange]
                                
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)
                                        
                                        linesplit = restofvegapointer[i].strip().split(' ') #Split the strig, remove the name of the player and some extra spaces in order to store just the information that is useful.
                                        while True:
                                                try:
                                                        linesplit.remove("")
                                                except ValueError:
                                                        break
                                        for j in range(len(linesplit)): #Change .veg file values to normal values.
                                                if linesplit[j] == "2":
                                                        linesplit[j] = "="
                                                if linesplit[j] == "6":
                                                        linesplit[j] = "="
                                                if linesplit[j] == "3":
                                                        linesplit[j] = "1"
                                                if linesplit[j] == "4":
                                                        linesplit[j] = "0"
                                                if linesplit[j] == "8":
                                                        linesplit[j] = "="

                                        del linesplit[0]
                                        #print(linesplit)
                                        if i > 0:
                                                line = " ".join(linesplit)
                                                #print(line)#testing
                                                self.roundresults.append(line.strip())
                                                                
                                csvfile.seek(0)
                                restofvegapointer = csvfile.readlines()[endofrange:]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line) #I don't use this data. Just store it like it is to put it back in the file in the output.


                                #print(self.playersopponent)
                                        
                                for line in lines:
                                        new_row = {}
                                        line = line.split(';')

                                        for i in range(len(line)):
                                                line[i] = line[i].strip()
                                                new_row[self.header[i]] = line[i]
                                        self.players_data.append(new_row)

                                #Write the points for each player.
                                playerspoints = []
                                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
                                for i in range(0, numberofplayers):
                                

                                        playersresults = self.roundresults[i].split(" ")
                                        
                                        for result in playersresults:
                                                result = result.strip()
                                        #print(playersresults)#testing
                                        points = 0.0
                                        for j in range(0, len(playersresults)):
                                                if playersresults[j] == "=":
                                                        points += 0.5
                                                if playersresults[j] == "1":
                                                        points += 1
                                        
                                        playerspoints.append(str(points))
                                                                                
                                        self.players_data[i].update({'POINTS' : str(points)})
                                        self.players_data[i].update({'RANK': '0'})#This is not the correct rank. Fix it!!!.
                                        #print(self.players_data[i])#testing
                                
                                csvfile.seek(0)

                        #In case of .csv files, with the Vega header, described in the documentation
                        if filename.endswith('.csv'):
                                self.typeoffile = 'csv'
                                reader = csv.DictReader(csvfile, delimiter=';')
                                self.header = reader.fieldnames
                                #print(self.header)
                                #Remove the spaces from the fields
                                
                                for i in range(0, len(reader.fieldnames)):
                                        reader.fieldnames[i] = reader.fieldnames[i].strip()
                                                               
                                try:
                                        print('Reading csv file...')
                                        for row in reader:
                                                for i in row:
                                                        row[i] = row[i].strip()
                                                new_row = row   
                                                self.players_data.append(new_row)
                                except csv.Error as e:
                                        sys.exit('file %s, line %d: %s' % (inputfile, DictReader.line_num, e))
                        if filename.endswith('.xls') and xlrd_present == True:
                                self.typeoffile = 'xls'
                                print("Reading file. Excel format (galician league).")
                                header = ['NAME', 'COUNTRY', 'BIRTHDAY', 'G', 'TITLE', 'IDFIDE', 'ELOFIDE', 'KFIDE', 'IDNAT', 'ELONAT', 'K', 'CLUB']
                                self.header = header
                                workbook = xlrd.open_workbook(filename)
                                worksheet = workbook.sheet_by_index(0)
                                count = 0
                                for i in range(1, worksheet.nrows):
                                        
                                        cell = ''.join(c for c in unicodedata.normalize('NFD', worksheet.cell_value(i, 10)) if unicodedata.category(c) != 'Mn') #This removes diacritics.
                                        #cell = str(worksheet.cell_value(i, 10))
                                        cellsplit = cell.split(' ')
                                        cellsplithyphen = cellsplit[0].split('-')
                                        surname = cellsplithyphen[0].capitalize()
                                        if len(cellsplithyphen)>1:
                                                for j in range(1, len(cellsplithyphen)):
                                                        surname = surname+'-'+cellsplithyphen[j].capitalize()   
                                        if len(cellsplit)>1:
                                                for j in range(1, len(cellsplit)):
                                                        cellsplithyphen = cellsplit[j].split('-')
                                                        surname = surname+' '+cellsplithyphen[0].capitalize()
                                                        if len(cellsplithyphen)>1:
                                                                for k in range(1, len(cellsplithyphen)):
                                                                       surname = surname+'-'+cellsplithyphen[k].capitalize()        
                                        cell = str(worksheet.cell_value(i, 11))
                                        cellsplit = cell.split(' ')
                                        firstname = cellsplit[0].capitalize()
                                        if len(cellsplit)>1:
                                                for j in range(1, len(cellsplit)):
                                                        firstname = firstname+' '+cellsplit[j].capitalize()
                                        name = surname+', '+firstname
                                        idfide = str(int(worksheet.cell_value(i, 5)))
                                        birthday = str(worksheet.cell_value(i, 7))
                                        feda = str(int(worksheet.cell_value(i, 4)))
                                        idfeda = str(int(worksheet.cell_value(i, 3)))
                                        fide = str(int(worksheet.cell_value(i, 6)))
                                        fed = str(worksheet.cell_value(i, 8))
                                        title = str(worksheet.cell_value(i, 2))
                                        sex = str(worksheet.cell_value(i, 9))
                                        new_row={'NAME': name, 'COUNTRY': fed, 'BIRTHDAY': birthday, 'G': sex, 'TITLE': title, 'IDFIDE': idfide, 'ELOFIDE': fide,  'KFIDE': '0', 'IDNAT': idfeda, 'ELONAT': feda, 'K': '0', 'CLUB': ' '}
                                        #print(surname+', '+firstname)
                                        self.players_data.append(new_row)
                                        count += 1
                                        print("\r"+str(count)+" players", end="")
                                print("\nFinished reading file")

                        #Now, a special case for a concrete format used by fegaxa
                        if filename.endswith(".fegaxa") and xlrd_present == True: #Database file in fegaxa format
                                self.typeoffile = "fegaxa"
                                print("Reading file. Fegaxa format....")
                                header = ['codigoFADA', 'codigoFEDA', 'codigoFIDE', 'DNI', 'LetraFinal', 'Apellidos', 'Nombre', 'FechaNacimiento', 'Hombre', 'email', 'Direccion', 'Telefono', 'Nacionalidad', 'Federado', 'NombreClub', 'Provincia', 'CodJugador', 'nombreLocalidad', 'Localidad', 'EloFADA', 'EloFEDA', 'EloFIDE']
                                self.header = header
                                workbook = xlrd.open_workbook(filename)
                                worksheet = workbook.sheet_by_index(0)
                                count = 0
                                for i in range(1, worksheet.nrows):
                                        cell = str(worksheet.cell_value(i, 5))
                                        cellsplit = cell.split(' ')
                                        cellsplithyphen = cellsplit[0].split('-')
                                        surname = cellsplithyphen[0].capitalize()
                                        if len(cellsplithyphen)>1:
                                                for j in range(1, len(cellsplithyphen)):
                                                        surname = surname+'-'+cellsplithyphen[j].capitalize()   
                                        if len(cellsplit)>1:
                                                for j in range(1, len(cellsplit)):
                                                        cellsplithyphen = cellsplit[j].split('-')
                                                        surname = surname+' '+cellsplithyphen[0].capitalize()
                                                        if len(cellsplithyphen)>1:
                                                                for k in range(1, len(cellsplithyphen)):
                                                                       surname = surname+'-'+cellsplithyphen[k].capitalize()   
                                        cell = str(worksheet.cell_value(i, 6))
                                        cellsplit = cell.split(' ')
                                        firstname = cellsplit[0].capitalize()
                                        if len(cellsplit)>1:
                                                for j in range(1, len(cellsplit)):
                                                        secondname = cellsplit[j]
                                                        if secondname != "II":
                                                                firstname = firstname+' '+secondname.capitalize()
                                                        else:
                                                                firstname = firstname+' '+secondname

                                        idfeda = str(worksheet.cell_value(i, 1))
                                        if idfeda != ' ':
                                                idfedasplit = idfeda.split('.')
                                                idfeda = idfedasplit[0]
                                        idfide = str(int(worksheet.cell_value(i, 2)))
                                        dni = str(worksheet.cell_value(i, 3))
                                        letradni = str(worksheet.cell_value(i, 4))
                                        
                                        birthday = str(worksheet.cell_value(i, 7))
                                        sex = str(worksheet.cell_value(i, 8)) #1 hombre, 0 mujer
                                        email = str(worksheet.cell_value(i, 9))
                                        address = str(worksheet.cell_value(i,10))
                                        telephone = str(worksheet.cell_value(i, 11))
                                        nationality = str(worksheet.cell_value(i, 12))
                                        federated = str(worksheet.cell_value(i, 13))
                                        club = str(worksheet.cell_value(i, 14))
                                        province = str(worksheet.cell_value(i, 15))
                                        code = str(worksheet.cell_value(i, 16))
                                        cityname = str(worksheet.cell_value(i, 17))
                                        city = str(worksheet.cell_value(i, 18))
                                        
                                        feda = str(worksheet.cell_value(i,20))
                                        fide = str(worksheet.cell_value(i, 21))
                                        title = str(worksheet.cell_value(i, 2))
                                        
                                        new_row={'codigoFADA': '0', 'codigoFEDA': idfeda, 'codigoFIDE': idfide, 'DNI': dni, 'LetraFinal': letradni, 'Apellidos': surname, 'Nombre': firstname, 'FechaNacimiento': birthday, 'Hombre': sex, 'email': email, 'Direccion':address, 'Telefono': telephone, 'Nacionalidad': nationality, 'Federado': federated, 'NombreClub': club, 'Provincia': province, 'CodJugador': code, 'nombreLocalidad':cityname, 'Localidad':city, 'EloFADA':'0', 'EloFEDA':feda, 'EloFIDE':fide}
                                        #print(surname+', '+firstname)
                                        self.players_data.append(new_row)
                                        count += 1
                                        print("\r"+str(count)+" players", end="")
                                print("\nFinished reading file")

        #Add new players to players_data
        def add_players_data_from_file(self, addfile):
                foundit = 0
                addfile_rows=[]
                with open(addfile) as csvaddfile:
                        print("Reading new data...")
                        reader = csv.DictReader(csvaddfile, delimiter = ";")
                        header = reader.fieldnames
                        for i in range(0, len(reader.fieldnames)):
                                reader.fieldnames[i] = reader.fieldnames[i].strip()
                                
                        try:
                                for row in reader:
                                        new_row = row
                                        addfile_rows.append(new_row)
                                
                        except csv.Error as e:
                                sys.exit('file %s, line %d: %s' % (inputfile, DictReader.line_num, e))
                        
                lenplayersdata = len(self.players_data)
                lenaddfile = len(addfile)
                
                for addrow in addfile_rows:
                        for i in range(0, lenplayersdata):
                                addrow['NAME'] = addrow['NAME'].strip()
                                self.players_data[i]['NAME'] = self.players_data[i]['NAME'].strip()
                                if addrow['NAME']==self.players_data[i]['NAME']:
                                        print("Not adding "+addrow['NAME']+". The player is already in the file.")
                                        foundit = 1
                                        break
                                #print(addrow['NAME']+" y "+self.players_data[i]['NAME']+" no son iguales")
                        if foundit == 0:
                                print("Add:" +addrow['NAME'])
                                self.players_data.append(addrow)
                        foundit = 0
                                
                                
                #print(self.players_data)
        def purge_tournament(self):
                #for index,player in enumerate(self.players_data):
                #        for player_to_purge in self.players_to_purge:
                #        
                #                if player['NAME'] == player_to_purge:
                #                        if player['ELOFIDE'] != "0":
               #                                 self.info['NUMBER_OF_RATED_PLAYERS'] = str(int(self.info['NUMBER_OF_RATED_PLAYERS']) - 1)+"\n"
                #                        self.indexes_to_purge.append(index+1) #store the index in order to skip it in export
                #                        self.players_data.remove(player)
                #                        del self.playerscolor[index]
                #                        del self.playersopponent[index]
                #                        del self.roundresults[index]
                #                        self.info['NUMBER_OF_PLAYERS'] = str(int(self.info['NUMBER_OF_PLAYERS']) - 1)+"\n"
                #print(self.players_data)
                self.purged = True
                logfilepath = os.path.join(os.getcwd(),"arbitools-report.log")
                with open(logfilepath, 'a') as logfile: #TESTING
                        logfile.write("\nFile purge report: "+time.strftime("%d/%m/%Y-%H:%M:%S")+"\n")
                        logfile.write("\n")
                        logfile.write(str(self.players_to_purge))
                        logfile.write("did not play")
                return

