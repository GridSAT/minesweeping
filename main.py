from solver_imple import *

games_to_play = 5
games_won = 0
games_lost = 0

print("Running...")

for i in range(games_to_play):
    rows = 80
    cols = 80
    mines = 800
    board = generate_board(rows, cols, mines)
    try:
        # print("trying")
        soln = solve(board, (random.randrange(rows), random.randrange(cols)))
        game_result = ""
        if check_solution(board, soln) == 1:
            games_won += 1
            game_result = "Game won!"
        else:
            games_lost += 1
            game_result = "Game lost."
        print(f"Game {i+1}/{games_to_play}: {game_result} Win rate: {round(games_won/(games_won+games_lost)*100, 2)}% ({games_won}/{games_won+games_lost})")
        # print(soln)
    except Exception as err:
        print(err)
        continue 
    

print(f"Win rate: {round(games_won/(games_won+games_lost)*100, 2)}%")