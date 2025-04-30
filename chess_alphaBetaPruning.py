import chess
import chess.svg
import cairosvg
import imageio
import io

# Piece-square tables (simplified for positional evaluation)
piece_square_tables = {
    chess.PAWN: [0, 5, 5, -10, -10, 5, 10, 0] * 8,
    chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50] * 8,
    chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20] * 8,
    chess.ROOK: [0, 0, 5, 10, 10, 5, 0, 0] * 8,
    chess.QUEEN: [-20, -10, -10, 0, 0, -10, -10, -20] * 8,
    chess.KING: [-30, -40, -40, -50, -50, -40, -40, -30] * 8
}

def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    material_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    score = 0
    for piece in material_values:
        for square in board.pieces(piece, chess.WHITE):
            score += material_values[piece]
            score += piece_square_tables[piece][square]
        for square in board.pieces(piece, chess.BLACK):
            score -= material_values[piece]
            score -= piece_square_tables[piece][chess.square_mirror(square)]
    return score

# Move ordering: prioritize captures and checks
def ordered_moves(board):
    return sorted(
        board.legal_moves,
        key=lambda move: board.is_capture(move) or board.gives_check(move),
        reverse=True
    )

# Alpha-beta with quiescence
def alpha_beta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return quiescence(board, alpha, beta), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in ordered_moves(board):
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
        for move in ordered_moves(board):
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

# Quiescence search: extend leaf evaluation to avoid unstable evals
def quiescence(board, alpha, beta):
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    return alpha

# Play game to video
def play_game_to_video(depth=3, filename="chess_alpha_beta.mp4"):
    board = chess.Board()
    writer = imageio.get_writer(filename, fps=1)
    move_count = 0

    while not board.is_game_over() and move_count < 150:
        print(board, "\n")

        maximizing = board.turn
        _, move = alpha_beta(board, depth, float('-inf'), float('inf'), maximizing)

        if move is None:
            break
        board.push(move)

        svg = chess.svg.board(board=board, lastmove=move, size=500)
        png = cairosvg.svg2png(bytestring=svg)
        img = imageio.v2.imread(io.BytesIO(png))
        writer.append_data(img)

        move_count += 1

    writer.close()
    print("Game Over:", board.result())
    print("Video saved to:", filename)

# Run
play_game_to_video(depth=2, filename="chess_alpha_beta.mp4")
