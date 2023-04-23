from itertools import combinations
from simpleagent import SimpleAgent
from game import Minesweeper


class SetAgent(SimpleAgent):

    def __init__(self, game: Minesweeper, seed=None):
        super().__init__(game, seed=seed)

    def pairwise(self, a, b):
        to_step = set()
        to_flag = set()
        av = self.game.cell_value(a)
        bv = self.game.cell_value(b)
        an = self.game.neighbours(a)
        bn = self.game.neighbours(b)
        af = an & self.game.flagged
        bf = bn & self.game.flagged
        vdiff = av - bv
        fdiff = len(af) - len(bf)
        amb = an - bn
        bma = bn - an
        pos_cells = amb - self.game.stepped
        neg_cells = bma - self.game.stepped
        pos_cells_no_flags = pos_cells - self.game.flagged
        neg_cells_no_flags = neg_cells - self.game.flagged
        if vdiff - fdiff == len(pos_cells_no_flags):
            to_flag |= pos_cells_no_flags
            to_step |= neg_cells_no_flags
        if fdiff - vdiff == len(neg_cells_no_flags):
            to_flag |= neg_cells_no_flags
            to_step |= pos_cells_no_flags
        return to_step, to_flag

    def play(self, **kwargs):
        show_mines = kwargs['show_mines'] if "show_mines" in kwargs.keys() else False
        coloured = kwargs['coloured'] if 'coloured' in kwargs.keys() else False
        verbosity = kwargs['verbosity'] if 'verbosity' in kwargs.keys() else 0
        show_strategy = kwargs['show_strategy'] if 'show_strategy' in kwargs.keys() else False
        step_by_step = kwargs['step_by_step'] if 'step_by_step' in kwargs.keys() else False
        cell_path = kwargs['cell_graphic_path'] if 'cell_graphic_path' in kwargs.keys() else None
        flagged_path = kwargs['flagged_graphic_path'] if 'flagged_graphic_path' in kwargs.keys() else None
        mine_path = kwargs['mine_graphic_path'] if 'mine_graphic_path' in kwargs.keys() else None
        # the tiles we know we need to step onto next
        to_step = {(self.random.randrange(self.game.row_count), self.random.randrange(self.game.col_count))}
        # the tiles we know to flag next
        to_flag = set()
        # the tiles we have already stepped onto and need to search
        to_search = set()
        # the tiles to use for pairwise search
        to_pair_search = set()
        running = True
        state_changed = False
        while len(self.game.grid - self.game.flagged - self.game.stepped) > 0 and running:
            if len(to_step) + len(to_flag) + len(to_search) == 0 and not state_changed:
                # make random choices smarter
                prob_mine = self.game.mines_remaining() / self.game.tiles_remaining()
                prob_not_mine = 1 - prob_mine
                field = self.game.grid - self.game.flagged - self.game.stepped
                # we use what's in the to-pair-wise search list, as we know they're all adjacent to untouched cells
                for cell in to_pair_search:
                    this_field = self.game.neighbours(cell) - self.game.flagged - self.game.stepped
                    this_prob_mine = (self.game.cell_value(cell) - len(self.game.neighbours(cell) & self.game.flagged)) / len(this_field)
                    if this_prob_mine <= prob_mine:
                        prob_mine = this_prob_mine
                        field = this_field
                tile = self.random.choice(list(field))
                if self.game.mines_remaining() == self.game.tiles_remaining():
                    to_flag.add(tile)
                else:
                    to_step.add(tile)
            state_changed = False
            # flag a tile we know we should flag
            while len(to_flag) > 0:
                tile = to_flag.pop()
                self.game.flag(tile)
                for neighbour in self.game.neighbours(tile) & self.game.stepped:
                    to_search.add(neighbour)
                state_changed = True
            # step onto a tile we know we should step onto
            while len(to_step) > 0:
                tile = to_step.pop()
                try:
                    self.game.step(tile, None)
                except ValueError:
                    running = False
                to_search.add(tile)
                for neighbour in self.game.neighbours(tile) & self.game.stepped:
                    to_search.add(neighbour)
                state_changed = True
            if verbosity > 2:
                self.game.draw(show_mines=show_mines, coloured=coloured, highlighted=list(to_pair_search) if show_strategy else None, underlined=list(to_search) if show_strategy else None)
                if step_by_step:
                    input()
            # search a tile we know we should search
            if len(to_search) > 0:
                while len(to_search) > 0:
                    tile = to_search.pop()
                    new_steps, new_flags = self.primitive(tile)
                    to_step |= new_steps
                    to_flag |= new_flags
                    if len(self.game.neighbours(tile) - (self.game.stepped | self.game.flagged | to_step | to_flag)) != 0:
                        to_pair_search.add(tile)
                        state_changed = True
                    else:
                        try:
                            to_pair_search.remove(tile)
                        except KeyError:
                            pass
            else:
                for a, b in combinations(to_pair_search, 2):
                    if len(self.game.neighbours(a) & self.game.neighbours(b)) != 0:
                        new_steps, new_flags = self.pairwise(a, b)
                        to_step |= new_steps
                        to_flag |= new_flags
                        if len(new_flags | new_steps) > 0:
                            for neighbour in (self.game.neighbours(a) | self.game.neighbours(b)) & self.game.stepped:
                                to_search.add(neighbour)
                            try:
                                to_pair_search.remove(a)
                            except KeyError:
                                pass
                            try:
                                to_pair_search.remove(b)
                            except KeyError:
                                pass
                            state_changed = True
        self.game.opened_tiles()
        if verbosity > 1:
            self.game.draw(show_mines=show_mines, coloured=coloured)
        if verbosity > 0:
            if self.game.winning_state():
                print("I Won!")
            else:
                print("I lost...")
