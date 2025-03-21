import curses
import random
import time

def snake_game(stdscr):
    """Snake game using curses."""

    stdscr.clear()
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(180)  # Input timeout in milliseconds (adjust for speed)
    sh, sw = stdscr.getmaxyx()
    box_width = sw - 2
    box_height = sh - 2
    stdscr.border()

    snake = [(box_height // 2, box_width // 2)]
    direction = curses.KEY_RIGHT
    food = (random.randint(1, box_height - 2), random.randint(1, box_width - 2))
    score = 0

    def place_food():
        nonlocal food
        while True:
            food = (random.randint(1, box_height - 2), random.randint(1, box_width - 2))
            if food not in snake:
                break

    place_food()

    while True:
        stdscr.addch(food[0], food[1], curses.ACS_BLOCK)

        for segment in snake:
            stdscr.addch(segment[0], segment[1], curses.ACS_BLOCK)  # Snake is all squares

        next_key = stdscr.getch()
        if next_key != -1:
            if next_key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN]:
                if (next_key == curses.KEY_LEFT and direction != curses.KEY_RIGHT) or \
                   (next_key == curses.KEY_RIGHT and direction != curses.KEY_LEFT) or \
                   (next_key == curses.KEY_UP and direction != curses.KEY_DOWN) or \
                   (next_key == curses.KEY_DOWN and direction != curses.KEY_UP):
                    direction = next_key

        head = snake[0]
        if direction == curses.KEY_RIGHT:
            new_head = (head[0], head[1] + 1)
        elif direction == curses.KEY_LEFT:
            new_head = (head[0], head[1] - 1)
        elif direction == curses.KEY_UP:
            new_head = (head[0] - 1, head[1])
        elif direction == curses.KEY_DOWN:
            new_head = (head[0] + 1, head[1])

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            place_food()
        else:
            stdscr.addch(snake[-1][0], snake[-1][1], ' ')
            snake.pop()

        # Game over conditions: hitting wall or self
        if (new_head[0] < 1 or new_head[0] > box_height - 0 or new_head[1] < 1 or new_head[1] > box_width - 0 or new_head in snake[1:]):
            stdscr.nodelay(0)
            stdscr.addstr(sh // 2 - 1, sw // 2 - 5, "Game Over!")
            stdscr.addstr(sh // 2 + 1, sw // 2 - 8, f"Score: {score}")
            stdscr.refresh()
            stdscr.getch()
            break
        stdscr.refresh()

curses.wrapper(snake_game)