import copy

class MiniChess:
    def __init__(self):
        self.current_game_state = self.init_board()
        self.currentTurn = 0
        self.captureTurn = 0
        self.winFlag = False
        self.fileOutput = ""
        self.maxTurns = 100

    def printG(self, output):
        """Capture outputs for gameTrace"""
        self.fileOutput += output + "\n"
        print(output)    

    def init_board(self):
        """Initialize the board"""
        return {
            "board": [
                ['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']
            ],
            "turn": 'white',
        }

    def display_board(self, game_state):
        """Prints the board"""
        self.printG("")
        for i, row in enumerate(game_state["board"], start=1):
            self.printG(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        self.printG("\n     A   B   C   D   E\n")

    def is_valid_move(self, game_state, move):
        """Check if the move is valid"""
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        board = game_state["board"]
        piece = board[start_row][start_col]

        # Prevent moving an empty square
        if piece == '.':
            return False  

        # Prevent moving opponent's piece
        if (game_state["turn"] == 'white' and 'b' in piece) or (game_state["turn"] == 'black' and 'w' in piece):
            return False  

        # Prevent capturing own piece
        if board[end_row][end_col] != '.' and board[end_row][end_col][0] == piece[0]:
            return False  

        piece_type = piece[1]

        # Movement validation based on piece type
        if piece_type == 'K':  # King moves one step in any direction
            return abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1
        elif piece_type == 'Q':  # Queen moves diagonally or in a straight line
            return self.is_valid_linear_move(board, start, end) or self.is_valid_diagonal_move(board, start, end)
        elif piece_type == 'B':  # Bishop moves diagonally
            return self.is_valid_diagonal_move(board, start, end)
        elif piece_type == 'N':  # Knight moves in L-shape
            return (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]
        elif piece_type == 'p':  # Pawn moves forward or captures diagonally
            direction = -1 if game_state["turn"] == 'white' else 1
            if start_col == end_col and board[end_row][end_col] == '.':  
                return end_row == start_row + direction
            elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
                return board[end_row][end_col] != '.' and board[end_row][end_col][0] != piece[0]
        return False  

    def is_valid_linear_move(self, board, start, end):
        "Checks linear (horizontal/vertical) movement"
        start_row, start_col = start
        end_row, end_col = end

        if start_row == end_row or start_col == end_col:
            row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)
            current_row, current_col = start_row + row_step, start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if board[current_row][current_col] != '.':
                    return False  # Path blocked
                current_row += row_step
                current_col += col_step
            return True
        return False

    def is_valid_diagonal_move(self, board, start, end):
        "Checks diagonal movement"
        start_row, start_col = start
        end_row, end_col = end

        if abs(start_row - end_row) == abs(start_col - end_col):
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            current_row, current_col = start_row + row_step, start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if board[current_row][current_col] != '.':
                    return False  # Path blocked
                current_row += row_step
                current_col += col_step
            return True
        return False

    def make_move(self, game_state, move):
        "Modify board to make a move"
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        piece = game_state["board"][start_row][start_col]
        game_state["board"][start_row][start_col] = '.'

        # Capture handling
        if game_state["board"][end_row][end_col] != '.':
            self.printG(f"Captured {game_state['board'][end_row][end_col]}!")
            if game_state["board"][end_row][end_col][1] == 'K':
                self.printG(f"{game_state['turn'].capitalize()} wins in {self.currentTurn} turns!")
                self.winFlag = True

        # Pawn promotion
        if piece[1] == 'p' and (end_row == 0 or end_row == 4):
            piece = piece[0] + 'Q'

        game_state["board"][end_row][end_col] = piece
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

        return game_state

    def parse_input(self, move):
        "Parse the input string into board coordinates"
        try:
            start, end = move.split()
            start = (5 - int(start[1]), ord(start[0].upper()) - ord('A'))
            end = (5 - int(end[1]), ord(end[0].upper()) - ord('A'))
            return start, end
        except:
            return None

    def gameTrace(self):
        "Creates a gameTrace file"
        filename = "gameTrace-false-5-100.txt"
        with open(filename, 'w') as f:
            f.write(self.fileOutput)
        print(f"\nGame Trace generated: {filename}")

    def play(self):
        "Game loop"
        self.printG("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
        while True:
            self.printG(f"Turn {self.currentTurn + 1}")
            self.display_board(self.current_game_state)

            move = input(f"{self.current_game_state['turn'].capitalize()} to move: ")
            if move.lower() == 'exit':
                self.printG("Game exited.")
                break

            move = self.parse_input(move)
            if not move or not self.is_valid_move(self.current_game_state, move):
                self.printG("Invalid move. Try again.")
                continue  

            self.currentTurn += 1
            self.make_move(self.current_game_state, move)

            if self.winFlag:
                self.printG("Final State:")
                self.display_board(self.current_game_state)
                self.gameTrace()
                break

if __name__ == "__main__":
    game = MiniChess()
    game.play()
