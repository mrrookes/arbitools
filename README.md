# arbitools
Chess Arbiter Tools
********************************************************************************************
arbitools    ------ Version 0.9
*********************************************************************************************
Copyright David Gonzalez Gandara 2015
This is free software. Read the LICENSE file for details.

Arbitools is a collection of programs that allow chess arbiters to manage a chess tournament. This is something that traditionally was possible only with non-free software. Arbitools tries to set the GNU way to do it.

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

For more details, refer to the manual.