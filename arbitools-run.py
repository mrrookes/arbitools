import click
import os
from arbitools import arbitools

@click.group()
def arbitoolsrun():
    pass

@click.command()
@click.argument('inputfile')
@click.option('--elolist', '-l', default = 'custom', help= 'Elo list file')


def update(inputfile, elolist):

    if elolist == 'feda':
        listfile = os.path.join(os.path.expanduser("~"), "elo_feda.xls")
    elif elolist == 'fidefeda':
        listfile = os.path.join(os.path.expanduser("~"), "FIDE-FEDA Vega.csv")
    elif elolist == 'fide':
        listfile = os.path.join(os.path.expanduser("~"), "players_list_xml.xml")
    elif elolist == 'custom':
        listfile = os.path.join(os.path.expanduser("~"), "custom_elo.csv")
    tournament = arbitools.Tournament()
    tournament.get_tournament_data_from_file(inputfile)
    listdata = tournament.get_list_data_from_file(elolist, listfile)
    if inputfile.endswith(".fegaxa"):
        tournament.update_players_data_from_list_fegaxa(listada)
    else:
        tournament.update_players_data_from_list(listdata, 1, 1, 1, 1, 1)
    tournament.output_to_file(inputfile)

@click.command()
@click.argument('inputfile')


def fedarating(inputfile):
                                                                                                        
    tournament = arbitools.Tournament()
    
    tournament.get_tournament_data_from_file(inputfile)

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
    listdata = tournament.get_list_data_from_file(elolist, listfile)
    tournament.update_players_data_from_list(listdata, 1, 1, 1, 1, 1)
    tournament.export_to_feda(inputfile)

@click.command()
@click.argument('inputfile')

def it3(inputfile):

    tournament = arbitools.Tournament()
    
    tournament.get_tournament_data_from_file(inputfile)
    tournament.write_it3_report(inputfile)

arbitoolsrun.add_command(fedarating)
arbitoolsrun.add_command(it3)
arbitoolsrun.add_command(update)

if __name__ == '__main__':
    arbitoolsrun()
