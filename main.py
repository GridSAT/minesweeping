from setagent import SetAgent
from game import Minesweeper
import argparse
from random import Random

def init():
    global args
    parser = argparse.ArgumentParser(description="Play an automated game of minesweeper")
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument("-s", "--seed",
                            help="Specify the seed for the game",
                            type=int,
                            default=None)
    seed_pair_group = parser.add_argument_group()
    seed_pair_group.add_argument("--board-seed",
                                 help="Specify the seed for the game board",
                                 type=int)
    seed_pair_group.add_argument("--agent-seed",
                                 help="Specify the seed for the game agent",
                                 type=int)
    dimensions_group = parser.add_argument_group()
    dimensions_group.add_argument("-r", "--rows", "-H", "--height",
                                  help="Specify the number of rows of the board",
                                  type=int,
                                  default=16)
    dimensions_group.add_argument("-c", "--columns", "-W", "--width",
                                  help="Specify the number of columns of the board",
                                  type=int,
                                  default=30)
    dimensions_group.add_argument("-m", "--mines",
                                  help="Specify the mine count of the board",
                                  type=int,
                                  default=99)
    parser.add_argument("-C", "--coloured",
                        help="Specify whether the board is coloured in previews",
                        action="store_true")
    parser.add_argument("-v", "--verbosity",
                        help="Increase output verbosity",
                        action="count")
    parser.add_argument("--show-mines",
                        help="Show the location of all mines on the board",
                        action="store_true")
    parser.add_argument("--show-strategy",
                        help="Highlight cells indicating the strategy of the currently playing AI. "
                             "Has no effect if verbosity is less than 3",
                        action="store_true")
    parser.add_argument("--play-count",
                        help="The number of times the bot should play",
                        type=int,
                        default=1)
    parser.add_argument("--density-range",
                        help="The range of mine densities the board should generate",
                        type=str,
                        default="none")
    parser.add_argument("--step-by-step",
                        help="Enables pausing the program at notable moments",
                        action="store_true")
    parser.add_argument("--first-safe",
                        help="Ensures the first tile clicked cannot be a mine",
                        action="store_true")
    args = parser.parse_args()


def main(mines):
    random = Random(args.seed)
    if args.board_seed is None:
        args.board_seed = random.getrandbits(64)
        print(f"Board seed: {args.board_seed}")
    if args.agent_seed is None:
        args.agent_seed = random.getrandbits(64)
        print(f"Agent seed: {args.agent_seed}")
    if args.verbosity is None:
        args.verbosity = 0
    args.mines = round((args.rows*args.columns)*(mines/100))
    game = Minesweeper(args.rows, args.columns, args.mines, args.board_seed, first_safe=args.first_safe)
    agent = SetAgent(game, seed=args.agent_seed)
    win_count = 0
    completion_rate = 0

    try:
        for i in range(args.play_count):
            game.reset()
            agent.play(show_mines=args.show_mines, coloured=args.coloured, verbosity=args.verbosity,
                       show_strategy=args.show_strategy, step_by_step=args.step_by_step)
            completion_rate += game.opened/(args.rows*args.columns)
            if args.step_by_step and args.play_count > 1:
                input()
            if game.winning_state():
                win_count += 1
            if args.verbosity < 1:
                print(
                    f"\r[{'=' * int(60 * (i + 1) / args.play_count)}{' ' * int(60 - 60 * (i + 1) / args.play_count)}] {'{:.1f}'.format((i + 1) / args.play_count * 100)}% ({'{:.1f}'.format(win_count / (i + 1) * 100)}%)",
                    end="")
    except KeyboardInterrupt:
        if args.verbosity < 1:
            print()
    completion_rate = completion_rate/args.play_count*100
    print()
    print(f"Won {win_count} out of {i+1} games ({win_count / (i+1) * 100}%)")
    print(f"Average completion rate: {round(completion_rate, 2)}%")
    return round(completion_rate, 2)


if __name__ == '__main__':
    args = argparse.Namespace
    init()
    rate_list = []
    if args.density_range != "none":
        start_density, end_density = list(map(int, args.density_range.split("-")))
        for i in range(start_density, end_density+1):
            rate_list.append([i, main(i)])
        for x in rate_list:
            print(f"{x[1]}")
    else:
        main(10)
