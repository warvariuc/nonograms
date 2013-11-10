import unittest

from nonograms import solver


class SolverTest(unittest.TestCase):

    def _test_solve_line(self, line, numbers, solved):
        self.assertEqual(solver.solve_line(line, numbers), solved)

    def test_solve_line(self):
        self._test_solve_line(
            '                         ', [15],
            '          @@@@@          ')
        self._test_solve_line(
            '                              ', [10, 12],
            '       @@@        @@@@@       ')
        self._test_solve_line(
            '@@@@@@ @   ', [6, 1],
            '@@@@@@.@...')
        self._test_solve_line(
            '@..............   @@.@@ @', [1, 4, 4],
            '@...............@@@@.@@@@')
