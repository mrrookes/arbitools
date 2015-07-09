# arbitools
Chess Arbiter Tools
********************************************************************************************
arbitools    ------ Version 0.7
*********************************************************************************************
Copyright David Gonzalez Gandara 2015
This is free software. Read the LICENSE file for details.

Arbitools is a collection of programs that allow chess arbiters to manage a chess tournament. This is something that traditionally was possible only with non-free software. Arbitools tries to set the GNU way to do it.

Important features of the GNU way: 
- The possibility to work from commandline.
- Integration with other software (.tex output for LaTeX, databases that can be easily imported, etc.).
- The easiness of making changes and improvements.
- For developers, arbitools.py offers the Tournament class, which defines easy to use properties and methods for other projects.

It is written in Python 3. It should work in other platforms apart from GNU/Linux.

FEATURES:
Up to here, the following tasks are possible:

- Updating the players data in the database file. You can add missing data like the ELOs, FIDE and nat ID, etc. Supported formats for the database are: .csv, .txt (fide official), .veg
- Adding a list of extra players to an existing database file.
- Produce output for standings: a .txt file and a .tex file, ready for pdflatex

TODO:
- Pairing engine. Arbitools doesn't do the pairings in this moment. The Dutch algorithm is tricky to implement and difficult to get officially endorsed by FIDE. I recommend the use of JavaPairing (javapairing.sourceforge.net). The program is able to do a pairing from arbitools output.
- Detect duplicated players in the elo list and warn the user about it.
- Generate PGN files.
- Appliying tiebreaks.
- Producing FIDE reports.



DEPENDENCIES
- python3
- lxml -> only if you need xml files from FIDE.
- xlrd -> only if you need xls files from FEDA.

You can get python and modules free from www.python.org. There are different ways to install modules, for example, you can use the script pip. Go to the python installation folder, then go the the Scripts folder and run: "pip install <name of the module>".

Make sure you keep up to date the following files:
-"FIDE-FEDA Vega.csv", maintained by Jesús Mena. You can download it free from wwwjemchess.com
-"player_list_xml.xml", from www.fide.com
-"elo_feda.xls", from www.feda.org. The file in the website is named differently. You need to rename it for the program to work.

USAGE:
**********************************


-----------------------------------------------
Command line.
-----------------------------------------------
NAME
	arbitools-update.py - Chess Arbiters Tools
SYNOPSIS
	arbitools-update.py [-l elo list] [-i inputfile] [-m search method]
OPTIONS
-h
	Displays help.
-v --version
	Displays version.
-l --list
	"feda" Reads data from elo_feda.xls. You need to give this name to the file downloaded from www.feda.org.
	"fide" Reads data from players_list_xml.xml. You can get it from www.fide.com.
	"fidefeda" Reads data from "FIDE-FEDA Vega.csv. You can download it from www.jemchess.com.
 -m --method
	"idfde" Search by FIDE code.
	"name" Search by name.
 -i --ifile
	Supported formats for the inputfile are: .txt (Krause file format), .veg, .csv (FIDE-FEDA style)
	
---------------------------------------------------
NAME
	arbitools-add.py
SYNOPSIS
	arbitools-add.py [-i inputfile] [-u file where the new data are]
DESCRIPTION
	Retrieves data from -u and paste them in -i.


----------------------------------------------------
NAME
	arbitools-standings.py
SYNOPSIS
	arbitools-standings.py [-i inputfile]
DESCRIPTION
	Creates to files, a .txt and a .tex with the standings

---------------------------------------------
GRAPHICAL INTERFACE
---------------------------------------------

SYNOPSIS
	arbitools-gui.py
	
USAGE

Update players data:
	Select the file you want to work with.
	
	Choose one of the options.

	Choose the fields you want to change.

	Choose search method.
