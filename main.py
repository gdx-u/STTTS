import copy, time, os

X = 1
O = 2
_ = 3

boards = [
    [
        0, 0, 0, 0, 0, 0, 0, 0, 0
    ] for _ in range(9)
]

win_map = [0] * 9

winner = None

win_patterns = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
)

tile_powers = (
    3, 1, 3,
    1, 5, 1,
    3, 1, 3
)

def has_chance(board):
    X_chance = False
    O_chance = False

    for i in range(9):
        if board[i] == 0:
            if not X_chance:
                board[i] = X
                for a, b, c in win_patterns:
                    if board[a] == board[b] == board[c] == X:
                        X_chance = True
                        break
                board[i] = 0

            if not O_chance:
                board[i] = O
                for a, b, c in win_patterns:
                    if board[a] == board[b] == board[c] == O:
                        O_chance = True
                        break
                board[i] = 0

    return X_chance, O_chance


def analyze(boards, win_map, intended_board, player):
    advantage = 0
    for i, board in enumerate(win_map):
        advantage += 20 if board == X else -20 if board == O else 0

        if board == X:
            advantage += 2 * tile_powers[i]
        elif board == O:
            advantage -= 2 * tile_powers[i]

    
    for i, board in enumerate(boards):
        advantage += 0.3 if board.count(X) > board.count(O) else -0.3 if board.count(X) < board.count(O) else 0

        Xc, Oc = has_chance(board)
        advantage += 0.8 * tile_powers[i] if Xc else 0
        advantage -= 0.8 * tile_powers[i] if Oc else 0

        for i, piece in enumerate(board):
            if piece == X:
                advantage += tile_powers[i] * 0.4
            elif piece == O:
                advantage -= tile_powers[i] * 0.4


    if player == X and win_map[intended_board] != 0:
        advantage += 2
    elif player == O and win_map[intended_board] != 0:
        advantage -= 2 

    return advantage


def place(boards, win_map, i, player):    
    new = copy.deepcopy(boards)
    board, square = divmod(i, 9)
    new[board][square] = player

    new_win_map = win_map[:]

    sub = new[board]
    if all(sub):
        new_win_map[board] = _
        return new, new_win_map, None
    
    for a, b, c in win_patterns:
        if sub[a] == sub[b] == sub[c] == player:
            new_win_map[board] = player
            break
    else:
        return new, new_win_map, None
    
    main = new_win_map
    for a, b, c in win_patterns:
        if main[a] == main[b] == main[c] == player:
            return new, new_win_map, player
        
    return new, new_win_map, None

def find_possible_moves(boards, intended_board):
    out = []
    if win_map[intended_board] == 0:
        for i in range(9):
            if boards[intended_board][i] == 0:
                out += [intended_board * 9 + i]
        
        return out
    
    for i in range(81):
        if win_map[i // 9] != 0:
            continue

        if boards[i // 9][i % 9] == 0:
            out += [i]

    return out


MAX_DEPTH = 6
# NUM_CONSIDER = 10

def recurse(boards, win_map, player, intended_board, depth):
    if depth == MAX_DEPTH:
        return None, analyze(boards, win_map, intended_board, 3 - player)
    
    # X1 -> +, O2 -> -

    options = find_possible_moves(boards, intended_board)

    # for option in options:
    #     new_boards, new_win_map, winner = place(boards, win_map, option, player)
    #     if winner and winner == player:
    #         return option, 100 if player == X else -100
        
    #     values[option] = analyze(new_boards, new_win_map, intended_board, player)

    new_values = {}
    for option in options:
        new_boards, new_win_map, new_winner = place(boards, win_map, option, player)
        if new_winner:
            new_values[option] = 100 if new_winner == X else -100
        else:
            __, value = recurse(new_boards, new_win_map[:], X if player == O else O, option % 9, depth + 1)
            new_values[option] = value
            # if player == X and value == 100 or player == O and value == -100:
                # return option, value

    best = max(new_values.keys(), key=lambda e: new_values[e] if player == X else -new_values[e])

    return best, new_values[best]


def print_board():
    os.system("cls")
    output = output_format

    for i in range(80, -1, -1):
        output = output.replace(
            " " + str(i), (" " + "_XO"[boards[i // 9][i % 9]]) if win_map[i // 9] == 0 else (" " + " XO/"[win_map[i // 9]]), 1
        ).replace(
            "_", "asdfghjkl"[i % 9] if i // 9 == intended_board or win_map[intended_board or 0] != 0 or intended_board == None else "."
        )

    allowed_boards = []
    if intended_board == None or win_map[intended_board] != 0:
        allowed_boards = [n for n in range(9) if not win_map[n]]
    else:
        allowed_boards = [intended_board]

    for board in allowed_boards:
        output = output.replace("ABCDEFGHI"[board], "\033[1;32;48m" + "ABCDEFGHI"[board] + "\033[0m")

    for char in "asdfghjkl":
        output = output.replace(char, str(" asdfghjkl".index(char)))

    print(output.replace(
        "O", "\033[1;34;48mO\033[0m"
    ).replace(
        "X", "\033[1;31;48mX\033[0m"
    ))

output_format = open("output.txt", "r").read()


ai_analysis = None
ai_move = None
intended_board = None
while True:
    if winner:
        print_board()
        print("WINNER IS", " XO"[winner])
        break

    print_board()
    print(f"AI last move: {('ABCDEFGHI'[ai_move // 9] + str(ai_move % 9 + 1)) if ai_move else '[FIRST TURN]'} // Analysis: {(ai_analysis or 0):.2f}")
    
    coord = "J"
    i = 81
    while intended_board != None and i // 9 != intended_board and win_map[intended_board] == 0 or i < 0 or i > 80 or coord[0] > "I" or coord[0] < "A":
        coord = input("Coordinate: (e.g. E5 is the middle square) ")
        i = "ABCDEFGHI".index(coord[0]) * 9 + int(coord[1]) - 1

    intended_board = i % 9

    boards, win_map, winner = place(boards, win_map, i, X)
    if winner:
        print_board()
        print("WINNER IS", " XO"[winner])
        break

    print_board()

    ai_move, ai_analysis = recurse(boards, win_map, O, intended_board, 1)
    intended_board = ai_move % 9


    boards, win_map, winner = place(boards, win_map, ai_move, O)