import streamlit as st
import copy

class ChessPiece:
    def __init__(self, color, piece_type, position):
        self.color = color
        self.piece_type = piece_type
        self.position = position
        self.has_moved = False
    
    def __str__(self):
        symbols = {
            'white': {'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'},
            'black': {'king': '♚', 'queen': '♛', 'rook': '♜', 'bishop': '♝', 'knight': '♞', 'pawn': '♟'}
        }
        return symbols[self.color][self.piece_type]

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.selected_square = None
        self.legal_moves_for_selected = []
        self.setup_initial_position()
    
    def setup_initial_position(self):
        # Set up pawns
        for col in range(8):
            self.board[1][col] = ChessPiece('black', 'pawn', (1, col))
            self.board[6][col] = ChessPiece('white', 'pawn', (6, col))
        
        # Set up other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        
        for col in range(8):
            self.board[0][col] = ChessPiece('black', piece_order[col], (0, col))
            self.board[7][col] = ChessPiece('white', piece_order[col], (7, col))
    
    def get_piece_at(self, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return self.board[row][col]
        return None
    
    def is_valid_move(self, start_row, start_col, end_row, end_col):
        piece = self.get_piece_at(start_row, start_col)
        target = self.get_piece_at(end_row, end_col)
        
        if not piece or piece.color != self.current_player:
            return False
        
        if target and target.color == piece.color:
            return False
        
        if not self.is_legal_piece_move(piece, start_row, start_col, end_row, end_col):
            return False
        
        if self.would_be_in_check_after_move(start_row, start_col, end_row, end_col):
            return False
        
        return True
    
    def is_legal_piece_move(self, piece, start_row, start_col, end_row, end_col):
        row_diff = end_row - start_row
        col_diff = end_col - start_col
        
        if piece.piece_type == 'pawn':
            return self.is_legal_pawn_move(piece, row_diff, col_diff, end_row, end_col)
        elif piece.piece_type == 'rook':
            return self.is_legal_rook_move(row_diff, col_diff, start_row, start_col, end_row, end_col)
        elif piece.piece_type == 'knight':
            return abs(row_diff) == 2 and abs(col_diff) == 1 or abs(row_diff) == 1 and abs(col_diff) == 2
        elif piece.piece_type == 'bishop':
            return self.is_legal_bishop_move(row_diff, col_diff, start_row, start_col, end_row, end_col)
        elif piece.piece_type == 'queen':
            return (self.is_legal_rook_move(row_diff, col_diff, start_row, start_col, end_row, end_col) or
                    self.is_legal_bishop_move(row_diff, col_diff, start_row, start_col, end_row, end_col))
        elif piece.piece_type == 'king':
            return abs(row_diff) <= 1 and abs(col_diff) <= 1
        
        return False
    
    def is_legal_pawn_move(self, piece, row_diff, col_diff, end_row, end_col):
        direction = -1 if piece.color == 'white' else 1
        target = self.get_piece_at(end_row, end_col)
        
        if col_diff == 0:
            if row_diff == direction and not target:
                return True
            if (row_diff == 2 * direction and not piece.has_moved and 
                not target and not self.get_piece_at(end_row - direction, end_col)):
                return True
        elif abs(col_diff) == 1 and row_diff == direction and target:
            return True
        
        return False
    
    def is_legal_rook_move(self, row_diff, col_diff, start_row, start_col, end_row, end_col):
        if row_diff != 0 and col_diff != 0:
            return False
        return self.is_path_clear(start_row, start_col, end_row, end_col)
    
    def is_legal_bishop_move(self, row_diff, col_diff, start_row, start_col, end_row, end_col):
        if abs(row_diff) != abs(col_diff):
            return False
        return self.is_path_clear(start_row, start_col, end_row, end_col)
    
    def is_path_clear(self, start_row, start_col, end_row, end_col):
        row_direction = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_direction = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        
        current_row = start_row + row_direction
        current_col = start_col + col_direction
        
        while current_row != end_row or current_col != end_col:
            if self.get_piece_at(current_row, current_col):
                return False
            current_row += row_direction
            current_col += col_direction
        
        return True
    
    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    return (row, col)
        return None
    
    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self.is_legal_piece_move(piece, row, col, king_row, king_col):
                        return True
        
        return False
    
    def would_be_in_check_after_move(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]
        
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = piece
        piece.position = (end_row, end_col)
        
        in_check = self.is_in_check(piece.color)
        
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = captured_piece
        piece.position = (start_row, start_col)
        
        return in_check
    
    def get_legal_moves_for_piece(self, row, col):
        piece = self.get_piece_at(row, col)
        if not piece or piece.color != self.current_player:
            return []
        
        legal_moves = []
        for end_row in range(8):
            for end_col in range(8):
                if self.is_valid_move(row, col, end_row, end_col):
                    legal_moves.append((end_row, end_col))
        
        return legal_moves
    
    def get_all_legal_moves(self, color):
        legal_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.is_valid_move(row, col, end_row, end_col):
                                legal_moves.append(((row, col), (end_row, end_col)))
        return legal_moves
    
    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        return len(self.get_all_legal_moves(color)) == 0
    
    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        return len(self.get_all_legal_moves(color)) == 0
    
    def make_move(self, start_row, start_col, end_row, end_col):
        if not self.is_valid_move(start_row, start_col, end_row, end_col):
            return False
        
        piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]
        
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = piece
        piece.position = (end_row, end_col)
        piece.has_moved = True
        
        self.move_history.append(((start_row, start_col), (end_row, end_col), captured_piece))
        
        # Pawn promotion
        if piece.piece_type == 'pawn' and (end_row == 0 or end_row == 7):
            piece.piece_type = 'queen'
        
        # Clear selection
        self.selected_square = None
        self.legal_moves_for_selected = []
        
        # Switch players
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        # Check game end conditions
        if self.is_checkmate(self.current_player):
            self.game_over = True
            self.winner = 'black' if self.current_player == 'white' else 'white'
        elif self.is_stalemate(self.current_player):
            self.game_over = True
            self.winner = 'draw'
        
        return True
    
    def select_square(self, row, col):
        piece = self.get_piece_at(row, col)
        
        # If there's already a selection and we click on a legal move, make the move
        if self.selected_square and (row, col) in self.legal_moves_for_selected:
            start_row, start_col = self.selected_square
            self.make_move(start_row, start_col, row, col)
            return True
        
        # Select new piece if it belongs to current player
        if piece and piece.color == self.current_player:
            self.selected_square = (row, col)
            self.legal_moves_for_selected = self.get_legal_moves_for_piece(row, col)
            return False
        
        # Deselect if clicking on empty square or opponent piece with no selection
        self.selected_square = None
        self.legal_moves_for_selected = []
        return False

