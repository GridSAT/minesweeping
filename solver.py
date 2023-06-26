import random
import math
import itertools as it 

import networkx as nx 
from bidict import bidict 
from pysat.formula import CNF 
from pysat.solvers import Minisat22 

class Solution:
    def __init__(self, rows, cols, mines):
        self.rows = rows 
        self.cols = cols 
        self.mines = mines 
        self.unsolved = mines 

        self.grid = nx.grid_2d_graph(rows, cols) 
        self.grid.add_edges_from([
            ((x, y), (x+1, y+1))
            for x in range(rows-1)
            for y in range(cols-1)
        ] + [
            ((x+1, y), (x, y+1))
            for x in range(rows-1)
            for y in range(cols-1)
        ], weight=1.4)

        for n in self.grid.nodes:
            self.grid.nodes[n]["value"] = 0
            self.grid.nodes[n]["solved"] = False 
            self.grid.nodes[n]["flagged"] = False 

    def __str__(self):
        string = ''
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid.nodes[i, j]['solved']:
                    if self.grid.nodes[i, j]['value'] == -1:
                        if self.grid.nodes[i, j]['flagged']:
                            string = string + ' . '
                        else:
                            string = string + ' * '
                    else:
                        if self.grid.nodes[i, j]['value'] == 0:
                            string = string + '   '
                        else:
                            string = string + ' ' + str(self.grid.nodes[i, j]['value']) + ' '
                else:
                    string = string + ' _ '
            string = string + '\n'
        return string


def sat_inspect_cell(solution, source, depth=1):
    if not solution.grid.nodes[source]["solved"]:
        return []

    dfs_tree = nx.dfs_tree(solution.grid, source, depth_limit=depth)
    border_nodes = set([n for n in dfs_tree.nodes if solution.grid.nodes[n]["solved"]
                        and any(not solution.grid.nodes[m]["solved"] for m in solution.grid.neighbors(n))])
    
    if len(border_nodes) == 0:
        return []

    unknown_nodes = set()

    for n in border_nodes:
        for m in solution.grid.neighbors(n):
            if not solution.grid.nodes[m]["solved"]:
                unknown_nodes.add(m)

    variable_by_node = bidict({})
    variable = 1
    for n in unknown_nodes:
        variable_by_node[n] = variable
        variable += 1

    cnf = CNF()
    for n in border_nodes:
        if solution.grid.nodes[n]["value"] == -1:
            continue 

        adj = list(solution.grid.neighbors(n))
        adj_unknown = [m for m in adj if not solution.grid.nodes[m]["solved"]]
        adj_mine = [m for m in adj if solution.grid.nodes[m]["solved"] and solution.grid.nodes[m]["value"] == -1]

        variables = [variable_by_node[m] for m in adj_unknown]

        mines_total = solution.grid.nodes[n]["value"]
        mines_needed = mines_total - len(adj_mine)

        left_combis = set(it.combinations(variables, len(adj_unknown) + 1 - mines_needed))
        right_combis = set(it.combinations(variables, 1 + mines_needed))

        for lc in left_combis:
            cnf.append(lc)
        for rc in right_combis:
            cnf.append([-1 * rc[i] for i in range(len(rc))])

    solutions = []
    for i in range(100000):
        with Minisat22(bootstrap_with=cnf.clauses) as solver:
            has_solution = solver.solve()
            model = solver.get_model()
        if has_solution:
            cnf.append([-1 * model[i] for i in range(len(model))])
            solutions.append(model)
        else:
            break

    discovered_variables = []
    for j in range(len(solutions[0])):
        certain = True 
        first = solutions[0][j]
        for i in range(len(solutions)):
            if not solutions[i][j] == first:
                certain = False 
                break
        if certain:
            discovered_variables.append(first) 
        
    solved_nodes = []
    for v in discovered_variables:
        node = variable_by_node.inv[abs(v)]
        solved_nodes.append(node)
        if v > 0:
            solution.grid.nodes[node]["flagged"] = True 
        
    return solved_nodes

def sat_inspect(solution, depth=1):
    solved_nodes = []
    for n in solution.grid.nodes:
        solved_nodes += sat_inspect_cell(solution, n, depth=depth)
    return solved_nodes 

