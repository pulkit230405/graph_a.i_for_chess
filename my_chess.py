import os, sys, pygame, chess
from collections import deque
from graph_ai import evaluate_board, find_best_move

pygame.init()
WIDTH, HEIGHT, SQUARE_SIZE = 600, 600, 75
WHITE, BROWN = (240, 217, 181), (181, 136, 99)
BUTTON_WIDTH, SIDE_PANEL_WIDTH = 180, 200

PIECE_IMAGES = {}
for p in 'prnbqkPRNBQK':
    color = 'b' if p.islower() else 'w'
    fname = os.path.join("pieces", f"{color}{p.lower()}.png")
    if os.path.exists(fname):
      img = pygame.transform.scale(pygame.image.load(fname), (SQUARE_SIZE, SQUARE_SIZE))
    else:
        img = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
    PIECE_IMAGES[p] = img

board = chess.Board()
screen = pygame.display.set_mode((WIDTH + SIDE_PANEL_WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
font, small_font = pygame.font.Font(None, 36), pygame.font.Font(None, 24)

post_search_eval = 0
ai_thoughts = []
game_message = ""
show_knight_path = show_attack_pattern = False
selected_square = selected_for_pattern = knight_start = knight_end = None
knight_path = []

button_rects = {
    k: pygame.Rect(WIDTH + 10, 400 + i * 40, BUTTON_WIDTH, 30)
    for i, k in enumerate(["knight_path", "attack_pattern", "minimax_tree", "show_all"])
}

def draw_buttons():
    for k, r in button_rects.items():
        pygame.draw.rect(screen, (100, 100, 100), r)
        pygame.draw.rect(screen, (255, 255, 255), r, 2)
        screen.blit(small_font.render(k.replace("_", " ").title(), True, (255, 255, 255)), (r.x + 10, r.y + 5))

def handle_button_click(pos):
    global show_knight_path, show_attack_pattern, knight_path, knight_start, knight_end, selected_for_pattern
    if button_rects["knight_path"].collidepoint(pos):
        show_knight_path, knight_path, knight_start, knight_end = not show_knight_path, [], None, None
    elif button_rects["attack_pattern"].collidepoint(pos):
        show_attack_pattern, selected_for_pattern = not show_attack_pattern, None
    elif button_rects["show_all"].collidepoint(pos):
        show_knight_path = show_attack_pattern = True

def draw_eval_bar():
    bar_x, bar_w = WIDTH + 160, 20
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, 0, bar_w, HEIGHT))
    eval_for_white = -post_search_eval if board.turn == chess.WHITE else post_search_eval
    eval_for_white_normalized = max(min(eval_for_white, 500), -500) / 500
    white_bar_height = int(((eval_for_white_normalized + 1) / 2) * HEIGHT)
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, HEIGHT - white_bar_height, bar_w, white_bar_height))
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, 0, bar_w, HEIGHT - white_bar_height))

def draw_ai_thought_panel():
    screen.blit(font.render("AI Thoughts", True, (255, 255, 255)), (WIDTH + 10, 10))
    for i, (move_san, eval_score) in enumerate(ai_thoughts):
        y = 50 + 40 * i
        text_color = (220, 220, 100) if eval_score == ai_thoughts[0][1] else (180, 180, 180)
        screen.blit(small_font.render(f"{i+1}. {move_san}", True, text_color), (WIDTH + 10, y))
        screen.blit(small_font.render(f"{eval_score/100.0:+.2f}", True, text_color), (WIDTH + 100, y))

def draw_side_panel():
    panel_rect = pygame.Rect(WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), panel_rect)
    draw_ai_thought_panel()
    draw_eval_bar()
    draw_buttons()

def knight_shortest_path(start, end):
    dirs = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
    queue, visited = deque([[start]]), set()
    while queue:
        path = queue.popleft()
        curr = path[-1]
        if curr == end: return path
        if curr in visited: continue
        visited.add(curr)
        r, c = divmod(curr, 8)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                next_sq = nr * 8 + nc
                if next_sq not in visited:
                    queue.append(path + [next_sq])
    return []

