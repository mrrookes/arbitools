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

#Frontend for arbitools

from arbitools import arbitools
import sys
import os
import csv
import pkg_resources
try:
    from lxml import etree
    lxml_present=True
except ImportError:
    lxml_present=False
try:
    import xlrd
    xlrd_present=True
except ImportError:
    xlrd_present=False
from tkinter import ttk
from subprocess import PIPE, Popen
from tkinter.filedialog import askopenfilename
import tkinter.messagebox
import unicodedata

class App:
    def __init__(self, master):

       #Defyning graphical layout.
        frame_update = ttk.LabelFrame(master, text="Update data")
        frame_update.grid(row=0, column=0, padx="5", pady="5")
        frame_add = ttk.LabelFrame(master, text="Add players to file")
        frame_add.grid(row=1, column=0, padx="5", pady="5")
        frame_options = ttk.LabelFrame(master, text="Search options")
        frame_options.grid(row=2, column=0, padx="5", pady="5")

        frame_textbox = ttk.LabelFrame(master, text="Output")
        frame_textbox.grid(row=3, column=0, padx="5", pady="5")

        frame_info = ttk.LabelFrame(master, text="Tournament Info")
        frame_info.grid(row=0, rowspan=3, column=1, padx="5", pady="5")

        frame_standings = ttk.LabelFrame(master, text="Reports")
        frame_standings.grid(row=3, column=1, padx="5", pady="5")

        #Create variables
        filename=""
        buscaconcodigo=0
        self.tournament = arbitools.Tournament()
        
        
        # create and position widgets
        current_path=os.path.expanduser("~")
        if not os.path.isfile(os.path.join(current_path,"custom_elo.csv")):
                tkinter.messagebox.showinfo("Error", "I can't find custom_elo.csv in your personal folder. You won't be able to get fidefeda data.")
        if not os.path.isfile(os.path.join(current_path, "FIDE-FEDA Vega.csv")):
                tkinter.messagebox.showinfo("Error", "I can't find FIDE-FEDA Vega.csv in your personal folder. You won't be able to get fidefeda data.")
        if not os.path.isfile(os.path.join(current_path, "/players_list_xml.xml")):
                tkinter.messagebox.showinfo("Error", "I can't find players_list_xml.xml in your personal folder. You won't be able to use fide xml data.")
        if not os.path.isfile(os.path.join(current_path, "/elo_feda.xls")):
                tkinter.messagebox.showinfo("Error", "I can't find elo_feda.xls in your personal folder. You won't be able to use feda data.")
        if not os.path.isfile(pkg_resources.resource_filename(__name__, "arbitools-update.py")):
                tkinter.messagebox.showinfo("Error", "I can't find arbitools-update.py. This program may not work properly. Copy the file to this folder.")
        if not os.path.isfile(pkg_resources.resource_filename(__name__, "/arbitools-add.py")):
                tkinter.messagebox.showinfo("Error", "I can't find arbitools-add.py. This program may not work properly. Copy the file to this folder.")

        #widgets for the infile information
        self.infilelabel = ttk.Label(frame_update, text="Input file:")
        self.infilelabel.grid(row=0)

        self.infiletextbox = tkinter.Text(frame_update, height=1, width=40)
        self.infiletextbox.grid(row=0, column=1, padx="2")
        self.infiletextbox.insert(tkinter.END, "")
        
        
        self.infilebutton = ttk.Button(frame_update, text="Browse", width=15, command=self.infile)
        self.infilebutton.grid(row=0, column=2, padx="2", pady="2")        
        
        
        
        self.optionslabel = ttk.Label(frame_update, text="Select elo file:")
        self.optionslabel.grid(row=1, column=0, padx="2")
 
        self.optionscombobox=ttk.Combobox(frame_update)
        self.optionscombobox['values']=('custom_elo.csv', 'FIDE-FEDA Vega.csv', 'players_list_xml.xml', 'elo_feda.xls')
        self.optionscombobox.state(['readonly'])
        #self.optionscombobox.bind('<<Combobox Selected>>, 
        self.optionscombobox.grid(row=1, column=1)
        
        
        self.updatedatabutton = ttk.Button(frame_update, text="Update data", width=15, command=self.update_data)
        self.updatedatabutton.grid(row=1, column=2, padx="2", pady="2")
        
        #widgets for the addfile information (to use with arbitools-add)
        self.addfilelabel = ttk.Label(frame_add, text="File with new data:")
        self.addfilelabel.grid(row=0, column=0, padx="2")

        self.addfilebutton = ttk.Button(frame_add, text="Browse", width=15, command=self.addfile)
        self.addfilebutton.grid(row=0, column=2)       
        

        self.addfiletextbox = tkinter.Text(frame_add, height=1, width=40)
        self.addfiletextbox.grid(row=0, column=1)
        self.addfiletextbox.insert(tkinter.END, "")
        
        self.adddatabutton = ttk.Button(frame_add, text="Add data from file", width=15, command=self.add_data)
        self.adddatabutton.grid(row=1, column=2, padx="2", pady="2")
        
       #Widgets with the options elements.
        self.methodlabel = ttk.Label(frame_options, text="Select search method:")
        self.methodlabel.pack()
 
        #self.method=tkinter.IntVar()
        self.methodcombobox=ttk.Combobox(frame_options)
        self.methodcombobox['values']=('idfide', 'name')
        self.methodcombobox.state(['readonly'])
        #self.methodcombobox.bind('<<Combobox Selected>>', self.method)
        
        self.methodcombobox.pack()

        
        
        self.whattoupdatelabel = ttk.Label(frame_options, text="Data to update:")
        self.whattoupdatelabel.pack()

        self.varname=tkinter.IntVar()
        self.checkboxname=tkinter.Checkbutton(frame_options, text="Name", variable=self.varname)
        self.checkboxname.pack(side=tkinter.LEFT)
        
        self.varfide=tkinter.IntVar()
        self.checkboxfide=tkinter.Checkbutton(frame_options, text="FIDE", variable=self.varfide)
        self.checkboxfide.pack(side=tkinter.LEFT)

        self.varfeda=tkinter.IntVar()
        self.checkboxfeda=tkinter.Checkbutton(frame_options, text="FEDA", variable=self.varfeda)
        self.checkboxfeda.pack(side=tkinter.LEFT)

        self.varidfide=tkinter.IntVar()
        self.checkboxidfide=tkinter.Checkbutton(frame_options, text="ID FIDE", variable=self.varidfide)
        self.checkboxidfide.pack(side=tkinter.LEFT)
        
        self.varidfeda=tkinter.IntVar()
        self.checkboxidfeda=tkinter.Checkbutton(frame_options, text="ID FEDA", variable=self.varidfeda)
        self.checkboxidfeda.pack(side=tkinter.LEFT)

       #Results box widget.
        self.resultsBox = tkinter.Text(frame_textbox, height=5, width=60)
        self.resultsBox.pack(padx="5", pady="5")

       #Info box widget.
        self.infoBox = tkinter.Text(frame_info, height=15, width=50)
        self.infoBox.pack()

       #Reports buttons.
        self.standingsbutton = ttk.Button(frame_standings, text="Get Standings", width=15, command=self.get_standings)
        self.standingsbutton.pack(pady="5")

        self.exportbutton = ttk.Button(frame_standings, text="Export to FIDE", width=15, command=self.export)
        self.exportbutton.pack(pady="5")


    def infile(self):

       #Store the information in the boxes in case the user presses cancel.        
        textbox = self.infiletextbox.get(1.0, tkinter.END)
        infobox = self.infoBox.get(1.0, tkinter.END)
        self.infiletextbox.delete(1.0, tkinter.END)
        self.resultsBox.delete(1.0, tkinter.END)
        self.infoBox.delete(1.0, tkinter.END)
        
        inputfile = askopenfilename()
        self.infiletextbox.insert(tkinter.END, inputfile)

       #If cancel, restore the boxes.
        if not inputfile:
                self.infiletextbox.insert(tkinter.END, textbox)
                self.infoBox.insert(tkinter.END, infobox)

        if inputfile.endswith('.txt'):
                self.resultsBox.insert(tkinter.END, "Looks like a FIDE file...")
        elif inputfile.endswith('.veg'):
                self.resultsBox.insert(tkinter.END, "Looks like a Vega file...")
        else:
                self.resultsBox.insert(tkinter.END, "Doesn't look like a tournament file...")
        self.tournament.get_tournament_data_from_file(inputfile)
        if self.tournament.info['TOURNAMENT_NAME'] != ' ':
                string = self.tournament.info['TOURNAMENT_NAME']
                self.infoBox.insert(tkinter.END, string)
        if self.tournament.info['TYPE_OF_TOURNAMENT'] != ' ':
                string = self.tournament.info['TYPE_OF_TOURNAMENT']
                self.infoBox.insert(tkinter.END, string)

        if self.tournament.info['CITY'] != ' ':
                string = self.tournament.info['CITY']
                self.infoBox.insert(tkinter.END, string)
        if self.tournament.info['NUMBER_OF_PLAYERS'] != ' ':
                string = "Number of players: "+self.tournament.info['NUMBER_OF_PLAYERS']
                self.infoBox.insert(tkinter.END, string)
        if self.tournament.info['ARBITER'] != ' ':
                string = "Arbiter: "+self.tournament.info['ARBITER']
                self.infoBox.insert(tkinter.END, string)
        if self.tournament.info['BEGIN_DATE'] != ' ':
                string = "Starts: "+self.tournament.info['BEGIN_DATE']
                self.infoBox.insert(tkinter.END, string)
        if self.tournament.info['END_DATE'] != ' ':
                string = "Ends: "+self.tournament.info['END_DATE']
                self.infoBox.insert(tkinter.END, string)
        if self.tournament.info['ALLOTED_TIME'] != ' ':
                string = "Alloted time: "+self.tournament.info['ALLOTED_TIME']
                self.infoBox.insert(tkinter.END, string)



    def addfile(self):
        text = self.addfiletextbox.get(1.0, tkinter.END)
        self.addfiletextbox.delete(1.0, tkinter.END)
        filename = self.addfiletextbox.insert(tkinter.END, askopenfilename())
        if not filename:
                self.addfiletextbox.insert(tkinter.END, text)
   
    def export(self):
        texttext = self.infiletextbox.get(1.0, tkinter.END)
        texttext=texttext.encode("utf-8")  #encode unicode to str
        texttext=texttext.rstrip() #remove what we don't need
        
        self.resultsBox.insert(tkinter.END, "Exporting to FIDE...\n")
        
        inputfile = self.infiletextbox.get(1.0, tkinter.END).strip()

        self.tournament.get_tournament_data_from_file(inputfile)
        self.tournament.export_to_fide(inputfile)

        self.resultsBox.insert(tkinter.END, "Data exported. Search for '_export.txt' file...\n")        


    def get_standings(self):
        
        texttext = self.infiletextbox.get(1.0, tkinter.END)
        texttext=texttext.encode("utf-8")  #encode unicode to str
        texttext=texttext.rstrip() #remove what we don't need
        
        self.resultsBox.insert(tkinter.END, "Getting standings...\n")
        
        inputfile = self.infiletextbox.get(1.0, tkinter.END).strip()

        self.tournament.get_tournament_data_from_file(inputfile)
        try:

                self.tournament.applyARPO(inputfile)
                self.resultsBox.insert(tkinter.END, "ARPO calcuations written to file with suffix '_ARPO'...\n")
        except Exception:
                self.resultsBox.insert(tkinter.END, "Sorry, I can't get ARPO calculations from this file...\n")
        self.tournament.standings_to_file(inputfile)

        self.resultsBox.insert(tkinter.END, "Standings files created with suffix '_standings'...\n")        
       
        

    def update_data(self):
          
        current_path=os.path.expanduser("~")
        elolist=''
        listfile=''
        
        # reset result box
        self.resultsBox.delete(1.0, tkinter.END)
        # get text

        texttext = self.infiletextbox.get(1.0, tkinter.END)
        texttext=texttext.encode("utf-8")  #encode unicode to str
        texttext=texttext.rstrip() #remove what we don't need
        
        self.resultsBox.insert(tkinter.END, "Updating data...\n")       
        
        if self.optionscombobox.get() == "custom_elo.csv":
                elolist='custom'
                tkinter.messagebox.showinfo("Custom list", "Using user custom list.")
                listfile=os.path.join(current_path, 'custom_elo.csv')
        if self.optionscombobox.get() == "player_list_xml.xml":
                elolist='fide'
                tkinter.messagebox.showinfo("WARNING!", "This process is extremely slow (more than fifteen minutes. Do it only if you really need it.")
                listfile=os.path.join(current_path,'players_list_xml.xml')
        if self.optionscombobox.get() == "FIDE-FEDA Vega.csv":
                elolist='fidefeda'
                tkinter.messagebox.showinfo("FIDE-FEDA", "Possible thanks to Jesus Mena. Download FIDE-FEDA monthly from www.jemchess.com")
                listfile=os.path.join(current_path, 'FIDE-FEDA Vega.csv')
        if self.optionscombobox.get() == "elo_feda.xls":
                elolist='feda'
                tkinter.messagebox.showinfo("ELO Feda", "There are multiple spelling issues in this file. Check everything after doing this.")
                listfile=os.path.join(current_path, 'elo_feda.xls')
        method=''        

        if self.methodcombobox.get() == "idfide":
                method='idfide'
                tkinter.messagebox.showinfo("WARNING!", "Don't use this option with the FEDA elo file. It does not include FIDE IDs!")
        if self.methodcombobox.get() == "name":
                method='name'

        inputfile = self.infiletextbox.get(1.0, tkinter.END).strip()

        #tkinter.messagebox.showinfo("var", elolist)#testing
        listdata = self.tournament.get_list_data_from_file(elolist, listfile)
        self.tournament.get_tournament_data_from_file(inputfile)
        #self.tournament.update_players_data_from_list(listdata, self.method.get(), self.varfide.get(), self.varfeda.get(), self.varidfide.get(), int(self.varidfeda.get()))
        self.tournament.update_players_data_from_list(listdata, self.varfide.get(), self.varfeda.get(), self.varidfide.get(), self.varidfeda.get(), self.varname.get())
        self.tournament.output_to_file(inputfile)

        self.resultsBox.insert(tkinter.END, "File updated...\n")        
        #self.update_data(texttext, elolist, method, self.varname.get(), self.varfide.get(), self.varfeda.get(), self.varidfide.get(), self.varidfeda.get())
        
    def add_data(self):
                
        # reset result box
        self.resultsBox.delete(1.0, tkinter.END)
        # get text
        current_path=os.path.dirname(os.path.realpath(sys.argv[0]))
        texttext = self.addfiletextbox.get(1.0, tkinter.END)
        texttext=texttext.encode("utf-8")  
        texttext=texttext.rstrip() 
        texttext2 = self.addfiletextbox.get(1.0, tkinter.END)
        texttext2=texttext2.encode("utf-8")  
        texttext2=texttext2.rstrip() 

        self.resultsBox.insert(tkinter.END, "Adding data...\n")
        #comando =current_path+"/pegar_csv.py -i "+texttext+" -u "+texttext2

        #exelist=comando.split(' ')
        
        #exe=Popen(exelist, shell=False, stdout=PIPE, stderr=PIPE)
        #out,err = exe.communicate()
        #self.resultsBox.insert(tkinter.END, out)
    
        
def main(argv):
    
        root = tkinter.Tk()
        root.title("Chess Arbiter Tools")
        app = App(root)
        root.mainloop()

if __name__ == "__main__":
   main(sys.argv[1:])


