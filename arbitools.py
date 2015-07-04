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
			
		self.info=[]
		self.standings=[]
		self.players_data = []

		#I think it is more clear if I put these variables in a class vegafile. I can define classes for the other files too.
		self.header=''
		self.vegaheader=[]
		self.headeroutputvega=''
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
		
		with open(outputfile, 'w') as csvoutputfile:
			writer = csv.DictWriter(csvoutputfile, fieldnames=self.header, delimiter=';')
			if inputfile.endswith('.csv'):
				writer.writeheader()
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
	def standings_to_file(self, outputfile):
		return

	#Apply recursive tiebreaks to standings
	def applyARPO(self):
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

	#Open a .csv, .txt or .veg and get the players data.
	def get_tournament_data_from_file(self, filename):
		
		with open(filename) as csvfile:
			if filename.endswith('.veg'):
				print(".veg file. Don't worry, I won't touch the original. It will be backed up.")
				for i in range(12):#Reserve the first lines of the .veg file. It is where the tournament info is.
					line = csvfile.readline()
					self.vegaheader.append(line)

				numberofplayers = self.vegaheader[11]# We get line 12 of the .veg file. It is where the number of players is.
				headerline=csvfile.readline()#This is the line with the names of the fields.
				csvfile.seek(0)#Reset the file pointer.
				lines = csvfile.readlines()[12:]#Read from 12th line, where the players data is.
				self.headeroutputvega = headerline
			#Now we store the players data in a dictionary
				self.header = lines[0].split(';')
				for i in range(14):
					self.header[i] = self.header[i].strip()#Remove the spaces we don't need.
				csvfile.seek(0)
				endofrange = 13+int(numberofplayers)#Calculate where the players data end.
				lines = csvfile.readlines()[13:endofrange]#Read the lines where the players data is.

				csvfile.seek(0)
				restofvegapointer=csvfile.readlines()[endofrange:]#Jump to the end of the players data.	
				for i in range(len(restofvegapointer)):
				#Now we put each line of restofvegapointer in restofvega. I do this way because the function for writing files would use the variable restofvegapointer.
					line = restofvegapointer[i]
					self.restofvega.append(line)
				print(self.restofvega)

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
	def add_players_data_from_file(self):
		return
