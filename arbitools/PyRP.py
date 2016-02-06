'''
PyRP is a module that implements various tie-breaking rules for
Swiss tournaments including Recursive Performance and Recursive Bucholz.
The class Tournament encapsulates the funtionality to calculate the
tie-breaking rules and to import from Swiss Manager outputs.
'''

import sys
from itertools import dropwhile, compress

from arbitools._PyRP import _Tournament, TournamentError, _FewRounds


class Tournament(_Tournament):
    '''
    Defines a class that holds the data of a Swiss tournament and gives
    functionality to calculate some tie-breaking rules and print the
    results to a file.
    '''
    def _import_swiss_manager(self, file_name, elo_default, draw_character):
        with open(file_name) as file:
            file_iter, index_name, index_elo, index_points, index_rounds =\
                self._read_first_line(file)
            
            # Read the rest of the file and split the fields in the list
            lines = [line.split(';') for line in file_iter]
            
            # Fill in the information
            self._names = [line[index_name] for line in lines]
            # First, determine which players haven't played any round
            self._opponents = [
                Tournament._calculate_opponents(line, index_rounds)
                for line in lines]
            self._number_of_opponents = [len(opps) for opps in self._opponents]
            self._did_not_play = [
                name for name, opps in zip(
                    self._names, self._number_of_opponents) if opps==0]
            
            # Now, save only the relevant players
            self._names = list(compress(self._names, self._number_of_opponents))
            self._elos = [
                Tournament._calculate_elo(line[index_elo], elo_default)
                for line in compress(lines, self._number_of_opponents)]
            self._points = [
                Tournament._calculate_points(
                    line[index_points], draw_character=draw_character)
                for line in compress(lines, self._number_of_opponents)]
            self._played_points = [
                Tournament._calculate_played_points(
                    line, index_rounds, draw_character)
                for line in compress(lines, self._number_of_opponents)]
            self._number_of_opponents = list(compress(
                self._number_of_opponents, self._number_of_opponents))
            self._number_of_rounds = len(index_rounds)

    def _read_log(self):
        less_than_half = {
            name for name,number in zip(self._names, self._number_of_opponents)
            if number<self._number_of_rounds/2} - set(self._did_not_play)
        return _FewRounds(set(self._did_not_play), less_than_half)

    ################### Tie-breaking rules ####################
    def _bucholz(self):
        ''' Calculates the Bucholz tie-breaking rule.'''
        return (
            sum(self._extract(self._points, opp)) for opp in self._opponents)

    def _average_bucholz(self):
        ''' Calculates the average score of the opponents.'''
        return (
            sum(self._extract(self._points, opps)) / num
            for num, opps in zip(self._number_of_opponents, self._opponents))

    def _performance(self):
        ''' Calculates the performance of the players.'''
        average_elos = (
            sum(self._extract(self._elos, opps))/num
            for num, opps in zip(self._number_of_opponents, self._opponents))
        factors = (
            Tournament._performance_table[
                int(100 * points / num + 0.5)]
            for points, num in zip(
                self._played_points, self._number_of_opponents))
        return (
            elos + factor for elos, factor in zip(average_elos, factors))
  
    def _rp_coefficient(self):
        # Recursive Performance coefficient
        c = [
            Tournament._performance_table[
                int(100 * points / num + 0.5)]
            for points, num in zip(
                self._played_points, self._number_of_opponents)]
        inflation = (
            sum(ci*num for ci, num in zip(c, self._number_of_opponents)) /
            sum(self._number_of_opponents))
        return [ci-inflation for ci in c]

    def _rb_coefficient(self):
        # Recursive Bucholz coefficient
        return [
            points / num - 0.5
            for points, num in zip(
                self._played_points, self._number_of_opponents)]

    def _rb_first(self):
        #Return the first iterand for the recursive Bucholz
        return [
            self._number_of_rounds * points / num
            if num!=0 else float('nan')
            for num, points in zip(
                self._number_of_opponents, self._played_points)]

    def _recursive_method(
        self, method_name, c, p0, epsilon=_Tournament._EPSILON,
        max_iterations=_Tournament._MAX_ITERATIONS):
        # Iterative process
        for k in range(max_iterations):
            # Next iteration
            p = [
                sum(self._extract(p0, opps)) / num + ci
                for ci, opps, num in zip(
                    c, self._opponents, self._number_of_opponents)]
            # Epsilon test
            difference = sum(num * (pi-p0i)**2 for num, p0i, pi in zip(
                self._number_of_opponents, p0, p))
            if difference < epsilon**2:
                self._write_log_info(method_name, k, difference)
                return p
            else:
                # Update iterand and continue
                p0 = p
            
        else:
            # The method did not converge
            try:
                self._write_log_info(method_name, max_iterations, difference)
                raise TournamentError(
                    'The {} method did not converge'.format(method_name))
            except:
                pass

    def _rivals_average(self, strengths, worst=0, best=0):
        # Average strength of the opponents removing best and worst opponents
        return (
            self._rivals_average_each(strengths, opps, worst, best)
            for opps in self._opponents)

    def _rivals_average_each(self, strengths, opponents, worst, best):
        # Sort opponents strengths and take out worst and best opponents
        rivals_strengths = sorted(
            self._extract(strengths, opponents),
            reverse=True)[best:self._number_of_rounds - worst]
        return (
            sum(rivals_strengths) / len(rivals_strengths)
            if rivals_strengths else float('nan'))
                   

########################### Run an example ###############################
if __name__ == '__main__':
    t = Tournament.load(r'testing.txt')
    t.run(
        methods_list=(
            {'method': 'Name'}, {'method': 'Points'},
            {'method': 'Elo'}, {'method': 'Average Bucholz'},
            {'method': 'Performance'}, {'method': 'RB'},
            {'method': 'RP'}, {'method': 'ARPO', 'worst': 1},
            {'method': 'ARPO', 'worst': 2},
            {'method': 'ARPO', 'worst': 1, 'best': 1}),
        #output_file=r'results.csv',
        sort_by=(
            {'method': 'Points'}, {'method': 'ARPO', 'worst': 1, 'best': 1}))
