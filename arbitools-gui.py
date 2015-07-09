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

import arbitools
import sys
import os
import csv
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
        frame = ttk.Frame(master)
        frame.pack()
        
        filename=""
        buscaconcodigo=0
        self.tournament = arbitools.Tournament()
        
        
        # create and position widgets
        current_path=os.path.dirname(os.path.realpath(sys.argv[0]))
        if not os.path.isfile(current_path+"/FIDE-FEDA Vega.csv"):
                tkinter.messagebox.showinfo("Error", "I can't find FIDE-FEDA Vega.csv. You won't be able to get fidefeda data.")
        if not os.path.isfile(current_path+"/players_list_xml.xml"):
                tkinter.messagebox.showinfo("Error", "I can't find players_list_xml.xml. You won't be able to use fide xml data.")
        if not os.path.isfile(current_path+"/elo_feda.xls"):
                tkinter.messagebox.showinfo("Error", "I can't find elo_feda.xls. You won't be able to use feda data.")
        if not os.path.isfile(current_path+"/arbitools-update.py"):
                tkinter.messagebox.showinfo("Error", "I can't find arbitools-update.py. This program may not work properly. Copy the file to this folder.")
        if not os.path.isfile(current_path+"/arbitools-add.py"):
                tkinter.messagebox.showinfo("Error", "I can't find arbitools-add.py. This program may not work properly. Copy the file to this folder.")

        #widgets for the infile information
        self.infilelabel = ttk.Label(frame, text="Input file:")
        self.infilelabel.pack()

        self.infilebutton = ttk.Button(frame, text="Browse", width=15, command=self.infile)
        self.infilebutton.pack()        
        
        
        self.infiletextbox = tkinter.Text(frame, height=1, width=40)
        self.infiletextbox.pack()
        self.infiletextbox.insert(tkinter.END, "")
        
        #widgets for the addfile information (to use with arbitools-add)
        self.addfilelabel = ttk.Label(frame, text="File with new data:")
        self.addfilelabel.pack()

        self.addfilebutton = ttk.Button(frame, text="Browse", width=15, command=self.addfile)
        self.addfilebutton.pack()       
        

        self.addfiletextbox = tkinter.Text(frame, height=1, width=50)
        self.addfiletextbox.pack()
        self.addfiletextbox.insert(tkinter.END, "")

        self.resultsBox = tkinter.Text(frame, height=15, width=75)
        self.resultsBox.pack()

        #self.scrollbar = Scrollbar(self.resultsBox, command=self.textbox.yview)
        #self.resultsBox.configure(yscrollcommand=self.scrollbar.set)
        #self.scrollbar.grid(column=3, sticky=N+S)
        
        self.updatedatabutton = ttk.Button(frame, text="Update data", width=15, command=self.update_data)
        self.updatedatabutton.pack()

        self.optionscombobox=ttk.Combobox(frame)
        self.optionscombobox['values']=('FIDE-FEDA Vega.csv', 'players_list_xml.xml', 'elo_feda.xls')
        self.optionscombobox.state(['readonly'])
        #self.optionscombobox.bind('<<Combobox Selected>>, 
        self.optionscombobox.pack()
        
        self.method=tkinter.IntVar()
        self.methodcombobox=ttk.Combobox(frame)
        self.methodcombobox['values']=('idfide', 'name')
        self.methodcombobox.state(['readonly'])
        self.methodcombobox.bind('<<Combobox Selected>>', self.method)
        
        self.methodcombobox.pack()

        
        self.adddatabutton = ttk.Button(frame, text="Add data from file", width=15, command=self.add_data)
        self.adddatabutton.pack()

        self.whattoupdatelabel = ttk.Label(frame, text="Data to update:")
        self.whattoupdatelabel.pack()

        self.varname=tkinter.IntVar()
        self.checkboxname=tkinter.Checkbutton(frame, text="Name", variable=self.varname)
        self.checkboxname.pack()
        
        self.varfide=tkinter.IntVar()
        self.checkboxfide=tkinter.Checkbutton(frame, text="FIDE", variable=self.varfide)
        self.checkboxfide.pack()

        self.varfeda=tkinter.IntVar()
        self.checkboxfeda=tkinter.Checkbutton(frame, text="FEDA", variable=self.varfeda)
        self.checkboxfeda.pack()

        self.varidfide=tkinter.IntVar()
        self.checkboxidfide=tkinter.Checkbutton(frame, text="ID FIDE", variable=self.varidfide)
        self.checkboxidfide.pack()
        
        self.varidfeda=tkinter.IntVar()
        self.checkboxidfeda=tkinter.Checkbutton(frame, text="ID FEDA", variable=self.varidfeda)
        self.checkboxidfeda.pack()

    def infile(self):
        self.infiletextbox.insert(tkinter.END, askopenfilename())

    def addfile(self):
        self.addfiletextbox.insert(tkinter.END, askopenfilename())

    def update_data(self):
          
        current_path=os.path.dirname(os.path.realpath(sys.argv[0]))
        elolist=''
        listfile=''
        
        # reset result box
        self.resultsBox.delete(1.0, tkinter.END)
        # get text

        texttext = self.infiletextbox.get(1.0, tkinter.END)
        texttext=texttext.encode("utf-8")  #encode unicode to str
        texttext=texttext.rstrip() #remove what we don't need
        
        self.resultsBox.insert(tkinter.END, "Updating data...\n")       
        
        if self.optionscombobox.get() == "player_list_xml.xml":
                elolist='fide'
                tkinter.messagebox.showinfo("WARNING!", "This process is extremely slow (more than fifteen minutes. Do it only if you really need it.")
                listfile='players_list_xml.xml'
        if self.optionscombobox.get() == "FIDE-FEDA Vega.csv":
                elolist='fidefeda'
                tkinter.messagebox.showinfo("FIDE-FEDA", "Possible thanks to Jesus Mena. Download FIDE-FEDA monthly from www.jemchess.com")
                listfile='FIDE-FEDA Vega.csv'
        if self.optionscombobox.get() == "elo_feda.xls":
                elolist='feda'
                tkinter.messagebox.showinfo("ELO Feda", "There are mistakes in this file. Check everything after doing this.")
                listfile='elo_feda.xls'
        
        inputfile = self.infiletextbox.get(1.0, tkinter.END).strip()

        tkinter.messagebox.showinfo("var", elolist)
        listdata = self.tournament.get_list_data_from_file(elolist, listfile, self.method.get())
        self.tournament.get_tournament_data_from_file(inputfile)
        self.tournament.update_players_data_from_list(listdata, self.method.get(), self.varfide.get(), self.varfeda.get(), self.varidfide.get(), self.varidfeda.get())
        self.tournament.output_to_file(inputfile)


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
        root.title("Tunear csv")
        app = App(root)
        root.mainloop()

if __name__ == "__main__":
   main(sys.argv[1:])


