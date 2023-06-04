from solver_imple import *

games_to_play = 100
games_won = 0
games_lost = 0

while games_to_play:
    rows = 10
    cols = 10
    mines = 10
    board = generate_board(rows, cols, mines)
    #try:
    print("trying")
    soln = solve(board, (random.randrange(rows), random.randrange(cols)))
    if check_solution(board, soln) == 1:
        games_won += 1
    else:
        games_lost += 1
    print(games_to_play)
    print(soln)
    games_to_play -= 1
    #except Exception as err:
        #print(err)
        #continue 


    

print(f"Win rate: {round(games_won/(games_won+games_lost)*100, 2)}%")