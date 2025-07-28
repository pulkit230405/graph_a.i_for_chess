import chess
import chess.polyglot

transposition_table = {}

PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
}

# === MODIFIED: Renamed KING_PST and added KING_PST_ENDGAME ===
PAWN_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]
KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,-40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,-30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,-30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,-10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,-10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,-10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,-20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_PST = [
     0,  0,  0,  0,  0,  0,  0,  0,  5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,-5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,-5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5, 0,  0,  0,  5,  5,  0,  0,  0
]
QUEEN_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,-10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10, -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,-10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,-20,-10,-10, -5, -5,-10,-10,-20
]
KING_PST_MIDDLEGAME = [
    -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20, 20, 30, 10,  0,  0, 10, 30, 20
]
KING_PST_ENDGAME = [
    -50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,-30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,-30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50,
]

PST = {
    chess.PAWN: PAWN_PST, chess.KNIGHT: KNIGHT_PST, chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST, chess.QUEEN: QUEEN_PST,
    # King now has two tables
    'KING_MG': KING_PST_MIDDLEGAME, 'KING_EG': KING_PST_ENDGAME
}

# === NEW: Function to determine the game phase ===
def get_game_phase(board: chess.Board) -> str:
    """Determines if the game is in middlegame or endgame."""
    # Count the value of major and minor pieces on the board
    material_count = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type not in [chess.PAWN, chess.KING]:
            material_count += PIECE_VALUES.get(piece.piece_type, 0)
    
    # A simple threshold to define endgame
    if material_count < 2000: # Less than 2 rooks + 2 minor pieces
        return "EG" # Endgame
    else:
        return "MG" # Middlegame

# === MODIFIED: calculate_pst_score is now game-phase aware ===
def calculate_pst_score(board: chess.Board, color: chess.Color) -> int:
    score = 0
    game_phase = get_game_phase(board)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            pst_table = None
            if piece.piece_type == chess.KING:
                # Choose the correct King PST based on game phase
                pst_table = PST[f'KING_{game_phase}']
            else:
                pst_table = PST.get(piece.piece_type)
            
            if pst_table:
                if color == chess.BLACK:
                    square = chess.square_mirror(square)
                score += pst_table[square]
    return score

# ... (all other functions like calculate_material, mobility, etc. remain the same) ...

# NOTE: The rest of your graph_ai.py file does not need to be changed.
# The evaluate_board function will automatically use the updated calculate_pst_score.
# I am including the full file below for completeness.

def calculate_material_score(board: chess.Board, color: chess.Color) -> int:
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            score += PIECE_VALUES.get(piece.piece_type, 0)
    return score

def calculate_mobility_score(board: chess.Board, color: chess.Color) -> int:
    original_turn = board.turn
    board.turn = color
    mobility = board.legal_moves.count()
    board.turn = original_turn
    return mobility

def calculate_center_control_score(board: chess.Board, color: chess.Color) -> int:
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    control_score = 0
    for square in center_squares:
        if board.is_attacked_by(color, square):
            control_score += 1
    return control_score

def calculate_king_safety_score(board: chess.Board, color: chess.Color) -> int:
    king_square = board.king(color)
    if king_square is None: return 0
    king_zone = []
    for rank_offset in [-1, 0, 1]:
        for file_offset in [-1, 0, 1]:
            if rank_offset == 0 and file_offset == 0: continue
            square = king_square + (rank_offset * 8) + file_offset
            if 0 <= square < 64 and chess.square_file(square) == chess.square_file(king_square) + file_offset:
                king_zone.append(square)
    opponent_color = not color
    attack_score = 0
    for square in king_zone:
        attack_score += len(board.attackers(opponent_color, square))
    return attack_score
# In graph_ai.py

def calculate_doubled_pawn_penalty(board: chess.Board, color: chess.Color) -> int:
    """Calculates the penalty for doubled pawns."""
    penalty = 0
    pawn_char = 'P' if color == chess.WHITE else 'p'
    
    for file_index in range(8): # Iterate through files a-h
        pawn_count = 0
        for rank_index in range(8): # Iterate through ranks 1-8
            square = chess.square(file_index, rank_index)
            piece = board.piece_at(square)
            if piece and piece.symbol() == pawn_char:
                pawn_count += 1
        if pawn_count > 1:
            penalty += (pawn_count - 1) * 20 # Penalty of -20 for each extra pawn
            
    return penalty

def calculate_isolated_pawn_penalty(board: chess.Board, color: chess.Color) -> int:
    """Calculates the penalty for isolated pawns."""
    penalty = 0
    pawn_char = 'P' if color == chess.WHITE else 'p'

    for file_index in range(8):
        for rank_index in range(8):
            square = chess.square(file_index, rank_index)
            piece = board.piece_at(square)

            if piece and piece.symbol() == pawn_char:
                # Check for friendly pawns on adjacent files
                is_isolated = True
                # Check left file
                if file_index > 0:
                    for r in range(8):
                        adj_square = chess.square(file_index - 1, r)
                        adj_piece = board.piece_at(adj_square)
                        if adj_piece and adj_piece.symbol() == pawn_char:
                            is_isolated = False
                            break
                if not is_isolated: continue

                # Check right file
                if file_index < 7:
                    for r in range(8):
                        adj_square = chess.square(file_index + 1, r)
                        adj_piece = board.piece_at(adj_square)
                        if adj_piece and adj_piece.symbol() == pawn_char:
                            is_isolated = False
                            break
                
                if is_isolated:
                    penalty += 15 # Penalty of -15 for each isolated pawn

    return penalty

