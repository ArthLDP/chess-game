import chess
import chess.pgn
import pygame
import os

# Screen dimensions
WIDTH = 700
HEIGHT = 500
DIMENSION = 8  # Chessboard is 8x8
SQ_SIZE = HEIGHT // DIMENSION  # Size of each square
FPS = 30  # Frames per second
IMAGES = {}  # Dictionary to hold loaded piece images
PROMOTION_OPTIONS = ['q', 'r', 'b', 'n']  # Promotion choices

def load_images():
    # Load and scale piece images from the assets folder
    pieces = ["wB", "wK", "wN", "wP", "wQ", "wR", "bB", "bK", "bN", "bP", "bQ", "bR"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load("assets/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )

def draw_board(screen):
    # Draw the chessboard squares
    colors = [pygame.Color("white"), pygame.Color("lightskyblue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board, flipped=False):
    # Draw pieces based on the current board state
    piece_to_image = {
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
    }
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            col = chess.square_file(square)
            row = chess.square_rank(square)
            if flipped:
                x = (7 - col) * SQ_SIZE
                y = row * SQ_SIZE
            else:
                x = col * SQ_SIZE
                y = (7 - row) * SQ_SIZE
            screen.blit(IMAGES[piece_to_image[symbol]], pygame.Rect(x, y, SQ_SIZE, SQ_SIZE))

def prompt_promotion(screen):
    # Show promotion choice overlay
    options = ['q', 'r', 'b', 'n']
    option_names = ['Queen', 'Rook', 'Bishop', 'Knight']
    font = pygame.font.SysFont("Arial", 24)
    rects = []
    for i, name in enumerate(option_names):
        rect = pygame.Rect(150, 100 + i * 60, 300, 50)
        rects.append(rect)
        pygame.draw.rect(screen, pygame.Color("Black"), rect)
        text = font.render(name, True, pygame.Color("white"))
        screen.blit(text, (rect.x + 10, rect.y + 10))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        return options[i]

def make_move(board, player_clicks, screen, flipped=False):
    # Attempt to make a move based on player clicks and handle promotion
    from_row, from_col = player_clicks[0]
    to_row, to_col = player_clicks[1]
    
    if flipped:
        from_square = chess.square(7 - from_col, from_row)
        to_square = chess.square(7 - to_col, to_row)
    else:
        from_square = chess.square(from_col, 7 - from_row)
        to_square = chess.square(to_col, 7 - to_row)

    move = chess.Move(from_square, to_square)

    if move in board.legal_moves:
        board.push(move)
        return True

    # Handle promotion
    # Check if it's a possible pawn promotion (only pawns moving to last rank)
    piece = board.piece_at(from_square)
    if piece and piece.piece_type == chess.PAWN:
        to_rank = chess.square_rank(to_square)
        if (piece.color == chess.WHITE and to_rank == 7) or (piece.color == chess.BLACK and to_rank == 0):
            promotion_test = chess.Move(from_square, to_square, promotion=chess.QUEEN) # Temp promotion to check if it's possible before triggering menu
            if promotion_test in board.legal_moves:
                choice = prompt_promotion(screen)
                promo_move = chess.Move(from_square, to_square, promotion=chess.Piece.from_symbol(choice).piece_type)
                board.push(promo_move)
                return True

    return False

def undo_move(board):
    # Undo the last move if possible
    if board.move_stack:
        board.pop()

def highlight_square(screen, sq_selected):
    # Highlight the selected square
    if sq_selected != ():
        row, col = sq_selected
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pygame.Color("red"))
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

def draw_legal_moves(screen, board, sq_selected, flipped=False):
    # Draw dots for all legal moves of the selected piece
    if sq_selected == ():
        return
    from_row, from_col = sq_selected
    
    if flipped:
        from_square = chess.square(7 - from_col, from_row)
    else:
        from_square = chess.square(from_col, 7 - from_row)
        
    for move in board.legal_moves:
        if move.from_square == from_square:
            to_col = chess.square_file(move.to_square)
            to_row = chess.square_rank(move.to_square)
            
            if flipped:
                center_x = (7 - to_col) * SQ_SIZE + SQ_SIZE // 2
                center_y = to_row * SQ_SIZE + SQ_SIZE // 2
            else:
                center_x = to_col * SQ_SIZE + SQ_SIZE // 2
                center_y = (7 - to_row) * SQ_SIZE + SQ_SIZE // 2
                
            radius = SQ_SIZE // 8
            pygame.draw.circle(screen, pygame.Color("red"), (center_x, center_y), radius)

def draw_game_over_overlay(screen, text):
    # Draw overlay and display game result text
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    font = pygame.font.SysFont("Arial", 30, bold=True)
    label = font.render(text, True, pygame.Color("white"))
    label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(label, label_rect)

def draw_move_log(screen, board, scroll_offset):
    # Draw the move log on the right panel with scroll offset
    font = pygame.font.SysFont("Arial", 20)
    log_x = 495
    padding = 5
    line_height = 20
    move_texts = []
    move_stack = board.move_stack
    temp_board = chess.Board()

    for i in range(0, len(move_stack), 2):
        move_str = f"{(i // 2) + 1}."
        move_str += f" {temp_board.san(move_stack[i])}"
        temp_board.push(move_stack[i])
        if i + 1 < len(move_stack):
            move_str += f" {temp_board.san(move_stack[i + 1])}"
            temp_board.push(move_stack[i + 1])
        move_texts.append(move_str)

    pygame.draw.rect(screen, pygame.Color("lightgray"), pygame.Rect(log_x, 0, WIDTH - log_x, HEIGHT))

    visible_lines = HEIGHT // line_height
    start = max(0, scroll_offset)
    end = min(start + visible_lines, len(move_texts))

    for i, text in enumerate(move_texts[start:end]):
        label = font.render(text, True, pygame.Color("black"))
        screen.blit(label, (log_x + padding, padding + i * line_height))

def export_game_to_pgn(board):
    # Export the game in PGN format to the 'games' folder
    if not os.path.exists("games"):
        os.makedirs("games")
    game = chess.pgn.Game()
    node = game
    for move in board.move_stack:
        node = node.add_variation(move)
    game.headers["White"] = "Player1"
    game.headers["Black"] = "Player2"
    game.headers["Result"] = board.result()
    i = 1
    while os.path.exists(f"games/game{i}.pgn"):
        i += 1
    with open(f"games/game{i}.pgn", "w") as f:
        print(game, file=f)

def main():
    # Main game loop
    pygame.init()
    running = True
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Chess")
    board = chess.Board()
    load_images()
    sq_selected = ()  # Selected square
    player_clicks = []  # Track clicks
    game_over = False
    game_result_text = ""
    scroll_offset = 0  # Scroll offset for move log
    flipped = False  # Board orientation

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_pos = pygame.mouse.get_pos()
                clicked_col = mouse_pos[0] // SQ_SIZE
                clicked_row = mouse_pos[1] // SQ_SIZE
                if clicked_col >= DIMENSION:
                    continue  # Ignore clicks on move log area
                clicked_square = (clicked_row, clicked_col)
                
                if flipped:
                    square_index = chess.square(7 - clicked_col, clicked_row)
                else:
                    square_index = chess.square(clicked_col, 7 - clicked_row)
                    
                clicked_piece = board.piece_at(square_index)

                if sq_selected == ():
                    if clicked_piece and clicked_piece.color == board.turn:
                        sq_selected = clicked_square
                        player_clicks = [sq_selected]
                    else:
                        sq_selected = ()
                        player_clicks = []
                else:
                    if clicked_square == sq_selected:
                        sq_selected = ()
                        player_clicks = []
                    elif clicked_piece and clicked_piece.color == board.turn:
                        sq_selected = clicked_square
                        player_clicks = [sq_selected]
                    else:
                        player_clicks.append(clicked_square)
                        if len(player_clicks) == 2:
                            move_made = make_move(board, player_clicks, screen, flipped)
                            if move_made:
                                if board.is_checkmate():
                                    game_over = True
                                    winner = "White" if not board.turn else "Black"
                                    game_result_text = f"{winner} wins, Checkmate!"
                                    export_game_to_pgn(board)
                                elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition() or board.is_variant_draw():
                                    game_over = True
                                    game_result_text = "Draw!"
                                    export_game_to_pgn(board)
                            sq_selected = ()
                            player_clicks = []

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    undo_move(board)
                    game_over = False
                    game_result_text = ""
                    sq_selected = ()
                    player_clicks = []
                elif event.key == pygame.K_r:
                    board = chess.Board()
                    game_over = False
                    game_result_text = ""
                    sq_selected = ()
                    player_clicks = []
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.key == pygame.K_DOWN:
                    scroll_offset += 1
                elif event.key == pygame.K_f:
                    flipped = not flipped
                    sq_selected = ()
                    player_clicks = []

        draw_board(screen)
        highlight_square(screen, sq_selected)
        draw_pieces(screen, board, flipped)
        draw_legal_moves(screen, board, sq_selected, flipped)
        draw_move_log(screen, board, scroll_offset)

        if game_over:
            draw_game_over_overlay(screen, game_result_text)

        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()