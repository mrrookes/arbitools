'''
_PyRP implements the common methods for PyRP and NumPyRP.
'''

import sys
from itertools import dropwhile
from functools import partial
from collections import namedtuple
from math import sqrt


# A named tuple that saves the information of the first line of a Swiss
# Manager file
_FirstLine = namedtuple(
    '_FirstLine',
    ['file_iter', 'index_name', 'index_elo', 'index_points', 'index_rounds'])
# A named tuple for players that did not play many rounds
_FewRounds = namedtuple('_FewRounds', ['did_not_play', 'less_than_half'])

class _Tournament:
    # Character used for drawn matches
    _DRAW = 'x'
    # Minimum Elo
    _MINIMUM_ELO = 1400
    # Default value for epsilon test
    _EPSILON = 1.e-10
    # Default value for the maximum number of iterations
    _MAX_ITERATIONS = 500
    # Approximately -400*log10(1/percentage-1)
    _performance_table = [
        -800, -677, -589, -538, -501, -470, -444, -422, -401, -383,
        -366, -351, -336, -322, -309, -296, -284, -273, -262, -251,
        -240, -230, -220, -211, -202, -193, -184, -175, -166, -158,
        -149, -141, -133, -125, -117, -110, -102, -95, -87, -80, -72,
        -65, -57, -50, -43, -36, -29, -21, -14, -7, 0, 7, 14, 21, 29,
        36, 43, 50, 57, 65, 72, 80, 87, 95, 102, 110, 117, 125, 133,
        141, 149, 158, 166, 175, 184, 193, 202, 211, 220, 230, 240,
        251, 262, 273, 284, 296, 309, 322, 336, 351, 366, 383, 401,
        422, 444, 470, 501, 538, 589, 677, 800]


    def __init__(self, *args, **kwargs):
        raise TournamentError(
            'Direct creation of instances is not allowed. Use load_tournament.')

    @classmethod
    def load(cls, file_name, elo_default=_MINIMUM_ELO, draw_character=_DRAW):
        '''
        load_tournament(file_name) returns a Tournament object loaded from
        a Swiss Manager file called file_name.
        '''
        # Initialize all private variables
        t = cls.__new__(cls)
        t._log_info = {}
        t._recursive_performances = None
        t._recursive_bucholzs = None
        # Load information from the file
        try:
            t._import_swiss_manager(file_name, elo_default, draw_character)
        except Exception as error:
            raise error from TournamentError(
                '{} could not be processed.'.format(file_name))
        else:
            # Get some log information
            t._log_info['Did not play'], t._log_info['Less than half'] =\
                t._read_log()
            return t

    def _read_first_line(self, file, convert=False):
        # Determine if we use str ot bytes
        if convert:
            type1 = partial(bytes, encoding='utf-8')
            type2 = partial(str, encoding='utf-8')
        else:
            type1, type2 = str, str
            
        file_iter = dropwhile(lambda line: type1('1.Rd.') not in line, file)
        try:
            # The first line is the heading line
            line = next(file_iter)
        except StopIteration:
            raise TournamentError(
                '{} is not a correct Swiss Manager file.'.format(file_name))
        
        # Determine the position of the information needed         
        fields = type2(line).strip().split(';')
        index_name = fields.index('Name')
        index_elo = fields.index('Rtg')
        index_points = fields.index('Pts')
        index_rounds = [
            i for i, field in enumerate(fields) if field.endswith('.Rd.')]
        return _FirstLine(
            file_iter, index_name, index_elo, index_points, index_rounds)

    @staticmethod
    def _calculate_elo(elo, elo_default):
        # Calculate the Elo from Swiss Manager
        return float(elo_default if not elo or int(elo)==0 else elo)
        
    @staticmethod
    def _calculate_points(value, draw_character):
        return float(value.replace(draw_character, '.5'))

    @staticmethod
    def _calculate_played_points(line, index_rounds, draw_character):
        # Calculate played points of a player from Swiss Manager
        return sum(
            _Tournament._player_played_points(line, index, draw_character)
            for index in index_rounds)

    @staticmethod
    def _player_played_points(line, index, draw_character):
        return (
            float(line[index+2].replace(draw_character, '.5'))
            if line[index+1]=='w' or line[index+1]=='b' else 0.0)

    @staticmethod
    def _calculate_opponents(line, index_rounds):
        return [
            int(line[index])-1 for index in index_rounds if line[index+1]!='-']

    def run(
        self, methods_list, output_file=sys.stdout, sort_by=None,
        reverse_order=True, heading=True, decimal_separator='.',
        comma_separator=';'):
        '''
        tournament.run(
            [{'method' : 'method name 1'},...], output_file, 
            sort_by = [{'method' : 'method name i'},...], reverse_order = True)
        prints to output_file the results of the various methods given as a
        dictionary.
        If sort_by is given the output is sorted according to the methods given.
        Possible methods are:
        'Name': names of the players.
        'Elo': Elo of each player as obtained from the input.
        'Points': number of points of a player as obtained from the input.
        'Played points': points obtained by each player in actual matches.
        'Bucholz': Bucholz of each player.
        'Average Bucholz': Bucholz divided by the number of opponents.
        'Performance': performance of the players using FIDE's table.
        'Recursive Performance' or 'RP': gives an approximation of the
            recursive performance of a player.
        'Average Recursive Performance of Opponents' or 'ARPO': calculates the
            average recursive performance of the opponents of each player.
        'Recursive Bucholz' or 'RB': gives an approximation of the
            recursive Bucholz of a player.
        'Average Recursive Bucholz of Opponents' or 'ARBO': calculates the
            average recursive Bucholz of the opponents of each player.

        The modifications 'Worst' and 'Best' can be given to 'ARPO' and 'ARBO'
        to remove a number of worst or best opponents of a player.
        '''
        try:
            if output_file==sys.stdout:
                # standard output
                self._put_results(
                    output_file, methods_list, sort_by, reverse_order,
                    heading, decimal_separator, comma_separator)
            else:
                # Open a file for writing
                with open(output_file, mode='w') as file:
                    self._put_results(
                        file, methods_list, sort_by, reverse_order, heading,
                        decimal_separator, comma_separator)
        except OSError as error:
            raise error from TournamentError(
                'Error writing file {}'
                'Make sure that the file is not being used '
                'by another application'.format(str(output_file)))

    def _put_results(
        self, file, methods_list, sort_by, reverse_order, heading,
        decimal_separator, comma_separator):
        # Writes the results on a file
        info = self.results_list(methods_list, sort_by, reverse_order)
        # Print heading if applicable
        if heading:
            print(
                *(_Tournament._str_heading(
                    **method) for method in methods_list),
                sep=comma_separator, file=file)
        # Creates a line of text (with no format) for writing on a file (csv)
        for line in info:
            print(
                *(_Tournament._to_string(
                    field, decimal_separator) for field in line),
                sep=comma_separator, file=file)

    @staticmethod
    def _to_string(expr, decimal_separator='.'):
        # Convert data applying locale characteristics
        if type(expr) == float:
            return str(expr).replace('.', decimal_separator)
        else:
            return str(expr)

    @classmethod
    def _str_heading(cls, *, method='Name', worst=0, best=0, **kwargs):
        # Print headings using the methods dictionary
        if method in (
            'ARPO', 'ARBO', 'Average Recursive Performance of Opponents', 
            'Average Recursive Bucholz of Opponents'):
            return '{}({}-{})'.format(method, worst, best)
        else:
            return method

    def results_list(self, methods_list, sort_by=None, reverse_order=True):
        '''
        tournament.results_list(
            [{'method' : 'method name 1'},...],
            sort_by = [{'method' : 'method name i'},...], reverse_order = True)
        returns a list of the results obtained by the various methods given.
        See the run method for information on the possible tie-breaks.
        '''
        try:
            # Create the list with the information
            info = list(zip(*(
                self._select_method(**method) for method in methods_list)))
            # Sort the results
            if sort_by:
                sort_indices=[methods_list.index(each) for each in sort_by]
                info.sort(
                    key=lambda lst: tuple(
                        self._extract(lst, sort_indices)),
                    reverse=reverse_order)
            # Finally add the players that did not play any round
            info.extend(
                self._did_not_play_methods(each, methods_list)
                for each in self._did_not_play)
            return info
            
        except KeyError as error:
            raise error from TournamentError('Invalid method.')
        except TypeError as error:
            raise error from TournamentError(
                'Method list\n{}\nis not valid.'.format(methods_list))
        except ValueError as error:
            raise error from TournamentError(
                'Invalid sorting method'.format(error))

    def _did_not_play_methods(self, name, methods_list):
        # Just return empty information except for the name
        return (
            name if method['method']=='Name' else ''
            for method in methods_list)

    def _select_method(
        self, *, method='Name', worst=0, best=0, epsilon=_EPSILON,
        max_iterations=_MAX_ITERATIONS):
        # Selects tie-breaking rules from a given list
        if method=='Name':
            yield from self._names
        elif method=='Elo':
            yield from self._elos
        elif method=='Points':
            yield from self._points
        elif method=='Played points':
            yield from self._played_points
        elif method=='Bucholz':
            yield from self._bucholz()
        elif method=='Average Bucholz':
            yield from self._average_bucholz()
        elif method=='Performance':
            yield from self._performance()
        elif method=='Recursive Performance' or method=='RP':
            if not self._recursive_performances:
                self._recursive_performance(
                    epsilon=epsilon, max_iterations=max_iterations)
            yield from self._recursive_performances  
        elif (
            method=='Average Recursive Performance of Opponents' or
            method=='ARPO'):
            if not self._recursive_performances:
                self._recursive_performance(
                    epsilon=epsilon, max_iterations=max_iterations)
            yield from self._rivals_average(
                self._recursive_performances, worst=worst, best=best)
        elif method=='Recursive Bucholz' or method=='RB':
            if not self._recursive_bucholzs:
                self._recursive_bucholz(
                    epsilon=epsilon, max_iterations=max_iterations)
            yield from self._recursive_bucholzs  
        elif (
            method=='Average Recursive Bucholz of Opponents' or
            method=='ARBO'):
            if not self._recursive_bucholzs:
                self._recursive_bucholz(
                    epsilon=epsilon, max_iterations=max_iterations)
            yield from self._rivals_average(self._recursive_bucholzs, worst=method.get('Worst', 0), best=method.get('Best', 0))
        else:
            raise KeyError(method)

    def _write_log_info(self, method_name, iterations, difference, sqrt=sqrt):
        # Writes log information about the convergence of the method
        log = self._log_info
        log['{} iterations'.format(method_name)] = iterations
        log['{} epsilon'.format(method_name)] = sqrt(difference)

    @property
    def log_info(self):
        '''
        Returns information on the methods runned by the Tournament class.
        '''
        return self._log_info

    @staticmethod        
    def _extract(target_list, indices):
        # Auxiliary function for extracting parts of lists
        return (target_list[each_index] for each_index in indices) #added if

    #def _extract(target_list, indices):
    #     for each_index in indices:
    #         target_list[each_index]
    #     return target_list

    ################### Tie-breaking rules ####################
    def _recursive_performance(
        self, epsilon=_EPSILON, max_iterations=_MAX_ITERATIONS):
        ''' Calculates the Recursive Performance tie-breaking rule.'''
        self._recursive_performances = self._recursive_method(
            'RP', self._rp_coefficient(), self._elos,
            epsilon=epsilon, max_iterations=max_iterations)

    def _recursive_bucholz(
        self, epsilon=_EPSILON, max_iterations=_MAX_ITERATIONS):
        ''' Calculates the Recursive Bucholz tie-breaking rule.'''
        # First iteration is vector of points rescaled to the number of rounds
        b0 = self._rb_first()
        self._recursive_bucholzs = self._recursive_method(
            'RB', self._rb_coefficient(), b0,
            epsilon=epsilon, max_iterations=max_iterations)


class TournamentError(Exception):
    '''
    A class that captures the errors produced by the Tournament class.
    '''
    def __init__(self, info):
        self.info = info

