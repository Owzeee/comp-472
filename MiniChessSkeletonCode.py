import copy

class MiniChess:
    def __init__(self):
        # Initialize the game state and configuration parameters
        self.current_game_state = self.init_board()
        self.currentTurn = 0                # Counts each move (each player's turn)
        self.turnsSinceCapture = 0          # Counts consecutive turns with no capture (for draw condition)
        self.winFlag = False                # Flag to indicate if a win has occurred
        self.fileOutput = ""                # String to capture all output for the game trace
        self.maxTurns = 100                 # Maximum number of turns allowed (game ends in a draw if reached)
        self.timeout = 5                    # Timeout for each move (hardcoded for H-H; not used in H-H mode)
        self.playMode = "H-H"               # Play mode: Human vs Human

    def printG(self, output):
        """
        Capture outputs for gameTrace and also print to the console.
        """
        self.fileOutput += output + "\n"
        print(output)    

    def init_board(self):
        """
        Initialize the board with the starting configuration.
        Board layout:
            Row 5: bK, bQ, bB, bN, .
            Row 4: ., ., bp, bp, .
            Row 3: ., ., ., ., .
            Row 2: ., wp, wp, ., .
            Row 1: ., wN, wB, wQ, wK
        """
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
        """
        Prints the current board state in a text-based format.
        """
        self.printG("")
        # Print rows in reverse order (row 5 at the top, row 1 at the bottom)
        for i, row in enumerate(game_state["board"], start=1):
            self.printG(str(6 - i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        self.printG("\n     A   B   C   D   E\n")

    def is_valid_move(self, game_state, move):
        """
        Check if the move is valid according to Mini Chess rules.
        It verifies:
          - The move's start and end coordinates are within bounds.
          - The starting square is not empty.
          - The player is moving their own piece.
          - The destination square is not occupied by the player's own piece.
          - The move conforms to piece-specific movement rules.
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        board = game_state["board"]
        
        # Check if start position is within board bounds
        if not (0 <= start_row < 5 and 0 <= start_col < 5):
            return False
        
        # Check if end position is within board bounds
        if not (0 <= end_row < 5 and 0 <= end_col < 5):
            return False
        
        piece = board[start_row][start_col]

        # Prevent moving an empty square
        if piece == '.':
            return False  

        # Prevent moving the opponent's piece
        if (game_state["turn"] == 'white' and 'b' in piece) or (game_state["turn"] == 'black' and 'w' in piece):
            return False  

        # Prevent capturing one's own piece
        if board[end_row][end_col] != '.' and board[end_row][end_col][0] == piece[0]:
            return False  

        piece_type = piece[1]

        # Movement validation based on the piece type
        if piece_type == 'K':  # King moves one step in any direction
            return abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1
        elif piece_type == 'Q':  # Queen moves either linearly or diagonally
            return self.is_valid_linear_move(board, start, end) or self.is_valid_diagonal_move(board, start, end)
        elif piece_type == 'B':  # Bishop moves diagonally
            return self.is_valid_diagonal_move(board, start, end)
        elif piece_type == 'N':  # Knight moves in an L-shape
            return (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]
        elif piece_type == 'p':  # Pawn movement: one square forward or diagonal capture
            direction = -1 if game_state["turn"] == 'white' else 1
            # Pawn forward move (non-capturing)
            if start_col == end_col and board[end_row][end_col] == '.':  
                return end_row == start_row + direction
            # Pawn capturing move (diagonally)
            elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
                return board[end_row][end_col] != '.' and board[end_row][end_col][0] != piece[0]
        return False  

    def is_valid_linear_move(self, board, start, end):
        """
        Checks if a linear (horizontal or vertical) move is valid by ensuring no obstacles are in the path.
        """
        start_row, start_col = start
        end_row, end_col = end

        if start_row == end_row or start_col == end_col:
            row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)
            current_row, current_col = start_row + row_step, start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if board[current_row][current_col] != '.':
                    return False  # The path is blocked.
                current_row += row_step
                current_col += col_step
            return True
        return False

    def is_valid_diagonal_move(self, board, start, end):
        """
        Checks if a diagonal move is valid by ensuring no obstacles are in the diagonal path.
        """
        start_row, start_col = start
        end_row, end_col = end

        if abs(start_row - end_row) == abs(start_col - end_col):
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            current_row, current_col = start_row + row_step, start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if board[current_row][current_col] != '.':
                    return False  # The path is blocked.
                current_row += row_step
                current_col += col_step
            return True
        return False

    def make_move(self, game_state, move):
        """
        Updates the board by making the given move.
          - Handles piece movement.
          - Performs captures and prints a message.
          - Declares win if a king is captured.
          - Handles pawn promotion.
          - Updates the capture counter.
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        board = game_state["board"]
        piece = board[start_row][start_col]
        captured = False  # Flag to track if a capture occurred during this move.

        # Handle capturing if the destination square is occupied.
        if board[end_row][end_col] != '.':
            self.printG(f"Captured {board[end_row][end_col]}!")
            captured = True
            # Check if the captured piece is a king.
            if board[end_row][end_col][1] == 'K':
                self.printG(f"{game_state['turn'].capitalize()} wins in {self.currentTurn + 1} turns!")
                self.winFlag = True

        # Move the piece from the source to the destination.
        board[start_row][start_col] = '.'
        
        # Pawn promotion: if a pawn reaches the far end, promote it to a queen.
        if piece[1] == 'p' and (end_row == 0 or end_row == 4):
            piece = piece[0] + 'Q'
        
        board[end_row][end_col] = piece
        # Switch turn to the other player if the game has not ended.
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"
        
        # Update capture counter: reset if a capture occurred, else increment.
        if captured:
            self.turnsSinceCapture = 0
        else:
            self.turnsSinceCapture += 1

        return game_state

    def parse_input(self, move):
        """
        Parses the input string (e.g., "B2 B3") into board coordinates.
        Includes additional bounds checking to ensure valid positions (A-E, 1-5).
        Returns:
            A tuple of coordinates: ((start_row, start_col), (end_row, end_col))
            or None if the input is malformed or out of bounds.
        """
        try:
            start, end = move.split()
            # Validate the length and content for start coordinate.
            if len(start) != 2 or len(end) != 2:
                return None
            start_letter = start[0].upper()
            start_digit = start[1]
            if start_letter < 'A' or start_letter > 'E' or not start_digit.isdigit() or not (1 <= int(start_digit) <= 5):
                return None
            # Validate the end coordinate.
            end_letter = end[0].upper()
            end_digit = end[1]
            if end_letter < 'A' or end_letter > 'E' or not end_digit.isdigit() or not (1 <= int(end_digit) <= 5):
                return None

            # Convert the input (e.g., "B2") into board indices.
            start_coord = (5 - int(start_digit), ord(start_letter) - ord('A'))
            end_coord = (5 - int(end_digit), ord(end_letter) - ord('A'))
            return start_coord, end_coord
        except Exception as e:
            return None

    def gameTrace(self):
        """
        Generates the game trace file.
        The trace file includes game parameters (timeout, max turns, play mode, etc.)
        and a move-by-move log of the game.
        The file name follows the format: gameTrace-false-<timeout>-<maxTurns>.txt
        """
        filename = f"gameTrace-false-{self.timeout}-{self.maxTurns}.txt"
        with open(filename, 'w') as f:
            f.write("Game Parameters:\n")
            f.write(f"    Timeout: {self.timeout} seconds\n")
            f.write(f"    Maximum Turns: {self.maxTurns}\n")
            f.write(f"    Play Mode: {self.playMode}\n")
            f.write("    Search Algorithm: None (Human vs Human)\n")
            f.write("\nGame Trace:\n")
            f.write(self.fileOutput)
        print(f"\nGame Trace generated: {filename}")

    def play(self):
        """
        Main game loop.
          - Displays the board.
          - Prompts for moves.
          - Checks for invalid moves.
          - Increments the turn counter.
          - Checks for win condition (king captured).
          - Checks for draw conditions:
                a) Maximum number of turns reached.
                b) No capture for 10 consecutive turns.
          - Writes the game trace to a file when the game ends.
        """
        self.printG("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
        
        # Print initial game parameters and board configuration in the trace.
        self.printG("Game Parameters:")
        self.printG(f"    Timeout: {self.timeout} seconds")
        self.printG(f"    Maximum Turns: {self.maxTurns}")
        self.printG(f"    Play Mode: {self.playMode}")
        self.printG("    Search Algorithm: None (Human vs Human)")
        self.printG("\nInitial Board:")
        self.display_board(self.current_game_state)
        
        while True:
            self.printG(f"Turn {self.currentTurn + 1}")
            self.display_board(self.current_game_state)

            move = input(f"{self.current_game_state['turn'].capitalize()} to move: ")
            if move.lower() == 'exit':
                self.printG("Game exited by user.")
                break

            move_coords = self.parse_input(move)
            if not move_coords or not self.is_valid_move(self.current_game_state, move_coords):
                self.printG("Invalid move. Try again.")
                continue  

            # Increment turn count after a valid move.
            self.currentTurn += 1
            self.current_game_state = self.make_move(self.current_game_state, move_coords)

            # Check for win condition: if a king was captured.
            if self.winFlag:
                self.printG("Final Board:")
                self.display_board(self.current_game_state)
                self.gameTrace()
                break

            # Draw condition: Maximum number of turns reached.
            if self.currentTurn >= self.maxTurns:
                self.printG("Maximum number of turns reached. Game is a draw.")
                self.gameTrace()
                break

            # Draw condition: No capture in 10 consecutive turns.
            if self.turnsSinceCapture >= 10:
                self.printG("No captures in 10 consecutive turns. Game is a draw.")
                self.gameTrace()
                break

if __name__ == "__main__":
    game = MiniChess()
    game.play()

