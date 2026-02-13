"""
Flappy Bird — curses, stdlib only, no root required

Start screen → Space to begin
In game      → Space to flap, q/Esc to quit
"""

import curses
import random
import time

# ── Constants ────────────────────────────────────────────────────────────────

WIDTH       = 60
HEIGHT      = 24
BIRD_COL    = 8
GRAVITY     = 0.3
FLAP        = -1.8
PIPE_SPEED  = 0.6   # columns per frame (fractional, accumulated)
PIPE_GAP    = 7
PIPE_EVERY  = 2.2    # seconds between pipe spawns
TICK        = 0.05   # seconds per frame


# ── Helpers ──────────────────────────────────────────────────────────────────

def new_pipe(x):
    gap_y = random.randint(2, HEIGHT - PIPE_GAP - 3)
    return {"x": float(x), "gap_y": gap_y, "scored": False}


def draw_border(stdscr):
    """Draw the play-field border."""
    for c in range(WIDTH + 2):
        try:
            stdscr.addch(0,          c, curses.ACS_HLINE)
            stdscr.addch(HEIGHT + 1, c, curses.ACS_HLINE)
        except curses.error:
            pass
    for r in range(HEIGHT + 2):
        try:
            stdscr.addch(r, 0,         curses.ACS_VLINE)
            stdscr.addch(r, WIDTH + 1, curses.ACS_VLINE)
        except curses.error:
            pass
    for r, c in [(0, 0), (0, WIDTH + 1),
                 (HEIGHT + 1, 0), (HEIGHT + 1, WIDTH + 1)]:
        try:
            stdscr.addch(r, c, curses.ACS_PLUS)
        except curses.error:
            pass


def draw_pipe(stdscr, pipe, pipe_color):
    x = int(pipe["x"])
    if x < 1 or x > WIDTH:
        return
    gap_y = pipe["gap_y"]
    for row in range(HEIGHT):
        in_gap = gap_y <= row < gap_y + PIPE_GAP
        screen_row = row + 1          # +1 for top border
        screen_col = x                # already offset — border is at col 0
        if 1 <= screen_col <= WIDTH and not in_gap:
            try:
                stdscr.addch(screen_row, screen_col,
                             curses.ACS_BLOCK, pipe_color)
                if screen_col + 1 <= WIDTH:
                    stdscr.addch(screen_row, screen_col + 1,
                                 curses.ACS_BLOCK, pipe_color)
            except curses.error:
                pass


# ── Screens ──────────────────────────────────────────────────────────────────

