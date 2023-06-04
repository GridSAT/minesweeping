from minesweeper import *
from solver import * 

def solve(board, initial, max_depth=1, remainder_cutoff=0):
    solution = Solution(board.rows, board.cols, board.mines)
    initial_revealed = board.reveal_node(board.safe_initial())

    for node, value in initial_revealed:
        solution.grid.nodes[node]["solved"] = True 
        solution.grid.nodes[node]["value"] = value 
        if value == -1:
            return solution

    depth = 0

    for i in range(10000):
        solved = sat_inspect(solution, depth=depth)
        revealed = board.reveal_nodes(solved)
        for node, value in revealed:
            solution.grid.nodes[node]["solved"] = True 
            solution.grid.nodes[node]["value"] = value 
        if len(revealed) == 0:
            if depth < max_depth:
                depth += 1
            else:
                break
        else:
            depth = 0

    for i in range(1000):
        remainder_solved = solve_remainder(solution, cutoff=remainder_cutoff)
        remainder_revealed = board.reveal_nodes(remainder_solved)
        for node, value in remainder_revealed:
            solution.grid.nodes[node]["solved"] = True 
            solution.grid.nodes[node]["value"] = value 
        if len(remainder_revealed) == 0:
            break

    while not check_solution(board, solution):
        guess = guess_node(solution)
        if guess:
            guess_revealed = board.reveal_node(guess)
            for node, value in guess_revealed:
                solution.grid.nodes[node]["solved"] = True 
                solution.grid.nodes[node]["value"] = value
                if value == -1:
                    return solution

        for i in range(10000):
            solved = sat_inspect(solution, depth=depth)
            revealed = board.reveal_nodes(solved)
            for node, value in revealed:
                solution.grid.nodes[node]["solved"] = True 
                solution.grid.nodes[node]["value"] = value 
            if len(revealed) == 0:
                if depth < max_depth:
                    depth += 1
                else:
                    break
            else:
                depth = 0

        for i in range(1000):
            remainder_solved = solve_remainder(solution, cutoff=remainder_cutoff)
            remainder_revealed = board.reveal_nodes(remainder_solved)
            for node, value in remainder_revealed:
                solution.grid.nodes[node]["solved"] = True 
                solution.grid.nodes[node]["value"] = value 
            if len(remainder_revealed) == 0:
                break

    return solution

def check_solution(board, solution):
    for n in board.grid.nodes:
        if solution.grid.nodes[n]["solved"] and board.grid.nodes[n]["value"] == -1 and not solution.grid.nodes[n]["flagged"]:
            return -1
    for n in board.grid.nodes:
        if not solution.grid.nodes[n]["solved"] and board.grid.nodes[n]["value"] != -1:
            return 0
    return 1 

def update_solution(solution, revealed):
    for node, value in revealed:
        solution.grid.nodes[node]["solved"] = True 
        solution.grid.nodes[node]["value"] = value