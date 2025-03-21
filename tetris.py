import os
import random
import time
from pynput import keyboard

# Game constants
WIDTH = 12
HEIGHT = 22
TETROMINOS = [
    ([[1, 1, 1, 1]], 31),  # I (Red)
    ([[1, 1], [1, 1]], 33),  # O (Yellow)
    ([[0, 1, 0], [1, 1, 1]], 32),  # T (Green)
    ([[1, 1, 0], [0, 1, 1]], 36),  # Z (Cyan)
    ([[0, 1, 1], [1, 1, 0]], 34),  # S (Blue)
    ([[1, 0, 0], [1, 1, 1]], 35),  # L (Magenta)
    ([[0, 0, 1], [1, 1, 1]], 93),  # J (Light Yellow)
]

def create_board():
    return [[(' ', 0) for _ in range(WIDTH)] for _ in range(HEIGHT)] # Fixed here

def new_tetromino():
    tetromino, color = random.choice(TETROMINOS)
    return tetromino, 0, WIDTH // 2 - 2, color

def rotate(tetromino):
    return list(zip(*reversed(tetromino)))

def check_collision(board, tetromino, row, col):
    for r, row_data in enumerate(tetromino):
        for c, cell in enumerate(row_data):
            if cell and (row + r >= HEIGHT or col + c < 0 or col + c >= WIDTH or board[row + r][col + c][0] != ' '):
                return True
    return False

def merge_tetromino(board, tetromino, row, col, color):
    for r, row_data in enumerate(tetromino):
        for c, cell in enumerate(row_data):
            if cell:
                board[row + r][col + c] = ('#', color)

def clear_lines(board):
    lines_cleared = 0
    full_rows = []
    for r in range(HEIGHT):
        if all(cell[0] != ' ' for cell in board[r]):
            full_rows.append(r)

    # Clear lines from bottom up
    full_rows.sort(reverse=True)
    for row_index in full_rows:
        del board[row_index]
        board.insert(0, [(' ', 0) for _ in range(WIDTH)])
        lines_cleared += 1

    return lines_cleared

def draw_board(board, tetromino, row, col, color):
    os.system('cls' if os.name == 'nt' else 'clear')
    temp_board = [row[:] for row in board]

    # Draw shadow
    shadow_row = row
    while not check_collision(board, tetromino, shadow_row + 1, col):
        shadow_row += 1
    for r, row_data in enumerate(tetromino):
        for c, cell in enumerate(row_data):
            if cell:
                temp_board[shadow_row + r][col + c] = ('.-.', color)

    # Draw tetromino
    for r, row_data in enumerate(tetromino):
        for c, cell in enumerate(row_data):
            if cell:
                temp_board[row + r][col + c] = ('#', color)

    for row_data in temp_board:
        line = '|'
        for cell, cell_color in row_data:
            line += f"\033[{cell_color}m{cell[0]}\033[0m"
        print(line + '|')
    print('+' + '-' * WIDTH + '+')

def tetris():
    board = create_board()
    tetromino, row, col, color = new_tetromino()
    score = 0
    drop_timer = 0
    drop_interval = 1.0
    key_pressed = None
    space_pressed = False
    game_over = False

    def on_press(key):
        nonlocal key_pressed, space_pressed, game_over
        try:
            if key == keyboard.Key.space:
                space_pressed = True
            elif hasattr(key, 'char') and key.char == 'e': #robust E key capture.
                game_over = True
            else:
                key_pressed = key
        except AttributeError:
            key_pressed = key

    def on_release(key):
        nonlocal key_pressed, space_pressed
        if key == keyboard.Key.space:
            space_pressed = False
        else:
            if key_pressed == key:
                key_pressed = None

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while not game_over:
        draw_board(board, tetromino, row, col, color)

        if key_pressed == keyboard.Key.left:
            if not check_collision(board, tetromino, row, col - 1):
                col -= 1
        elif key_pressed == keyboard.Key.right:
            if not check_collision(board, tetromino, row, col + 1):
                col += 1
        elif key_pressed == keyboard.Key.down:
            if not check_collision(board, tetromino, row + 1, col):
                row += 1
        elif key_pressed == keyboard.Key.up:
            rotated_tetromino = rotate(tetromino)
            if not check_collision(board, rotated_tetromino, row, col):
                tetromino = rotated_tetromino

        if space_pressed:
            while not check_collision(board, tetromino, row + 1, col):
                row += 1

        drop_timer += 0.1
        if drop_timer >= drop_interval:
            if check_collision(board, tetromino, row + 1, col):
                merge_tetromino(board, tetromino, row, col, color)
                score += clear_lines(board) * 100
                tetromino, row, col, color = new_tetromino()
                if check_collision(board, tetromino, 0, WIDTH // 2 - 2):
                    game_over = True
                    break
                row, col = 0, WIDTH // 2 - 2
            else:
                row += 1
            drop_timer = 0

        time.sleep(0.1)

    listener.stop()
    if game_over:
        print(f"Game Over! Score: {score}")

if __name__ == "__main__":
    tetris()