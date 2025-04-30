import chess
import chess.svg
import cairosvg
import imageio
import io

# Evaluation function with position-based scoring
def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3.3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
    }
    score = 0
    for piece_type in values:
        score += len(board.pieces(piece_type, chess.WHITE)) * values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * values[piece_type]
    return score

# Minimax algorithm
def minimax(board, depth, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

# Generate video of game
def play_game_to_video(filename="chess_minimax.mp4", depth=3):
    board = chess.Board()
    writer = imageio.get_writer(filename, fps=1)

    while not board.is_game_over():
        _, move = minimax(board, depth, board.turn)

        if move is None:
            print("No move found by minimax, picking fallback.")
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            move = legal_moves[0]

        board.push(move)

        # Render frame
        svg_data = chess.svg.board(board=board)
        png_data = cairosvg.svg2png(bytestring=svg_data)
        img = imageio.v2.imread(io.BytesIO(png_data))
        writer.append_data(img)

    writer.close()
    print("Game over.")
    print("Reason:", board.result(), "-", board.outcome().termination.name)

# Run game
play_game_to_video("chess_minimax.mp4", depth=2)
