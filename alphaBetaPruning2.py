import chess

# Improved evaluation: includes checkmate/stalemate detection
def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn else 9999  # If it's checkmate, the player to move lost
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0  # Drawish positions

    # Material count
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    score = 0
    for piece_type in values:
        score += len(board.pieces(piece_type, chess.WHITE)) * values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * values[piece_type]
    return score

# Alpha-Beta Pruning with improved evaluation
def alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Play a game using alpha-beta
def play_game(depth=4):
    board = chess.Board()
    while not board.is_game_over():
        print(board, "\n")

        if board.turn == chess.WHITE:
            print("White is thinking...")
            _, move = alpha_beta(board, depth, float('-inf'), float('inf'), True)
        else:
            print("Black is thinking...")
            _, move = alpha_beta(board, depth, float('-inf'), float('inf'), False)

        print(f"Move played: {board.san(move)}\n")
        board.push(move)

    print("\nGame Over!")
    print("Result:", board.result())
    print("Final Board:\n", board)

play_game(depth=4)