def solve_remainder(solution, cutoff=16):
    global_mines_solved = sum(
        1 for n in solution.grid.nodes if solution.grid.nodes[n]["solved"] and solution.grid.nodes[n]["value"] == -1
    )
    global_mines_needed = solution.mines - global_mines_solved 

    border_nodes = set([
        n for n in solution.grid.nodes if solution.grid.nodes[n]["solved"]
        and any(not solution.grid.nodes[m]["solved"] for m in solution.grid.neighbors(n))
    ])
    unknown_nodes = set([
        n for n in solution.grid.nodes if not solution.grid.nodes[n]["solved"]
    ])

    if len(unknown_nodes) <= cutoff:
        variable_by_node = bidict({})
        variable = 1
        for n in unknown_nodes:
            variable_by_node[n] = variable 
            variable += 1

        cnf = CNF()

        global_left_combis = set(
            it.combinations(
                list(variable_by_node.values()),
                len(unknown_nodes) + 1 - global_mines_needed
            )
        )
        global_right_combis = set(
            it.combinations(
                list(variable_by_node.values()),
                1 + global_mines_needed
            )
        )

        for glc in global_left_combis:
            cnf.append(glc)
        for grc in global_right_combis:
            cnf.append([-1 * grc[i] for i in range(len(grc))])

        for n in border_nodes:
            if solution.grid.nodes[n]["value"] == -1:
                continue 

            adj = list(solution.grid.neighbors(n))
            adj_unknown = [m for m in adj if not solution.grid.nodes[m]["solved"]]
            adj_mine = [m for m in adj if solution.grid.nodes[m]["solved"] and solution.grid.nodes[m]["value"] == -1]

            variables = [variable_by_node[m] for m in adj_unknown]

            mines_total = solution.grid.nodes[n]["value"]
            mines_needed = mines_total - len(adj_mine)

            left_combis = set(
                it.combinations(
                    variables,
                    len(adj_unknown) + 1 - mines_needed
                )
            )
            right_combis = set(
                it.combinations(
                    variables, 
                    1 + mines_needed
                )
            )

            for lc in left_combis:
                cnf.append(lc)
            for rc in right_combis:
                cnf.append([-1 * rc[i] for i in range(len(rc))])

        solutions = []
        for i in range(100000):
            with Minisat22(bootstrap_with=cnf.clauses) as solver:
                has_solution = solver.solve()
                model = solver.get_model()
            if has_solution:
                cnf.append([-1 * model[i] for i in range(len(model))])
                solutions.append(model)
            else:
                break

        discovered_variables = []
        for j in range(len(solutions[0])):
            certain = True
            first = solutions[0][j]
            for i in range(len(solutions)):
                if not solutions[i][j] == first:
                    certain = False 
                    break
            if certain:
                discovered_variables.append(first)

        solved_nodes = []
        for v in discovered_variables:
            node = variable_by_node.inv[abs(v)]
            solved_nodes.append(node)
            if v > 0:
                solutions.grid.nodes[node]["flagged"] = True
        return solved_nodes 

    else:
        return []

def guess_node(solution):
    unknown_nodes = set([n for n in solution.grid.nodes if not solution.grid.nodes[n]["solved"]])
    if len(unknown_nodes) == 0:
        return []

    mines_solved = sum(1 for n in solution.grid.nodes if solution.grid.nodes[n]["solved"] and solution.grid.nodes[n]["value"] == -1)
    mines_needed = solution.mines - mines_solved 

    locked_nodes = set([n for n in unknown_nodes if all(not solution.grid.nodes[m]["solved"] for m in solution.grid.neighbors(n))])
    unlocked_nodes = unknown_nodes - locked_nodes  

    possible_guesses = dict()

    for n in locked_nodes:
        a = math.comb(len(unknown_nodes) - 1 - len(list(solution.grid.neighbors(n))), mines_needed)
        b = math.comb(len(unknown_nodes) - 1 , mines_needed)
        progress = a / b
        mines_accounted = 0
        for m in solution.grid.nodes:
            mines_accounted += solution.grid.nodes[m]["value"] - len([k for k in solution.grid.neighbors(m) if solution.grid.nodes[k]["flagged"]])
        safety = 1 - ((mines_needed - mines_accounted) / (len(unknown_nodes) - 1))
        if safety == 1:
            return n
        else:
            possible_guesses[n] = ((2/3) * safety + (1/3) * progress) 

    for n in unlocked_nodes:
        surroundings = [m for m in solution.grid.neighbors(n) if solution.grid.nodes[m]["solved"] and not solution.grid.nodes[m]["flagged"] and solution.grid.nodes[m]["value"] != -1]
        safeties = []

        for m in surroundings:
            val = solution.grid.nodes[m]["value"]
            val -= len([k for k in solution.grid.neighbors(m) if solution.grid.nodes[k]["flagged"]])
            local_space = len([k for k in solution.grid.neighbors(m) if not solution.grid.nodes[k]["solved"]])
            safeties.append(1 - (val/local_space))

        if safeties:
            possible_guesses[n] = sum(safeties)/len(safeties)
        

    if possible_guesses:
        guess = sorted(possible_guesses, key=lambda x: possible_guesses[x], reverse=True)[0]
        print(possible_guesses[guess])
        return guess
    else:
        return random.choice(list(unknown_nodes))


def is_complete(solution):
    for n in solution.grid.nodes:
        if not solution.grid.nodes[n]["solved"]:
            return False 
    return True