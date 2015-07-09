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
                        
                self.info={'TOURNAMENT_NAME':'', 'CITY':'', 'FED':'', 'BEGIN_DATE':'', 'END_DATE':'', 'ARBITER':'', 'DEPUTY':'', 'TIEBREAKS':'', 'NUMBER_OF_ROWS':'', 'CURRENT_ROUND':'', 'NUMBER_OF_PLAYERS':''}
                self.standings=[]

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
                if self.players_data == '':
                        print("I don't have anything to write in the file")
                        sys.exit()
                inputfilesplit = inputfile.split('.')#Separate file name and extension.
                if inputfile.endswith('.csv'):
                        outputfile=inputfilesplit[0]+'_updated'+'.csv'#Get the name for the updated file.
                if inputfile.endswith('.veg'):
                        outputfile=inputfilesplit[0]+'_updated'+'.veg'
                if inputfile.endswith('.txt'):
                        outputfile=inputfilesplit[0]+'_updated'+'.txt'
                else:
                        print("I don't have a filter for this file format.")
                with open(outputfile, 'w') as csvoutputfile:
                        writer = csv.DictWriter(csvoutputfile, fieldnames=self.header, delimiter=';')
                        if inputfile.endswith('.csv'):
                                writer.writeheader()
#This code is for .veg and .csv only. I have to write the code for .txt
                        try:
                                if inputfile.endswith('.veg'):
                                        csvoutputfile.writelines(self.vegaheader)
                                        csvoutputfile.writelines(self.headeroutputvega)
                                writer.writerows(self.players_data)
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
        def standings_to_file(self, inputfile):
                inputfilestrip = inputfile.split('.')
                outputfile = inputfilestrip[0]+"_standings.txt"
                outputfileTeX = inputfilestrip[0]+"_standings.tex"
                numberofplayers = int(self.info['NUMBER_OF_PLAYERS'])
                currentround = int(self.info['CURRENT_ROUND'])
                #tex_header = []
                #tex_middle = []
                playerspoints = []
                if inputfile.endswith('.veg'):
                        for i in range(0, numberofplayers):
                                playersresults = self.roundresults[i].split(" ")
                                playerspoints.append(0)
                                for j in range(4, 4+currentround-1):
                                        playerspoints[i] += int(playersresults[j])
                                
                        for i in range(0, numberofplayers):
                                line = {'NAME':self.players_data[i]['NAME'], 'POINTS':playerspoints[i]}
                                self.standings.append(line)
                if inputfile.endswith('.txt') or inputfile.endswith('.trfx'):
                        for i in range(0, numberofplayers):
                                line = {'NAME':self.players_data[i]['NAME'], 'POINTS':self.players_data[i]['POINTS']}
                                self.standings.append(line)
                newlist = sorted(self.standings, key=itemgetter('POINTS'), reverse=True)        
                
#Writing the text file
                with open(outputfile, 'w') as csvoutputfile:
                        print("Writing .txt file...")
                        csvoutputfile.write(self.info['TOURNAMENT_NAME']+"\n")
                        csvoutputfile.write("Standings\n")
                        for i in range(0, len(newlist)):
                                line = newlist[i]['NAME']+" "+str(newlist[i]['POINTS'])
                                csvoutputfile.write(line)
                                csvoutputfile.write("\n")
                                
