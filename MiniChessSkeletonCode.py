import re

class MiniChess:
    # Constants
    BOARD_SIZE = 5
    MAX_TURNS = 100         # Maximum half-moves (each valid move counts as one turn)
    FULL_TURNS_FOR_DRAW = 10  # 10 full turns (i.e. 20 half-moves) without a capture results in a draw
    MOVES_FOR_DRAW = FULL_TURNS_FOR_DRAW * 2  # 20 half-moves without capture

    def __init__(self):
        self.current_game_state = self.init_board()
        self.current_turn = 0  # Counts half-moves (each valid move counts)
        self.half_moves_since_capture = 0
        self.win_flag = False
        self.file_output = ""
        self.timeout = 5
        self.play_mode = "H-H"

    def init_board(self):
        """Initialize 5x5 board with starting positions"""
        return {
            "board": [
                ['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']
            ],
            "turn": 'white'  # White always starts
        }

    def print_game(self, output):
        """Record and display game output"""
        self.file_output += output + "\n"
        print(output)

    def display_board(self, game_state):
        """Display current board state"""
        self.print_game("")
        # Board row 0 is displayed as row 5, row 4 as row 1.
        for i, row in enumerate(game_state["board"], start=1):
            self.print_game(f"{self.BOARD_SIZE + 1 - i}  {' '.join(piece.rjust(3) for piece in row)}")
        self.print_game("\n     A   B   C   D   E\n")

    def convert_coordinate(self, coord):
        """
        Convert board coordinate tuple (row, col) to algebraic notation.
        For example, (4, 0) becomes "A1" and (0, 4) becomes "E5".
        """
        row, col = coord
        return f"{chr(col + ord('A'))}{self.BOARD_SIZE - row}"

    def parse_input(self, move):
        """
        Parse the input string using a regular expression to ensure the format is correct.
        Expected format is like "B2 B3" (letters A-E and digits 1-5).
        Returns a tuple ((start_row, start_col), (end_row, end_col)) or None if malformed.
        """
        move = move.strip()
        pattern = r'^[A-Ea-e][1-5]\s+[A-Ea-e][1-5]$'
        if not re.match(pattern, move):
            return None
        try:
            tokens = move.split()
            start, end = tokens[0], tokens[1]
            start_letter, start_digit = start[0].upper(), start[1]
            end_letter, end_digit = end[0].upper(), end[1]
            start_coord = (self.BOARD_SIZE - int(start_digit), ord(start_letter) - ord('A'))
            end_coord = (self.BOARD_SIZE - int(end_digit), ord(end_letter) - ord('A'))
            return start_coord, end_coord
        except Exception:
            return None

    def validate_move(self, game_state, move):
        """
        Validate the move and return a tuple (is_valid, error_message).
        Provides detailed feedback if the move is invalid.
        """
        if move is None:
            return False, "Move format incorrect. Please use the format 'B2 B3'."

        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        board = game_state["board"]

        if not self.is_within_bounds(start_row, start_col):
            return False, "Starting coordinate out of bounds."
        if not self.is_within_bounds(end_row, end_col):
            return False, "Destination coordinate out of bounds."

        piece = board[start_row][start_col]
        if piece == '.':
            return False, "No piece at the starting square."

        current_turn = game_state["turn"]
        if current_turn == 'white' and piece[0] != 'w':
            return False, "It's white's turn, but the selected piece is not white."
        if current_turn == 'black' and piece[0] != 'b':
            return False, "It's black's turn, but the selected piece is not black."

        target = board[end_row][end_col]
        if target != '.' and target[0] == piece[0]:
            return False, "Cannot move to a square occupied by your own piece."

        # Validate movement based on the type of piece.
        piece_type = piece[1]
        if piece_type == 'K':  # King moves one square any direction.
            if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
                return True, ""
            else:
                return False, "King can only move one square in any direction."
        elif piece_type == 'Q':  # Queen moves linearly or diagonally.
            if self.is_valid_linear_move(board, start, end) or self.is_valid_diagonal_move(board, start, end):
                return True, ""
            else:
                return False, "Queen must move in a straight line or diagonally with no obstacles."
        elif piece_type == 'B':  # Bishop moves diagonally.
            if self.is_valid_diagonal_move(board, start, end):
                return True, ""
            else:
                return False, "Bishop can only move diagonally with no obstacles."
        elif piece_type == 'N':  # Knight moves in an L-shape.
            if (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]:
                return True, ""
            else:
                return False, "Knight moves in an L-shape (2 squares in one direction and 1 in the other)."
        elif piece_type == 'p':  # Pawn: forward move or diagonal capture.
            direction = -1 if current_turn == 'white' else 1
            # Forward move
            if start_col == end_col:
                if end_row == start_row + direction and board[end_row][end_col] == '.':
                    return True, ""
                else:
                    return False, "Pawn can only move forward one square into an empty space."
            # Diagonal capture
            elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
                if board[end_row][end_col] != '.' and board[end_row][end_col][0] != piece[0]:
                    return True, ""
                else:
                    return False, "Pawn can only capture diagonally one square."
            else:
                return False, "Invalid pawn move."
        else:
            return False, "Unknown piece type encountered."

    def is_within_bounds(self, row, col):
        """Check if the given coordinates are within board bounds."""
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE

    def is_valid_linear_move(self, board, start, end):
        """Validate straight-line (horizontal or vertical) movement."""
        start_row, start_col = start
        end_row, end_col = end

        # Must be in same row or same column.
        if start_row != end_row and start_col != end_col:
            return False

        row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)

        current_row = start_row + row_step
        current_col = start_col + col_step

        while (current_row, current_col) != (end_row, end_col):
            if board[current_row][current_col] != '.':
                return False
            current_row += row_step
            current_col += col_step
        return True

    def is_valid_diagonal_move(self, board, start, end):
        """Validate diagonal movement."""
        start_row, start_col = start
        end_row, end_col = end

        if abs(start_row - end_row) != abs(start_col - end_col):
            return False

        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        current_row = start_row + row_step
        current_col = start_col + col_step

        while (current_row, current_col) != (end_row, end_col):
            if board[current_row][current_col] != '.':
                return False
            current_row += row_step
            current_col += col_step
        return True

    def make_move(self, game_state, move):
        """
        Execute the move, update the board, handle captures and pawn promotions,
        and switch turns. Returns a flag indicating if pawn promotion occurred.
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        board = game_state["board"]
        piece = board[start_row][start_col]
        captured = False

        # Check for capture
        if board[end_row][end_col] != '.':
            captured_piece = board[end_row][end_col]
            self.print_game(f"Captured {captured_piece}!")
            captured = True
            if captured_piece[1] == 'K':
                self.print_game(f"{game_state['turn'].capitalize()} wins in turn {self.current_turn + 1}!")
                self.win_flag = True

        board[start_row][start_col] = '.'

        # Handle pawn promotion:
        # For white, promotion when reaching row index 0; for black, row index BOARD_SIZE-1.
        promotion = False
        if piece[1] == 'p' and ((game_state["turn"] == 'white' and end_row == 0) or
                                (game_state["turn"] == 'black' and end_row == self.BOARD_SIZE - 1)):
            piece = piece[0] + 'Q'
            promotion = True

        board[end_row][end_col] = piece

        # Switch turn: note that we log the move before switching.
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

        # Update no-capture counter (each valid move is a half-move).
        if captured:
            self.half_moves_since_capture = 0
        else:
            self.half_moves_since_capture += 1

        return promotion

    def generate_game_trace(self):
        """Generate the game trace file with game parameters and move-by-move log."""
        filename = f"gameTrace-false-{self.timeout}-{self.MAX_TURNS}.txt"
        try:
            with open(filename, 'w') as f:
                f.write("Game Parameters:\n")
                f.write(f"    Timeout: {self.timeout} seconds\n")
                f.write(f"    Maximum Turns: {self.MAX_TURNS}\n")
                f.write(f"    Play Mode: {self.play_mode}\n")
                f.write("    Search Algorithm: None (Human vs Human)\n\n")
                f.write("Game Trace:\n")
                f.write(self.file_output)
            self.print_game(f"\nGame Trace generated: {filename}")
        except IOError:
            self.print_game("Error: Unable to write game trace.")

    def play(self):
        """Main game loop."""
        # Log game parameters and initial board configuration.
        self.print_game("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
        self.print_game("\nGame Parameters:")
        self.print_game(f"    Timeout: {self.timeout} seconds")
        self.print_game(f"    Maximum Turns: {self.MAX_TURNS}")
        self.print_game(f"    Play Mode: {self.play_mode}")
        self.print_game("    Search Algorithm: None (Human vs Human)")
        self.print_game("\nInitial Board:")
        self.display_board(self.current_game_state)

        while True:
            self.print_game(f"\nTurn {self.current_turn + 1}")
            self.display_board(self.current_game_state)

            move_input = input(f"{self.current_game_state['turn'].capitalize()} to move: ").strip()
            if move_input.lower() == 'exit':
                self.print_game("Game exited by user.")
                break

            move_coords = self.parse_input(move_input)
            valid, error_msg = self.validate_move(self.current_game_state, move_coords)
            if not valid:
                self.print_game("Invalid move. " + error_msg + " Try again.")
                continue

            # Log the move details in algebraic notation.
            start_coord, end_coord = move_coords
            self.print_game(f"{self.current_game_state['turn'].capitalize()} move: from {self.convert_coordinate(start_coord)} to {self.convert_coordinate(end_coord)}")

            self.current_turn += 1
            promotion = self.make_move(self.current_game_state, move_coords)
            if promotion:
                self.print_game(f"Pawn promoted to Queen at {self.convert_coordinate(end_coord)}!")

            # Check win condition.
            if self.win_flag:
                self.print_game("Final Board:")
                self.display_board(self.current_game_state)
                self.generate_game_trace()
                break

            # Check maximum moves condition.
            if self.current_turn >= self.MAX_TURNS:
                self.print_game("Maximum number of moves reached. Game is a draw.")
                self.generate_game_trace()
                break

            # Check draw condition: 10 full turns (20 half-moves) with no capture.
            if self.half_moves_since_capture >= self.MOVES_FOR_DRAW:
                self.print_game("No captures in 10 full turns (20 moves). Game is a draw.")
                self.generate_game_trace()
                break

if __name__ == "__main__":
    game = MiniChess()
    game.play()

