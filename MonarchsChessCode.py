import re
import time
import copy

class MiniChess:
    # Constants
    BOARD_SIZE = 5
    MAX_TURNS = 100         # Maximum half-moves (each valid move counts as one turn)
    FULL_TURNS_FOR_DRAW = 10  # 10 full turns (i.e. 20 half-moves) without a capture results in a draw
    MOVES_FOR_DRAW = FULL_TURNS_FOR_DRAW * 2  # 20 half-moves without capture

    def __init__(self):
        # Initialize game state and parameters.
        self.current_game_state = self.init_board()
        self.current_turn = 0  # Counts half-moves (each valid move counts)
        self.half_moves_since_capture = 0
        self.win_flag = False
        self.file_output = ""
        self.timeout = 5  # Maximum allowed time (in seconds) for an AI move.
        
        # Default settings; these will be updated by user input.
        self.play_mode = "H-H"  # A string summarizing the overall mode.
        # Dictionary to define each player's type: "human" or "ai".
        self.player_types = {"white": "human", "black": "human"}
        
        # AI algorithm settings:
        self.use_alpha_beta = False  # If True, use alpha-beta pruning; if False, plain minimax.
        self.heuristic_choice = "e0"   # Choose among "e0", "e1", or "e2" for board evaluation.

    def init_board(self):
        """Initialize 5x5 board with starting positions."""
        return {
            "board": [
                ['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']
            ],
            "turn": 'white'  # White always starts.
        }

    def print_game(self, output):
        """Record and display game output (to both command line and trace log)."""
        self.file_output += output + "\n"
        print(output)

    def display_board(self, game_state):
        """Display current board state with row numbers and column labels."""
        self.print_game("")
        # Display board so that board row 0 appears as row 5, row 4 as row 1.
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

        # Must be in the same row or same column.
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

    def get_all_valid_moves(self, game_state):
        """
        Generate and return a list of all valid moves for the current player.
        This is used by the AI search to explore possible moves.
        """
        moves = []
        board = game_state["board"]
        current_turn = game_state["turn"]
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                piece = board[i][j]
                if piece != '.' and ((current_turn == 'white' and piece[0] == 'w') or (current_turn == 'black' and piece[0] == 'b')):
                    for x in range(self.BOARD_SIZE):
                        for y in range(self.BOARD_SIZE):
                            move = ((i, j), (x, y))
                            valid, _ = self.validate_move(game_state, move)
                            if valid:
                                moves.append(move)
        return moves

    def is_game_over(self, game_state):
        """
        Check if the game is over by ensuring that both kings are still on the board.
        """
        board = game_state["board"]
        kings = 0
        for row in board:
            for piece in row:
                if piece != '.' and piece[1] == 'K':
                    kings += 1
        return kings < 2

    def evaluate_board(self, game_state):
        """
        Evaluate the board using the selected heuristic.
        Three heuristics are available:
            - e0: (#wp + 3*#wB + 3*#wN + 9*#wQ + 999*#wK) -
                  (#bp + 3*#bB + 3*#bN + 9*#bQ + 999*#bK)
            - e1 and e2 are variations; here we make simple adjustments.
        """
        board = game_state["board"]
        white_value = 0
        black_value = 0
        for row in board:
            for piece in row:
                if piece == '.':
                    continue
                color = piece[0]
                p_type = piece[1]
                if self.heuristic_choice == "e0":
                    weights = {'p': 1, 'B': 3, 'N': 3, 'Q': 9, 'K': 999}
                elif self.heuristic_choice == "e1":
                    weights = {'p': 1, 'B': 3, 'N': 3, 'Q': 9, 'K': 900}
                elif self.heuristic_choice == "e2":
                    weights = {'p': 1, 'B': 3, 'N': 3, 'Q': 9, 'K': 1200}
                else:
                    weights = {'p': 1, 'B': 3, 'N': 3, 'Q': 9, 'K': 999}

                if color == 'w':
                    white_value += weights.get(p_type, 0)
                else:
                    black_value += weights.get(p_type, 0)
        return white_value - black_value

    def minimax(self, game_state, depth, maximizing, alpha, beta, start_time, time_limit, current_depth=0):
        """
        Minimax search with optional alpha-beta pruning.
        Returns a tuple (best_move, best_score).
        """
        if time.time() - start_time > time_limit:
            return None, self.evaluate_board(game_state)
        if depth == 0 or self.is_game_over(game_state):
            return None, self.evaluate_board(game_state)

        valid_moves = self.get_all_valid_moves(game_state)
        best_move = None

        if maximizing:
            value = float('-inf')
            for move in valid_moves:
                new_state = copy.deepcopy(game_state)
                self.make_move(new_state, move, suppress_output=True, simulate=True)
                _, score = self.minimax(new_state, depth - 1, False, alpha, beta, start_time, time_limit, current_depth + 1)
                if score > value:
                    value = score
                    best_move = move
                if self.use_alpha_beta:
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break
            return best_move, value
        else:
            value = float('inf')
            for move in valid_moves:
                new_state = copy.deepcopy(game_state)
                self.make_move(new_state, move, suppress_output=True, simulate=True)
                _, score = self.minimax(new_state, depth - 1, True, alpha, beta, start_time, time_limit, current_depth + 1)
                if score < value:
                    value = score
                    best_move = move
                if self.use_alpha_beta:
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
            return best_move, value

    def ai_move(self, game_state):
        """
        Determine the best move for the AI using iterative deepening with minimax.
        Returns (best_move, best_score, move_time).
        """
        start_time = time.time()
        time_limit = self.timeout
        current_player = game_state["turn"]
        maximizing = True if current_player == 'white' else False

        best_move = None
        best_score = None
        depth = 1

        while True:
            if time.time() - start_time > time_limit:
                break
            move, score = self.minimax(game_state, depth, maximizing, float('-inf'), float('inf'), start_time, time_limit)
            if move is not None:
                best_move = move
                best_score = score
            depth += 1
            if depth > 5:
                break

        move_time = time.time() - start_time
        return best_move, best_score, move_time

    def make_move(self, game_state, move, suppress_output=False, simulate=False):
        """
        Execute the move, update the board, handle captures and pawn promotions,
        and switch turns.
        If simulate is True, do not update global win_flag.
        If suppress_output is True, do not print output.
        Returns a flag indicating if pawn promotion occurred.
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        board = game_state["board"]
        piece = board[start_row][start_col]
        captured = False

        if board[end_row][end_col] != '.':
            captured_piece = board[end_row][end_col]
            if not suppress_output:
                self.print_game(f"Captured {captured_piece}!")
            captured = True
            # Only update win_flag if this is a real move (not a simulation).
            if not simulate and captured_piece[1] == 'K':
                if not suppress_output:
                    self.print_game(f"{game_state['turn'].capitalize()} wins in turn {self.current_turn + 1}!")
                self.win_flag = True

        board[start_row][start_col] = '.'
        promotion = False
        if piece[1] == 'p' and ((game_state["turn"] == 'white' and end_row == 0) or
                                (game_state["turn"] == 'black' and end_row == self.BOARD_SIZE - 1)):
            piece = piece[0] + 'Q'
            promotion = True

        board[end_row][end_col] = piece
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

        if captured:
            self.half_moves_since_capture = 0
        else:
            self.half_moves_since_capture += 1

        return promotion

    def generate_game_trace(self):
        """
        Generate the game trace file with game parameters and move-by-move log.
        Filename format: gameTrace-<b>-<t>-<m>.txt where b is 'true' if alpha-beta is active.
        """
        alpha_beta_flag = "true" if self.use_alpha_beta else "false"
        filename = f"gameTrace-{alpha_beta_flag}-{self.timeout}-{self.MAX_TURNS}.txt"
        try:
            with open(filename, 'w') as f:
                f.write("Game Parameters:\n")
                f.write(f"    Timeout: {self.timeout} seconds\n")
                f.write(f"    Maximum Turns: {self.MAX_TURNS}\n")
                f.write(f"    Player 1 (white): {self.player_types['white']}\n")
                f.write(f"    Player 2 (black): {self.player_types['black']}\n")
                f.write(f"    Alpha-Beta: {alpha_beta_flag}\n")
                f.write(f"    Heuristic: {self.heuristic_choice}\n\n")
                f.write("Game Trace:\n")
                f.write(self.file_output)
            self.print_game(f"\nGame Trace generated: {filename}")
        except IOError:
            self.print_game("Error: Unable to write game trace.")

    def play(self):
        """Main game loop supporting human and AI moves."""
        self.print_game("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
        self.print_game("\nGame Parameters:")
        self.print_game(f"    Timeout: {self.timeout} seconds")
        self.print_game(f"    Maximum Turns: {self.MAX_TURNS}")
        self.print_game(f"    Play Mode: {self.play_mode}")
        self.print_game(f"    Player 1 (white): {self.player_types['white']}")
        self.print_game(f"    Player 2 (black): {self.player_types['black']}")
        self.print_game(f"    Alpha-Beta: {self.use_alpha_beta}")
        self.print_game(f"    Heuristic: {self.heuristic_choice}")
        self.print_game("\nInitial Board:")
        self.display_board(self.current_game_state)

        while True:
            self.print_game(f"\nTurn {self.current_turn + 1}")
            self.display_board(self.current_game_state)

            current_player = self.current_game_state["turn"]
            if self.player_types[current_player] == "human":
                move_input = input(f"{current_player.capitalize()} to move: ").strip()
                if move_input.lower() == 'exit':
                    self.print_game("Game exited by user.")
                    break
                move_coords = self.parse_input(move_input)
                valid, error_msg = self.validate_move(self.current_game_state, move_coords)
                if not valid:
                    self.print_game("Invalid move. " + error_msg + " Try again.")
                    continue
                chosen_move = move_coords
                move_time = None
                start_coord, end_coord = move_coords
                self.print_game(f"{current_player.capitalize()} move: from {self.convert_coordinate(start_coord)} to {self.convert_coordinate(end_coord)}")
            else:
                self.print_game(f"{current_player.capitalize()} (AI) is thinking...")
                chosen_move, ai_score, move_time = self.ai_move(self.current_game_state)
                if chosen_move is None:
                    self.print_game("AI could not find a valid move. Game over.")
                    break
                start_coord, end_coord = chosen_move
                self.print_game(f"{current_player.capitalize()} (AI) move: from {self.convert_coordinate(start_coord)} to {self.convert_coordinate(end_coord)}")
                self.print_game(f"Time for this action: {move_time:.2f} sec")
                self.print_game(f"Minimax/Alpha-Beta search score: {ai_score}")

            self.current_turn += 1
            promotion = self.make_move(self.current_game_state, chosen_move)
            if promotion:
                self.print_game(f"Pawn promoted to Queen at {self.convert_coordinate(end_coord)}!")

            if self.player_types[current_player] == "ai":
                post_move_eval = self.evaluate_board(self.current_game_state)
                self.print_game(f"Heuristic score of the resulting board: {post_move_eval}")

            if self.win_flag:
                self.print_game("Final Board:")
                self.display_board(self.current_game_state)
                self.generate_game_trace()
                break

            if self.current_turn >= self.MAX_TURNS:
                self.print_game("Maximum number of moves reached. Game is a draw.")
                self.generate_game_trace()
                break

            if self.half_moves_since_capture >= self.MOVES_FOR_DRAW:
                self.print_game("No captures in 10 full turns (20 moves). Game is a draw.")
                self.generate_game_trace()
                break

if __name__ == "__main__":
    game = MiniChess()
    print("Select play mode:")
    print("1: Human vs Human")
    print("2: Human vs AI")
    print("3: AI vs AI")
    mode_choice = input("Enter 1, 2, or 3: ").strip()

    if mode_choice == "1":
        game.play_mode = "H-H"
        game.player_types = {"white": "human", "black": "human"}
    elif mode_choice == "2":
        game.play_mode = "H-AI"
        side_choice = input("Do you want to play as White (W) or Black (B)? ").strip().lower()
        if side_choice in ["w", "white"]:
            game.player_types = {"white": "human", "black": "ai"}
        else:
            game.player_types = {"white": "ai", "black": "human"}
    elif mode_choice == "3":
        game.play_mode = "AI-AI"
        game.player_types = {"white": "ai", "black": "ai"}
    else:
        print("Invalid selection. Defaulting to Human vs Human.")
        game.play_mode = "H-H"
        game.player_types = {"white": "human", "black": "human"}

    ab_choice = input("Use alpha-beta pruning? (y/n): ").strip().lower()
    game.use_alpha_beta = True if ab_choice in ["y", "yes"] else False

    heuristic_choice = input("Select heuristic (e0, e1, or e2): ").strip().lower()
    if heuristic_choice in ["e0", "e1", "e2"]:
        game.heuristic_choice = heuristic_choice
    else:
        game.heuristic_choice = "e0"

    game.play()