#Writing the LaTeX file
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
                        csvoutputfile.write("\\begin{tabular}{p{8cm}l}")
                        for i in range(0, len(newlist)):
                                line = newlist[i]['NAME']+"&"+str(newlist[i]['POINTS']+"\\\\")
                                csvoutputfile.write(line)
                                csvoutputfile.write("\n\n")
                        csvoutputfile.write("\\end{tabular}")
                        csvoutputfile.write("\\end{document}")

        #Apply recursive tiebreaks to standings
        def applyARPO(self, inputfile):
                RPtournament = MyRP.Tournament.load(inputfile, 1400, x)
                
                return

        #Read a elo list and get the players data. The argument listfile_rows comes from the get_list_data_from_file method 
        def update_players_data_from_list(self, listfile_rows, method, fide, feda, idfide, idfeda):
                for row in self.players_data:
                        for listfilerow in listfile_rows:
                                if method == 'idfide':
                                        if listfilerow['IDFIDE']==row['IDFIDE']:
                                                print('Updating data from: '+row['NAME']+'...')
                                                if listfilerow['IDFIDE'] != '' and idfide == 1:
                                                        row['IDFIDE']=listfilerow['IDFIDE']
                                                if listfilerow['ELOFIDE'] != '' and fide == 1:
                                                        row['ELOFIDE']=listfilerow['ELOFIDE']
                                                if listfilerow['ELONAT'] != '' and feda == 1:
                                                        row['ELONAT']=listfilerow['ELONAT']
                                                if listfilerow['IDNAT'] != '' and idfeda == 1:
                                                        row['IDNAT']=listfilerow['IDNAT']
                                if method == 'name':
                                        if listfilerow['NAME']==row['NAME']:
                                                print('Updating data from: '+row['NAME']+'...')
                                                if listfilerow['IDFIDE'] != '' and idfide == 1:
                                                        row['IDFIDE']=listfilerow['IDFIDE']
                                                if listfilerow['ELOFIDE'] != '' and fide == 1:
                                                        row['ELOFIDE']=listfilerow['ELOFIDE']
                                                if listfilerow['ELONAT'] != '' and feda == 1:
                                                        row['ELONAT']=listfilerow['ELONAT']
                                                if listfilerow['IDNAT'] != '' and idfeda == 1:
                                                        row['IDNAT']=listfilerow['IDNAT']
                


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
                                        lastname = cell[0].capitalize()#We leave only the first capital in the Surname
                                        firstname = cell[1].strip()#To remove the space in front of the name, because it was after the comma.
                                        firstname = firstname.capitalize()#Only the first capital is left.
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
                                
                                new_row={'NAME': name, 'G': '', 'IDFIDE': '', 'ELOFIDE': '', 'COUNTRY': '', 'TITLE': '', 'ELONAT': elonat, 'KFIDE': '', 'CLUB': '', 'BIRTHDAY': '', 'KNAT': '0', 'IDNAT': idnat}
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
                                                        new_row={'NAME': name, 'G': '', 'IDFIDE': '', 'ELOFIDE': '', 'COUNTRY': '', 'TITLE': '', 'ELONAT': elonat, 'KFIDE': '', 'CLUB': '', 'BIRTHDAY': '', 'KNAT': '0', 'IDNAT': idnat}
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
                                while line:
                                        line = csvfile.readline()
                                        firstblock = line[0:3]
                                        if firstblock == "012":
                                                info = line[4:]
                                                self.info['TOURNAMENT_NAME'] = info
                                                print(info)
                                        if firstblock == "022":
                                                info = line[4:]
                                                self.info['CITY'] = info
                                                print(info)
                                        if firstblock == "032":
                                                info = line[4:]
                                                self.info['FED'] = info
                                                print(info)
                                        if firstblock == "042":
                                                info = line[4:]
                                                self.info['BEGIN_DATE'] = info
                                                print(info)
                                        if firstblock == "052":
                                                info = line[4:]
                                                self.info['END_DATE'] = info
                                                print(info)
                                        if firstblock == "062":
                                                info = line[4:]
                                                self.info['NUMBER_OF_PLAYERS'] = info
                                                print(info)
                                        if firstblock == "102":
                                                info = line[4:]
                                                self.info['ARBITER'] = info
                                                print(info)
                                        if firstblock == "022":
                                                info = line[4:]
                                                self.info['CITY'] = info
                                                print(info)
                                        if firstblock == "001": #Players information
                                                sex = line[9]
                                                title = line[10:13]
                                                name = line[14:47]
                                                fide = line[48:52]
                                                fed = line[53:56]
                                                idfide = line[57:68]
                                                birthday = line[69:79]
                                                points = line[80:84]
                                                roundblock = ' '
                                                offset = 0
                                                numberofrounds = 0 #This variable is to count the number of rounds. This data is not in the TRF format
                                                playersopponent_temp = ''
                                                prueba = 0#Testing
                                                while 1:
                                                       offset += 10
                                                       opponent = line[91+offset:95+offset]
                                                       if not opponent:
                                                              break
                                                       playersopponent_temp = playersopponent_temp+" "+opponent
                                                       #self.playersopponent[0]=self.playersopponent[0]+" "+opponent#I have to put the right index here.
                                                       numberofrounds += 1
                                                       prueba += 1#Testing

                                                new_row={'NAME': name, 'G': sex, 'IDFIDE': idfide, 'ELOFIDE': fide, 'COUNTRY': fed, 'TITLE': title, 'BIRTHDAY': birthday, 'POINTS':points}
                                                self.playersopponent.append(playersopponent_temp)

                                                self.info['NUMBER_OF_ROUNDS'] = numberofrounds #This is not correct, but the info is not always available in this file format.
                                                self.info['CURRENT_ROUND'] = numberofrounds
                                                #print(new_row)
                                                self.players_data.append(new_row)
                                                players_index += 1        
                                
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
                                self.info['CURRENT_ROUND'] = roundinfo[2]
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
                                        if i > 0:
                                                self.playerscolor.append(line) #Store the data.
                                
                                csvfile.seek(0)
                                endofrange = endofrangenext+numberofplayers+1 #Next jump. Players opponents.
                                restofvegapointer = csvfile.readlines()[endofrangenext:endofrange]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)
                                        if i > 0:
                                                self.playersopponent.append(line) #We store the data in the property.

                                
                                csvfile.seek(0)
                                endofrangenext = endofrange+numberofplayers+1
                                restofvegapointer = csvfile.readlines()[endofrange:endofrangenext]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)
                                        if i > 0:
                                                self.playersfloater.append(line) 



                                csvfile.seek(0)
                                endofrange = endofrangenext+numberofplayers+1
                                restofvegapointer = csvfile.readlines()[endofrangenext:endofrange]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line)
                                        if i > 0:
                                                self.roundresults.append(line)

                                
                                csvfile.seek(0)
                                restofvegapointer = csvfile.readlines()[endofrange:]
                                for i in range(len(restofvegapointer)):
                                        line = restofvegapointer[i]
                                        self.restofvega.append(line) #I don't use this data. Just store it like it is to put it back in the file in the output.



                                        
                                for line in lines:
                                        new_row = {}
                                        line = line.split(';')

                                        for i in range(len(line)):
                                                line[i] = line[i].strip()
                                                new_row[self.header[i]] = line[i]
                                        self.players_data.append(new_row)
                                csvfile.seek(0)
                        if filename.endswith('.csv'):
                                reader = csv.DictReader(csvfile, delimiter=';')
                                self.header = reader.fieldnames
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
                        try:
                                for row in reader:
                                        new_row = row
                                        addfile_rows.append(new_row)
                        except csv.Error as e:
                                sys.exit('file %s, line %d: %s' % (inputfile, DictReader.line_num, e))
                        
                                
                for addrow in addfile_rows:
                        for row in self.players_data:
                                if addrow['NAME']==row['NAME']:
                                        foundit = 1
                                if foundit == 0:
                                        print("Add:" +addrow['NAME'])
                                        self.players_data.append(addrow)
                                foundit = 0
				
                print(self.players_data)
