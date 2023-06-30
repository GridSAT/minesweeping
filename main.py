from solver_imple import *

games_to_play = 100
games_won = 0
games_lost = 0

rows = 10
cols = 10
mines = 25

print(f"Playing {rows}x{cols}x{mines} boards for {games_to_play} games...")

for i in range(games_to_play):
    board = generate_board(rows, cols, mines)
    try:
        soln = solve(board, (random.randrange(rows), random.randrange(cols)))
        game_result = ""
        if check_solution(board, soln) == 1:
            games_won += 1
            game_result = "Game won!"
        else:
            games_lost += 1
            game_result = "Game lost."
        print(f"\r[{'=' * int(60 * (i + 1) / games_to_play)}{' ' * int(60 - 60 * (i + 1) / games_to_play)}] {'{:.1f}'.format((i + 1) / games_to_play * 100)}% ({'{:.1f}'.format(games_won / (i + 1) * 100)}%)", end="")
    except Exception as err:
        print(err)
        continue 
    

print(f"\nWin rate: {round(games_won/(games_won+games_lost)*100, 2)}%")