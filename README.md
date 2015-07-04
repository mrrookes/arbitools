# arbitools
Chess Arbiter Tools
********************************************************************************************
*arbitools    ------ Version 0.5
*******

Arbitools is a collection of programs that allow chess arbiters to manage a chess tournament. this is something that traditionally was possible only with non-free software. Arbitools tries to be the GNU way to do it. Important features of the GNU way: the possibility to work from commandline; possibility of integration with other software (to write pdfs, easily export databases, etc.). And most importantly, the easiness of making changes and improvements.
arbitools.py offers the Tournament class, very easy to use for other projects.
Up to here, the following tasks are possible:

- Updating the players data in the database file. Supported formats for the database are: .csv, .txt, .veg
- Adding a list of players in a file to a database file.

TODO:
- Pairing engine. This is the hardest part of all. For the moment, I recommend the use of JavaPairing (javapairing.sourceforge.net). Although this program is free software, it doesn't opperate the GNU way.
- Producing output for standings.
- Appliying tiebreaks.
- Producint FIDE reports.



Copyright 2015 David González Gándara

DEPENDENCIES
- python3
- lxml -> only if you need xml files from FIDE.
- xlrd -> only if you need xls files from FEDA.
- tk -> only if you want to use the gui.

You can get python and modules free from www.python.org.

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

---------------------------------------------
GUI.
---------------------------------------------

SYNOPSIS
	arbitools-gui.py
	
USAGE

Update players data:
	Select the file you want to work with.
	
	Choose one of the options.

	Choose the fields you want to change.

	Choose search method.