# In graph_ai.py

def evaluate_board(board: chess.Board) -> int:
    if board.is_checkmate():
        return -float('inf') if board.outcome().winner != board.turn else float('inf')
    if board.is_game_over():
        return 0

    # Define all our weights
    w_mobility, w_control, w_king_safety = 5, 10, 15

    # Calculate base scores (positive is good)
    white_score = calculate_material_score(board, chess.WHITE) + calculate_pst_score(board, chess.WHITE)
    black_score = calculate_material_score(board, chess.BLACK) + calculate_pst_score(board, chess.BLACK)
    
    # Calculate penalties (higher number is worse)
    white_pawn_penalty = calculate_doubled_pawn_penalty(board, chess.WHITE) + calculate_isolated_pawn_penalty(board, chess.WHITE)
    black_pawn_penalty = calculate_doubled_pawn_penalty(board, chess.BLACK) + calculate_isolated_pawn_penalty(board, chess.BLACK)

    # Apply penalties
    white_score -= white_pawn_penalty
    black_score -= black_pawn_penalty
    
    # Calculate other graph metrics
    white_mobility = calculate_mobility_score(board, chess.WHITE)
    black_mobility = calculate_mobility_score(board, chess.BLACK)
    white_control = calculate_center_control_score(board, chess.WHITE)
    black_control = calculate_center_control_score(board, chess.BLACK)
    white_king_threat = calculate_king_safety_score(board, chess.WHITE)
    black_king_threat = calculate_king_safety_score(board, chess.BLACK)

    # Combine all evaluations
    material_eval = white_score - black_score
    mobility_eval = w_mobility * (white_mobility - black_mobility)
    control_eval = w_control * (white_control - black_control)
    safety_eval = w_king_safety * (black_king_threat - white_king_threat)
    
    total_eval = material_eval + mobility_eval + control_eval + safety_eval
    return total_eval if board.turn == chess.WHITE else -total_eval

def score_move(move: chess.Move, board: chess.Board) -> int:
    score = 0
    if move.promotion:
        score += PIECE_VALUES.get(move.promotion, 0)
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            score += 10 * PIECE_VALUES.get(victim.piece_type, 0) - PIECE_VALUES.get(attacker.piece_type, 0)
    return score

def find_best_move(board: chess.Board, depth: int) -> (chess.Move, list):
    global transposition_table
    transposition_table = {}
    best_move = None
    max_eval = -float('inf')
    alpha, beta = -float('inf'), float('inf')
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: score_move(move, board), reverse=True)
    move_evals = []
    for move in moves:
        board.push(move)
        eval = -alphabeta(board, depth - 1, -beta, -alpha)
        board.pop()
        move_evals.append((board.san(move), eval))
        if eval > max_eval:
            max_eval = eval
            best_move = move
            alpha = max(alpha, eval)
    move_evals.sort(key=lambda item: item[1], reverse=True)
    return best_move, move_evals[:5]

def alphabeta(board: chess.Board, depth: int, alpha: float, beta: float) -> float:
    original_alpha = alpha
    board_hash = chess.polyglot.zobrist_hash(board)
    if board_hash in transposition_table and transposition_table[board_hash]['depth'] >= depth:
        entry = transposition_table[board_hash]
        if entry['flag'] == 'EXACT':
            return entry['score']
        elif entry['flag'] == 'LOWERBOUND' and entry['score'] >= beta:
            return beta
        elif entry['flag'] == 'UPPERBOUND' and entry['score'] <= alpha:
            return alpha
    if depth == 0 or board.is_game_over():
        return quiescence_search(board, alpha, beta)
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: score_move(move, board), reverse=True)
    for move in moves:
        board.push(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha)
        board.pop()
        if score >= beta:
            transposition_table[board_hash] = {'score': beta, 'depth': depth, 'flag': 'LOWERBOUND'}
            return beta
        if score > alpha:
            alpha = score
    if alpha <= original_alpha:
        flag = 'UPPERBOUND'
    else:
        flag = 'EXACT'
    transposition_table[board_hash] = {'score': alpha, 'depth': depth, 'flag': flag}
    return alpha

def quiescence_search(board: chess.Board, alpha: float, beta: float) -> float:
    stand_pat_eval = evaluate_board(board)
    if stand_pat_eval >= beta:
        return beta
    if stand_pat_eval > alpha:
        alpha = stand_pat_eval
    capture_moves = [move for move in board.legal_moves if board.is_capture(move)]
    capture_moves.sort(key=lambda move: score_move(move, board), reverse=True)
    for move in capture_moves:
        board.push(move)
        score = -quiescence_search(board, -beta, -alpha)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha