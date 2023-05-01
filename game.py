from typing import Iterable, IO
from itertools import product as iter_prod
from random import Random
import numpy as np

class Minesweeper:
    def __init__(self, rows: int, columns: int, mines: int, seed=None, first_safe=False):
        self.grid = None
        self.stepped = None
        self._mines = None
        self.flagged = None
        self._ignore_mine = None
        self.col_count = columns
        self.row_count = rows
        self.mine_count = mines
        self.first_safe = first_safe
        self.opened = 0
        self.random = Random(seed)
        self.reset()

    def reset(self):
        self.grid = {(row, col) for row, col in iter_prod(range(self.row_count), range(self.col_count))}
        self.stepped = set()
        self._mines = set(self.random.sample(tuple(self.grid), self.mine_count))
        # self._mines = {(0, 4), (3,4), (4,0), (4,3), (4,4)}
        print(self._mines)
        self.flagged = set()
        self._ignore_mine = self.first_safe

    def winning_state(self):
        if len(self.stepped & self._mines) > 0:
            return False
        if self.mines_remaining() == 0:
            return True
        return False

    def neighbours(self, cell):
        naive_neighbours = set((cell[0] + row, cell[1] + col) for row, col in iter_square(range(-1, 2)))
        naive_neighbours.remove(cell)
        return set.intersection(self.grid, naive_neighbours)

    def cell_value(self, cell):
        if cell not in self.stepped:
            raise ValueError("That's cheating!")
        return len(set.intersection(self.neighbours(cell), self._mines))

    def step(self, cell, f=None):
        self.stepped.add(cell)
        if cell in self._mines:
            if self._ignore_mine:
                new_mine = self.random.choice(tuple(self.grid - self.stepped - self._mines))
                self._mines.remove(cell)
                self._mines.add(new_mine)
            else:
                raise ValueError("Boom!")
        self._ignore_mine = False
        return self.cell_value(cell)

    def flag(self, cell):
        if cell in self.stepped:
            return False
        self.flagged.add(cell)
        return True

    def mines_remaining(self):
        return len(self._mines - self.flagged)

    def tiles_remaining(self):
        return len(self.grid - self.stepped - self.flagged)

    def opened_tiles(self, **kwargs):
        opened = 0
        for row in range(self.row_count):
            for col in range(self.col_count):
                if (row, col) in self.stepped:
                    if (row, col) in self._mines:
                        opened += 1
                    else:
                        opened += 1
                elif (row, col) in self.flagged:
                    opened += 1
        self.opened = opened

    def draw(self, **kwargs):
        show_mines = kwargs['show_mines'] if "show_mines" in kwargs.keys() else False
        end = kwargs['end'] if 'end' in kwargs.keys() else "\n"
        opened = 0
        for row in range(self.row_count):
            for col in range(self.col_count):
                if (row, col) in self.stepped:
                    if (row, col) in self._mines:
                        print("X", end=" ")
                        opened += 1
                    else:
                        value = self.cell_value((row, col))
                        opened += 1
                        print(value, end=" ")
                elif (row, col) in self.flagged:
                    print("F", end=" ")
                    opened += 1
                else:
                    if show_mines and (row, col) in self._mines:
                        print("M", end=" ")
                    else:
                        print("#", end=" ")
            print()
        print(end=end)

    def get_board(self):
        board = np.zeros((self.row_count, self.col_count), dtype=np.int8)
        for cell in iter_prod(range(self.row_count), range(self.col_count)):
            board[cell] = len(set.intersection(self.neighbours(cell), self._mines))
        for mine in self._mines:
            board[mine] = 9
        return board


def iter_square(i):
    return iter_prod(i, i)

def ansi_seq(*args):
    return "\x1b[" + ";".join(args) + "m"
