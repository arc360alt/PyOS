"""
Tetris — stdlib only (curses), no root, Linux + Windows

Controls:
  ← →     move
  ↑        rotate
  ↓        soft drop
  Space    hard drop
  q / Esc  quit
"""

import curses
import random
import time

# ── Constants ────────────────────────────────────────────────────────────────

WIDTH  = 12
HEIGHT = 22

# How long between gravity drops at level 1 (seconds)
BASE_DROP_INTERVAL = 1.0

TETROMINOS = [
    ([[1, 1, 1, 1]], 1),           # I
    ([[1, 1], [1, 1]], 2),          # O
    ([[0, 1, 0], [1, 1, 1]], 3),   # T
    ([[1, 1, 0], [0, 1, 1]], 4),   # Z
    ([[0, 1, 1], [1, 1, 0]], 5),   # S
    ([[1, 0, 0], [1, 1, 1]], 6),   # L
    ([[0, 0, 1], [1, 1, 1]], 7),   # J
]


# ── Board helpers ────────────────────────────────────────────────────────────

def create_board():
    return [[(0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]

def new_piece():
    shape, color = random.choice(TETROMINOS)
    return [row[:] for row in shape], 0, WIDTH // 2 - 2, color

def rotate_cw(shape):
    return [list(row) for row in zip(*reversed(shape))]

def collides(board, shape, row, col):
    for r, row_data in enumerate(shape):
        for c, cell in enumerate(row_data):
            if cell:
                nr, nc = row + r, col + c
                if nr >= HEIGHT or nc < 0 or nc >= WIDTH:
                    return True
                if board[nr][nc][0]:
                    return True
    return False

def merge(board, shape, row, col, color):
    for r, row_data in enumerate(shape):
        for c, cell in enumerate(row_data):
            if cell:
                board[row + r][col + c] = (1, color)

def clear_lines(board):
    full = [r for r in range(HEIGHT) if all(board[r][c][0] for c in range(WIDTH))]
    for r in sorted(full, reverse=True):
        del board[r]
        board.insert(0, [(0, 0) for _ in range(WIDTH)])
    return len(full)

def drop_bottom(board, shape, row, col):
    while not collides(board, shape, row + 1, col):
        row += 1
    return row

def lock_piece(board, shape, row, col, color, score, lines_total, level):
    merge(board, shape, row, col, color)
    cleared     = clear_lines(board)
    lines_total += cleared
    score       += (cleared ** 2) * 100 * level
    level        = lines_total // 10 + 1
    drop_int     = max(0.1, BASE_DROP_INTERVAL - (level - 1) * 0.09)
    shape, row, col, color = new_piece()
    dead         = collides(board, shape, row, col)
    return shape, row, col, color, score, lines_total, level, drop_int, dead


# ── Drawing ──────────────────────────────────────────────────────────────────

def draw(stdscr, board, shape, row, col, color,
         score, level, next_shape, next_color):
    stdscr.erase()

    # Build display grid
    grid = [list(board[r]) for r in range(HEIGHT)]

    ghost_row = drop_bottom(board, shape, row, col)
    for r, row_data in enumerate(shape):
        for c, cell in enumerate(row_data):
            if cell and not grid[ghost_row + r][col + c][0]:
                grid[ghost_row + r][col + c] = (2, color)   # ghost

    for r, row_data in enumerate(shape):
        for c, cell in enumerate(row_data):
            if cell:
                grid[row + r][col + c] = (1, color)

    try:
        stdscr.addstr(0, 0, f"Score: {score}   Level: {level}")
        stdscr.addstr(1, 0, '+' + '-' * WIDTH + '+')
        for r in range(HEIGHT):
            stdscr.addstr(r + 2, 0, '|')
            for c in range(WIDTH):
                filled, cp = grid[r][c]
                if filled == 1:
                    stdscr.addstr(r + 2, c + 1, '#',
                                  curses.color_pair(cp) | curses.A_BOLD)
                elif filled == 2:
                    stdscr.addstr(r + 2, c + 1, '·', curses.color_pair(cp))
                else:
                    stdscr.addstr(r + 2, c + 1, ' ')
            stdscr.addstr(r + 2, WIDTH + 1, '|')
        stdscr.addstr(HEIGHT + 2, 0, '+' + '-' * WIDTH + '+')

        # Next piece
        stdscr.addstr(2, WIDTH + 4, "NEXT:")
        for r, row_data in enumerate(next_shape):
            for c, cell in enumerate(row_data):
                attr = curses.color_pair(next_color) | curses.A_BOLD if cell else 0
                stdscr.addstr(3 + r, WIDTH + 4 + c, '#' if cell else ' ', attr)

        stdscr.addstr(HEIGHT + 4, 0,
                      "arrows=move/rotate  space=drop  q=quit")
    except curses.error:
        pass

    stdscr.refresh()


# ── Main ─────────────────────────────────────────────────────────────────────

def tetris(stdscr):
    # --- curses init ---
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    # halfdelay(N): getch() waits up to N tenths-of-a-second, then returns ERR.
    # This lets arrow-key escape sequences arrive as a single unit (keypad=True
    # handles the decoding) without busy-looping or splitting multi-byte keys.
    curses.halfdelay(1)          # 0.1 s timeout — responsive but not busy
    stdscr.keypad(True)          # decode arrow keys into KEY_LEFT etc.

    for i, c in enumerate([
        curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_GREEN,
        curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA,
        curses.COLOR_WHITE,
    ], start=1):
        curses.init_pair(i, c, -1)

    # --- game state ---
    board       = create_board()
    shape, row, col, color = new_piece()
    next_shape, _, _, next_color = new_piece()
    score       = 0
    lines_total = 0
    level       = 1
    drop_int    = BASE_DROP_INTERVAL
    drop_timer  = 0.0
    game_over   = False

    last_tick   = time.monotonic()

    while not game_over:

        # --- timing ---
        now     = time.monotonic()
        elapsed = now - last_tick
        last_tick = now

        # --- input ---
        # halfdelay means this blocks for up to 0.1 s then returns ERR.
        # keypad=True means arrow keys come in as a single KEY_* constant.
        key = stdscr.getch()

        moved    = False
        rotated  = False
        dropped  = False
        quit_key = False

        if key == curses.KEY_LEFT:
            if not collides(board, shape, row, col - 1):
                col -= 1
                moved = True

        elif key == curses.KEY_RIGHT:
            if not collides(board, shape, row, col + 1):
                col += 1
                moved = True

        elif key == curses.KEY_DOWN:
            if not collides(board, shape, row + 1, col):
                row += 1
                drop_timer = 0   # soft drop resets gravity

        elif key == curses.KEY_UP:
            rotated_shape = rotate_cw(shape)
            for kick in (0, -1, 1, -2, 2):
                if not collides(board, rotated_shape, row, col + kick):
                    shape = rotated_shape
                    col  += kick
                    break

        elif key == ord(' '):
            row = drop_bottom(board, shape, row, col)
            (shape, row, col, color,
             score, lines_total, level,
             drop_int, game_over) = lock_piece(
                board, shape, row, col, color,
                score, lines_total, level)
            next_shape, _, _, next_color = new_piece()
            drop_timer = 0

        elif key in (ord('q'), ord('Q'), 27):   # q, Q, Esc
            break

        # --- gravity ---
        if not game_over:
            drop_timer += elapsed
            if drop_timer >= drop_int:
                drop_timer = 0
                if collides(board, shape, row + 1, col):
                    (shape, row, col, color,
                     score, lines_total, level,
                     drop_int, game_over) = lock_piece(
                        board, shape, row, col, color,
                        score, lines_total, level)
                    next_shape, _, _, next_color = new_piece()
                else:
                    row += 1

        draw(stdscr, board, shape, row, col, color,
             score, level, next_shape, next_color)

    # --- game over ---
    curses.halfdelay(255)   # slow timeout so we can wait for a keypress
    stdscr.erase()
    lines = [
        "╔══════════════════╗",
        "║    GAME  OVER    ║",
        f"║  Score : {score:<7}  ║",
        f"║  Level : {level:<7}  ║",
        "╚══════════════════╝",
        "",
        "   press any key...",
    ]
    sr = max(0, HEIGHT // 2 - len(lines) // 2)
    for i, line in enumerate(lines):
        try:
            stdscr.addstr(sr + i, 2, line)
        except curses.error:
            pass
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(tetris)