def draw_graph_path(path, color):
    pts = [(chess.square_file(sq) * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - chess.square_rank(sq)) * SQUARE_SIZE + SQUARE_SIZE // 2) for sq in path]
    for p in pts: pygame.draw.circle(screen, color, p, 6)
    for a, b in zip(pts, pts[1:]): pygame.draw.line(screen, color, a, b, 2)

def draw_attack_pattern(square):
    piece = board.piece_at(square)
    if not piece: return
    sx, sy = chess.square_file(square) * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - chess.square_rank(square)) * SQUARE_SIZE + SQUARE_SIZE // 2
    for t in board.attacks(square):
        x, y = chess.square_file(t) * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - chess.square_rank(t)) * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 6)
        pygame.draw.line(screen, (255, 0, 0), (sx, sy), (x, y), 2)

def draw_board():
    for r in range(8):
        for c in range(8):
            sq = chess.square(c, 7 - r)
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            color = WHITE if (r + c) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, rect)
            if selected_square == sq:
                pygame.draw.rect(screen, (0, 255, 0), rect, 3)
            elif selected_square and chess.Move(selected_square, sq) in board.legal_moves:
                pygame.draw.circle(screen, (0, 0, 255), tuple(map(int, rect.center)), 10)
    for i in range(8):
        screen.blit(small_font.render(str(8 - i), True, (0, 0, 0)), (5, i * SQUARE_SIZE + 5))
        screen.blit(small_font.render(chr(97 + i), True, (0, 0, 0)), (i * SQUARE_SIZE + SQUARE_SIZE - 15, HEIGHT - 20))

def draw_pieces():
    for r in range(8):
        for c in range(8):
            sq = chess.square(c, 7 - r)
            p = board.piece_at(sq)
            if p: screen.blit(PIECE_IMAGES[p.symbol()], (c * SQUARE_SIZE, r * SQUARE_SIZE))

def draw_message():
    if game_message:
        text = font.render(game_message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        pygame.draw.rect(screen, (0,0,0,150), text_rect.inflate(20,20))
        screen.blit(text, text_rect)

def check_game_status():
    global game_message, ai_thoughts
    if board.is_game_over():
        ai_thoughts = []
        if board.is_checkmate(): game_message = "Checkmate! Game Over."
        elif board.is_stalemate(): game_message = "Stalemate!"
        else: game_message = "Game Over"
    else:
        game_message = ""

def handle_click(pos):
    global selected_square, knight_path, selected_for_pattern, knight_start, knight_end, ai_thoughts, post_search_eval
    if board.is_game_over(): return
    col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
    sq = chess.square(col, 7 - row)

    if show_knight_path:
        if knight_start is None: knight_start = sq
        else:
            knight_end = sq; knight_path = knight_shortest_path(knight_start, knight_end) or []; knight_start = None
        return

    if selected_square is None:
        if board.piece_at(sq) and board.piece_at(sq).color == board.turn:
            selected_square = sq
            if show_attack_pattern: selected_for_pattern = sq
    else:
        move = chess.Move(selected_square, sq)
        if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(sq) in [0, 7]:
            move = chess.Move(selected_square, sq, promotion=chess.QUEEN)
            
        if move in board.legal_moves:
            board.push(move)
            check_game_status()
            draw_board(); draw_pieces(); draw_side_panel(); pygame.display.flip()
            
            if not board.is_game_over():
                ai_move, thoughts = find_best_move(board, 3)
                ai_thoughts = thoughts
                if thoughts:
                    post_search_eval = thoughts[0][1]
                if ai_move:
                    board.push(ai_move)
                check_game_status()
        selected_square = None
        
running = True
while running:
    draw_board()
    draw_pieces()
    draw_side_panel()
    draw_message()
    if show_knight_path and knight_path: draw_graph_path(knight_path, (0, 255, 255))
    if show_attack_pattern and selected_for_pattern: draw_attack_pattern(selected_for_pattern)
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] >= WIDTH:
                handle_button_click(event.pos)
            else:
                handle_click(event.pos)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_u:
            if board.move_stack: board.pop()
            if board.move_stack: board.pop()
            check_game_status()
            ai_thoughts = []; post_search_eval = 0

pygame.quit()