#---------------------arbitools-------------------------
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
import sys
import csv
import unicodedata
from collections import namedtuple
from operator import itemgetter
from itertools import dropwhile, compress
import PyRP
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

class Tournament:

        def __init__(self):
                        
                self.info={'TOURNAMENT_NAME':' ', 'CITY':' ', 'FED':' ', 'BEGIN_DATE':' ', 'END_DATE':' ', 'ARBITER':' ', 'DEPUTY':' ', 'TIEBREAKS':' ', 'NUMBER_OF_ROUNDS':' ', 'CURRENT_ROUND':' ', 'NUMBER_OF_PLAYERS':' ', 'NUMBER_OF_RATED_PLAYERS':' ', 'NUMBER_OF_TEAMS':' ', 'TYPE_OF_TOURNAMENT':' ', 'ALLOTED_TIME':' ', 'DATES': ' '}
                self.standings=[]
                self.dates=[]

                self.players_data = []
                self.crosstable = []

                
                
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
                

        #Output players_data, tournament info or both to a file (.veg, .csv, .txt)      
        def output_to_file(self, inputfile):
                outputfile = ''
                if self.players_data == '':
                        print("I don't have anything to write in the file")
                        sys.exit()
                inputfilesplit = inputfile.split('.')#Separate file name and extension.
                outputfiletxt=inputfilesplit[0]+'_updated'+'.txt' #The name for the .txt file.
                if inputfile.endswith('.csv'):
                        outputfile=inputfilesplit[0]+'_updated'+'.csv'#Get the name for the updated file.
                elif inputfile.endswith('.veg'):
                        outputfile=inputfilesplit[0]+'_updated'+'.veg'
                elif inputfile.endswith('.txt'):
                        true = True
                else:
                        print("I don't have a filter for this file format.")
                if inputfile.endswith('.csv') or inputfile.endswith('.veg'):
                        with open(outputfile, 'w') as csvoutputfile:
                                writer = csv.DictWriter(csvoutputfile, fieldnames=self.header, delimiter=';')
                                if inputfile.endswith('.csv'):
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


        #Print standings to file
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
                        txtoutputfile.write("082 "+self.info['NUMBER_OF_TEAMS'])#Number of teams. Implement in the future, by now, only tournaments without teams.
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
                        dates = "132                                                                                        "#We need spaces until position 92. Maybe there is a better way of doing this...
                        dates = dates+self.info['DATES']
                        txtoutputfile.write(dates)
                        #if self.info['DATES'] == ' ':
                        txtoutputfile.write("\n")
                        count = 1
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
                                        countstr = " "*extra+str(count)
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
                                        birthdaystr = " "*extra+player['BIRTHDAY']
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
                                        if len(playersopponentsplit[i]) < 4:
                                                extra = 4-len(playersopponentsplit[i])
                                                opponent = " "*extra+playersopponentsplit[i]
                                        else:
                                                opponent = playersopponentsplit[i]
                                        color = playerscolorsplit[i]
                                        result = roundresultssplit[i]
                                        roundsstr = roundsstr+" "+opponent+" "+color+" "+result
                                        offset += 10
                                playerdata = "001 "+countstr+" "+player['G']+titlestr+" "+namestr+" "+elostr+" "+player['COUNTRY']+" "+idfidestr+" "+birthdaystr+" "+pointsstr+" "+rankstr+"  "+roundsstr
                                txtoutputfile.write(playerdata+"\n")
                                count += 1
                return



        def standings_to_file(self, inputfile):
                inputfilestrip = inputfile.split('.')
                outputfile = inputfilestrip[0]+"_standings.txt"
                outputfileTeX = inputfilestrip[0]+"_standings.tex"
                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
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
                if inputfile.endswith('.txt') or inputfile.endswith('.trfx'):
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
                with open("tex_header.txt") as texheaderfile:
                        tex_header = texheaderfile.read()
                with open("tex_middle.txt") as texmiddlefile:
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

        #Apply recursive tiebreaks to standings
        def applyARPO(self, inputfile):
                lines = []#This is the list PyRP takes. We have to fill it with the players and tournament info.
                             
                for i in range(0, len(self.players_data)):
                        opponents = self.playersopponent[i].split(' ')
                        colors = self.playerscolor[i].split(' ')
                        results = self.roundresults[i].split(' ')
                        
                                                
                        line = [i+1, i+1, self.players_data[i]['TITLE'], self.players_data[i]['NAME'], self.players_data[i]['ELOFIDE'], self.players_data[i]['COUNTRY']]
                        
                        for j in range(0, int(self.info['CURRENT_ROUND'])-1):
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
                print(lines)#testing
                index_rounds = []
                roundcount = 6
                limit = self.info['CURRENT_ROUND']*3+6
                while roundcount <= self.info['CURRENT_ROUND']*3:
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
                index_points = 3+self.info['CURRENT_ROUND']*3 #I don't really understand why 3+ and not 5+, since there are 5 fields and then the fields for the rounds.
                
                RPtournament._points = [RPtournament._calculate_points(line[index_points], draw_character="x") for line in compress(lines, RPtournament._number_of_opponents)]
                
                RPtournament._played_points = [RPtournament._calculate_played_points(line, index_rounds, "x") for line in compress(lines, RPtournament._number_of_opponents)]
                RPtournament._number_of_opponents = list(compress(RPtournament._number_of_opponents, RPtournament._number_of_opponents))
                
                RPtournament._number_of_rounds = len(index_rounds)
                #print(RPtournament._points)#testing
                #print(self.info['NUMBER_OF_PLAYERS'])#testing
                #print(self.players_data)#testing
                inputfilesplit = inputfile.split('.')
                outputfile = inputfilesplit[0]+"_ARPO.csv"
                RPtournament.run(methods_list = ({'method': 'Name'}, {'method': 'Points'}, {'method': 'Bucholz'}, {'method': 'ARPO', 'worst': 1, 'best': 1}, {'method': 'Performance'}), output_file = outputfile)
                
                
                return

        #Read a elo list and get the players data. The argument listfile_rows comes from the get_list_data_from_file method 
        def update_players_data_from_list(self, listfile_rows, method, fide, feda, idfide, idfeda):
                for row in self.players_data:
                        for listfilerow in listfile_rows:
                                if method == 'idfide':
                                        if listfilerow['IDFIDE']==row['IDFIDE']:
                                                print('Updating data from: '+row['NAME']+'...')
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
                                if method == 'name':
                                        if listfilerow['NAME']==row['NAME']:
                                                print('Updating data from: '+row['NAME']+'...')
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
                          
                        #print(row)#testing


        #Get data from a list (fide, feda, fidefeda) and return the data in listfilerows. 
        #Searching by code or by name is possible
        def get_list_data_from_file(self, elolist, filename, method):
                listfile_rows=[]
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

                if elolist == 'feda' and xlrd_present == True:
                        print("Using FEDA file...")
                        workbook = xlrd.open_workbook(filename)
                        worksheet = workbook.sheet_by_index(0)

                        for i in range(4, worksheet.nrows):
                                cell = ''.join(c for c in unicodedata.normalize('NFD', worksheet.cell_value(i, 1)) if unicodedata.category(c) != 'Mn') #This removes diacritics.
                                
                                if ',' in cell:
                                        cell = cell.split(',')#To separate first and last name
                                        lastnamesplit = cell[0].split(" ")#In case the surname has more than one word

                                        lastname1 = lastnamesplit[0].capitalize()#We leave only the first capital in the Surname
                                        firstname = ''
                                        lastname = ''
                                        lastname2 = ''
                                        if len(lastnamesplit)>1:
                                                lastname2 = lastnamesplit[1].capitalize()
                                                lastname = lastname1+" "+lastname2
                                        elif len(lastnamesplit) == 1:
                                                lastname = lastname1
                                        
                                        firstname = cell[1].strip()#To remove the space in front of the name, because it was after the comma.
                                        firstnamesplit = firstname.split(" ")
                                        firstname1 = firstnamesplit[0].capitalize()
                                        firstname2 = ''
                                        if len(firstnamesplit)>1:
                                                firstname2 = firstnamesplit[1].capitalize()
                                                firstname = firstname1+" "+firstname2
                                        elif len(firstnamesplit) == 1:
                                                firstname = firstname1
                                        
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
                        return listfile_rows

                if elolist == 'fide' and lxml_present == True:
                        try:
                                print('Reading data from FIDE list... Please be patient, is a very large file')
                                doc = etree.parse(filename)
                                if not doc:
                                        print("I cannot find "+filename)
                                        sys.exit()
                                root = doc.getroot()
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
                                                if name == row['NAME']:
                                                        new_row={'NAME': name, 'G': sex, 'IDFIDE': idfide, 'ELOFIDE': rating, 'COUNTRY': country, 'TITLE': title, 'ELONAT': '', 'KFIDE': k, 'CLUB': '', 'BIRTHDAY': birthday, 'KNAT': '0', 'IDNAT': ''}
                                                        listfile_rows.append(new_row)
                                        return listfile_rows

                        except etree.XMLSyntaxError:
                                print('XML parsing error.')
                                exit(1)
        
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
                                 


        #Open a .csv, .txt or .veg and get the players data.
        def get_tournament_data_from_file(self, filename):
                
                with open(filename) as csvfile:
                        if filename.endswith('.txt') or filename.endswith('.trf') or filename.endswith('.trfx'):
                                print("FIDE format file")
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
                                                              playersresults_temp = playersresults_temp+" "+result.strip()
                                                       
                                                    
                                                new_row={'NAME': name, 'G': sex, 'IDFIDE': idfide, 'ELOFIDE': fide, 'COUNTRY': fed, 'TITLE': title, 'BIRTHDAY': birthday, 'POINTS':points, 'RANK':rank}
                                        
                                                self.playersopponent.append(playersopponent_temp.strip())
                                                self.playerscolor.append(playerscolor_temp.strip())
                                                self.roundresults.append(playersresults_temp.strip())
                                                

                                                #print(new_row)
                                                self.players_data.append(new_row)
                                                players_index += 1
                                                playercount += 1
        
                                #print(self.playersopponent)
                        if filename.endswith('.veg'):
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
                                self.info['BEGIN_DATE'] = endandstartdates[0]
                                self.info['END_DATE'] = endandstartdates[1].strip()
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

                        #Lastly, we read the .veg file to the end.

                                
                                csvfile.seek(0)
                                
                                endofrangenext = endofrange+numberofplayers+1 #The next jump is again the number of players plus a title line. The information here is the players colors.
                                restofvegapointer = csvfile.readlines()[endofrange:endofrangenext]#Jump to the end of the players data.
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
                                                if linesplit[j] == "-1":
                                                        linesplit[j] = "b"
                                                if linesplit[j] == "1":
                                                        linesplit[j] = "w"
                                                if linesplit[j] == "0":
                                                        linesplit[j] = "-"
                                        del linesplit[0]
                                      
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
                        if filename.endswith('.csv'):
                                reader = csv.DictReader(csvfile, delimiter=';')
                                self.header = reader.fieldnames
                                #Remove the spaces from the fields
                                
                                for i in range(0, len(reader.fieldnames)):
                                        reader.fieldnames[i] = reader.fieldnames[i].strip()
                                                               
                                try:
                                        print('Reading file...')
                                        for row in reader:
                                                for i in row:
                                                        row[i] = row[i].strip()
                                                new_row = row   
                                                self.players_data.append(new_row)
                                except csv.Error as e:
                                        sys.exit('file %s, line %d: %s' % (inputfile, DictReader.line_num, e))

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