def start_screen(stdscr):
    """Show title screen. Returns when Space is pressed, or exits on q/Esc."""
    curses.curs_set(0)
    stdscr.nodelay(False)   # blocking — just wait for input
    stdscr.keypad(True)

    lines = [
        "",
        " ███████╗██╗      █████╗ ██████╗ ██████╗ ██╗   ██╗",
        " ██╔════╝██║     ██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝",
        " █████╗  ██║     ███████║██████╔╝██████╔╝ ╚████╔╝ ",
        " ██╔══╝  ██║     ██╔══██║██╔═══╝ ██╔═══╝   ╚██╔╝  ",
        " ██║     ███████╗██║  ██║██║     ██║        ██║   ",
        " ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝        ╚═╝   ",
        "",
        "              ·. · · B I R D · · .·",
        "",
        "",
        "          Press  SPACE  to start",
        "          Press    q    to quit",
        "",
        "   ── Controls ──────────────────────────",
        "   SPACE   flap",
        "   q / Esc quit",
    ]

    while True:
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()

        # Centre the block
        start_r = max(0, rows // 2 - len(lines) // 2)
        for i, line in enumerate(lines):
            r = start_r + i
            if r >= rows:
                break
            c = max(0, (cols - len(line)) // 2)
            attr = curses.A_BOLD if "SPACE" in line or "BIRD" in line else 0
            try:
                stdscr.addstr(r, c, line, attr)
            except curses.error:
                pass

        # Blink prompt
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord(' '):
            return True
        if key in (ord('q'), ord('Q'), 27):
            return False


def game_over_screen(stdscr, score):
    """Show game-over. Returns True to play again, False to quit."""
    stdscr.nodelay(False)
    lines = [
        "  ╔══════════════════════╗  ",
        "  ║      GAME  OVER      ║  ",
        f"  ║   Score : {score:<12}║  ",
        "  ╠══════════════════════╣  ",
        "  ║  SPACE  → play again ║  ",
        "  ║    q    → quit       ║  ",
        "  ╚══════════════════════╝  ",
    ]
    rows, cols = stdscr.getmaxyx()
    sr = max(0, rows // 2 - len(lines) // 2)
    stdscr.erase()
    for i, line in enumerate(lines):
        r = sr + i
        if r >= rows:
            break
        c = max(0, (cols - len(line)) // 2)
        try:
            stdscr.addstr(r, c, line, curses.A_BOLD)
        except curses.error:
            pass
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord(' '):
            return True
        if key in (ord('q'), ord('Q'), 27):
            return False


# ── Game loop ────────────────────────────────────────────────────────────────

def play(stdscr):
    curses.halfdelay(1)      # getch() times out after 0.1 s — no busy loop
    stdscr.keypad(True)
    curses.curs_set(0)

    # Colour pairs
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN,  -1)   # pipes
    curses.init_pair(2, curses.COLOR_YELLOW, -1)   # bird
    curses.init_pair(3, curses.COLOR_CYAN,   -1)   # score
    curses.init_pair(4, curses.COLOR_WHITE,  -1)   # border

    pipe_color = curses.color_pair(1) | curses.A_BOLD
    bird_color = curses.color_pair(2) | curses.A_BOLD
    score_color= curses.color_pair(3) | curses.A_BOLD

    # State
    bird_y    = HEIGHT / 2.0
    bird_vel  = 0.0
    pipes     = [new_pipe(WIDTH + 5)]
    score     = 0
    pipe_accum  = 0.0        # fractional pipe movement accumulator
    next_pipe   = PIPE_EVERY # seconds until next pipe spawns
    time_elapsed= 0.0        # total time since game started

    while True:
        t0 = time.monotonic()

        # ── Input ─────────────────────────────────────────────────────────
        key = stdscr.getch()
        if key == ord(' '):
            bird_vel = FLAP
        elif key in (ord('q'), ord('Q'), 27):
            return False    # quit entirely

        # ── Physics ───────────────────────────────────────────────────────
        bird_vel += GRAVITY
        bird_y   += bird_vel

        # ── Move pipes ────────────────────────────────────────────────────
        pipe_accum += PIPE_SPEED
        steps = int(pipe_accum)
        pipe_accum -= steps
        for pipe in pipes:
            pipe["x"] -= steps

        # Score: pipe fully passed the bird
        for pipe in pipes:
            if not pipe["scored"] and pipe["x"] + 1 < BIRD_COL:
                pipe["scored"] = True
                score += 1

        # Spawn new pipe on a timer
        time_elapsed += TICK
        next_pipe    -= TICK
        if next_pipe <= 0:
            pipes.append(new_pipe(WIDTH + 2))
            next_pipe = PIPE_EVERY

        # Remove off-screen pipes
        pipes = [p for p in pipes if p["x"] > -3]

        # ── Collision ─────────────────────────────────────────────────────
        dead = False
        if bird_y < 0 or bird_y >= HEIGHT:
            dead = True
        for pipe in pipes:
            px = int(pipe["x"])
            # Bird occupies BIRD_COL and BIRD_COL (1 wide); pipe is 2 wide
            if px <= BIRD_COL <= px + 1:
                by = int(bird_y)
                if not (pipe["gap_y"] <= by < pipe["gap_y"] + PIPE_GAP):
                    dead = True

        if dead:
            return score   # hand score back to caller

        # ── Draw ──────────────────────────────────────────────────────────
        stdscr.erase()
        draw_border(stdscr)

        # Pipes
        for pipe in pipes:
            draw_pipe(stdscr, pipe, pipe_color)

        # Bird  (▶ as fallback if emoji width is unreliable in curses)
        br = int(bird_y) + 1   # +1 for border row
        bc = BIRD_COL
        if 1 <= br <= HEIGHT and 1 <= bc <= WIDTH:
            try:
                stdscr.addstr(br, bc, ">", bird_color)
            except curses.error:
                pass

        # Score
        try:
            stdscr.addstr(0, 3, f" Score: {score} ", score_color)
        except curses.error:
            pass

        stdscr.refresh()

        # ── Tick timing ───────────────────────────────────────────────────
        elapsed = time.monotonic() - t0
        wait    = TICK - elapsed
        if wait > 0:
            time.sleep(wait)


# ── Entry point ──────────────────────────────────────────────────────────────

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()

    while True:
        if not start_screen(stdscr):
            return                    # quit from title

        result = play(stdscr)

        if result is False:
            return                    # quit mid-game

        # result is the score
        play_again = game_over_screen(stdscr, result)
        if not play_again:
            return


if __name__ == "__main__":
    curses.wrapper(main)