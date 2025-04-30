import chess
import chess.svg
import cairosvg
import imageio
import io

# Enhanced evaluation with repetition penalty
def evaluate_board(board, history):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    # Penalize if board has repeated more than once
    repetition_penalty = -20 if history.count(board.fen()) >= 2 else 0

    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    score = 0
    for piece in values:
        score += len(board.pieces(piece, chess.WHITE)) * values[piece]
        score -= len(board.pieces(piece, chess.BLACK)) * values[piece]

    return score + repetition_penalty

# Alpha-beta with history to avoid repetition
def alpha_beta(board, depth, alpha, beta, maximizing, history):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board, history), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            history.append(board.fen())
            eval, _ = alpha_beta(board, depth - 1, alpha, beta, False, history)
            history.pop()
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
            history.append(board.fen())
            eval, _ = alpha_beta(board, depth - 1, alpha, beta, True, history)
            history.pop()
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Game play and video generation
def play_game_to_video(depth=3, filename="alphabeta_chess.mp4"):
    board = chess.Board()
    history = []
    seen_positions = {}

    writer = imageio.get_writer(filename, fps=1)

    move_limit = 150  # Stop if game drags too long
    moves_played = 0

    while not board.is_game_over() and moves_played < move_limit:
        print(board, "\n")

        maximizing = board.turn
        _, move = alpha_beta(board, depth, float('-inf'), float('inf'), maximizing, history)

        if move is None:
            break
        board.push(move)
        fen = board.fen()
        history.append(fen)
        seen_positions[fen] = seen_positions.get(fen, 0) + 1
        if seen_positions[fen] >= 3:
            print("Threefold repetition detected. Ending game.")
            break

        # Save frame
        svg = chess.svg.board(board=board)
        png = cairosvg.svg2png(bytestring=svg)
        img = imageio.v2.imread(io.BytesIO(png))
        writer.append_data(img)

        moves_played += 1

    writer.close()
    print("Game Over:", board.result())
    print("Video saved to:", filename)

# Run
play_game_to_video(depth=2, filename="chess_alphaBeta.mp4")