def initialize_game():
    if 'chess_board' not in st.session_state:
        st.session_state.chess_board = ChessBoard()
        st.session_state.move_made = False

def get_square_color(row, col, board):
    # Base square color
    is_light = (row + col) % 2 == 0
    base_color = "#F0D9B5" if is_light else "#B58863"
    
    # Selected square
    if board.selected_square == (row, col):
        return "#FFD700"  # Gold
    
    # Legal move squares
    if (row, col) in board.legal_moves_for_selected:
        return "#90EE90"  # Light green
    
    # King in check
    piece = board.get_piece_at(row, col)
    if piece and piece.piece_type == 'king' and board.is_in_check(piece.color):
        return "#FF6B6B"  # Light red
    
    return base_color

def display_board():
    board = st.session_state.chess_board
    
    # Create the board
    for row in range(8):
        cols = st.columns(8)
        for col in range(8):
            with cols[col]:
                piece = board.get_piece_at(row, col)
                square_color = get_square_color(row, col, board)
                
                # Create button for each square
                piece_text = str(piece) if piece else "　"  # Wide space for empty squares
                
                if st.button(
                    piece_text,
                    key=f"square_{row}_{col}",
                    help=f"{chr(ord('a') + col)}{8 - row}",
                    use_container_width=True
                ):
                    move_made = board.select_square(row, col)
                    if move_made:
                        st.session_state.move_made = True
                        st.rerun()
                
                # Style the button with CSS
                st.markdown(f"""
                <style>
                div[data-testid="column"]:nth-child({col + 1}) button[data-testid="baseButton-secondary"] {{
                    background-color: {square_color} !important;
                    border: 2px solid #8B4513 !important;
                    height: 60px !important;
                    font-size: 32px !important;
                    padding: 0 !important;
                    margin: 1px !important;
                }}
                div[data-testid="column"]:nth-child({col + 1}) button[data-testid="baseButton-secondary"]:hover {{
                    background-color: {square_color} !important;
                    border: 3px solid #654321 !important;
                    transform: scale(1.05) !important;
                }}
                </style>
                """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Streamlit Chess Game",
        page_icon="♔",
        layout="wide"
    )
    
    st.title("♔ Chess Game ♛")
    
    initialize_game()
    board = st.session_state.chess_board
    
    # Sidebar with game info
    with st.sidebar:
        st.header("Game Status")
        
        if board.game_over:
            if board.winner == 'draw':
                st.success("Game Over: Draw (Stalemate)")
            else:
                st.success(f"Game Over: {board.winner.title()} Wins!")
        else:
            st.info(f"Current Player: {board.current_player.title()}")
            
            if board.is_in_check(board.current_player):
                st.warning(f"{board.current_player.title()} is in Check!")
        
        # Game controls
        st.header("Game Controls")
        
        if st.button("New Game", use_container_width=True):
            st.session_state.chess_board = ChessBoard()
            st.rerun()
        
        if st.button("Undo Last Move", use_container_width=True, disabled=len(board.move_history) == 0):
            if board.move_history:
                # Simple undo - just reinitialize and replay all but last move
                last_moves = board.move_history[:-1]
                st.session_state.chess_board = ChessBoard()
                new_board = st.session_state.chess_board
                
                for (start_pos, end_pos, captured) in last_moves:
                    new_board.make_move(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                
                st.rerun()
        
        # Game statistics
        st.header("Game Statistics")
        st.write(f"Moves played: {len(board.move_history)}")
        
        if board.move_history:
            st.subheader("Recent Moves")
            for i, ((start_row, start_col), (end_row, end_col), captured) in enumerate(board.move_history[-5:]):
                start_square = f"{chr(ord('a') + start_col)}{8 - start_row}"
                end_square = f"{chr(ord('a') + end_col)}{8 - end_row}"
                move_text = f"{start_square} → {end_square}"
                if captured:
                    move_text += f" (captured {captured})"
                st.text(f"{len(board.move_history) - 4 + i}: {move_text}")
    
    # Main board area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Chess Board")
        
        # Coordinate labels
        st.markdown("""
        <div style='text-align: center; margin-bottom: 10px;'>
            <span style='margin-left: 30px;'>a　　b　　c　　d　　e　　f　　g　　h</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Display the board
        display_board()
        
        # Bottom coordinate labels
        st.markdown("""
        <div style='text-align: center; margin-top: 10px;'>
            <span style='margin-left: 30px;'>a　　b　　c　　d　　e　　f　　g　　h</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Instructions
    with col1:
        st.subheader("How to Play")
        st.markdown("""
        1. **Click** on a piece to select it
        2. **Click** on a highlighted square to move
        3. **Gold** square shows your selection
        4. **Green** squares show legal moves
        5. **Red** square shows king in check
        
        **Piece Symbols:**
        - ♔♕♖♗♘♙ White pieces
        - ♚♛♜♝♞♟ Black pieces
        """)
    
    with col3:
        if board.selected_square:
            piece = board.get_piece_at(*board.selected_square)
            if piece:
                st.subheader("Selected Piece")
                st.write(f"**Type:** {piece.piece_type.title()}")
                st.write(f"**Color:** {piece.color.title()}")
                st.write(f"**Position:** {chr(ord('a') + board.selected_square[1])}{8 - board.selected_square[0]}")
                st.write(f"**Legal Moves:** {len(board.legal_moves_for_selected)}")
        
        # Show legal moves count for current player
        total_legal_moves = len(board.get_all_legal_moves(board.current_player))
        st.subheader("Game Analysis")
        st.write(f"**Total Legal Moves:** {total_legal_moves}")
        
        if total_legal_moves == 0 and not board.game_over:
            st.error("No legal moves available!")

if __name__ == "__main__":
    main()