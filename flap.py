import os
import time
import random
from pynput import keyboard

# Constants
WIDTH = 40
HEIGHT = 20
BIRD_CHAR = "🐦"
PIPE_CHAR = "█"
GRAVITY = 0.1   # Use a float for gravity
FLAP_STRENGTH = -1                  
PIPE_SPEED = 1
PIPE_GAP = 10

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_screen(bird_y, pipes):
    """Draws the game screen."""
    screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Draw bird
    if 0 <= bird_y < HEIGHT:
        screen[int(bird_y)][5] = BIRD_CHAR #Convert to int for screen indexing

    # Draw pipes
    for pipe in pipes:
        for y in range(HEIGHT):
            if y < pipe["gap_y"] or y >= pipe["gap_y"] + PIPE_GAP:
                if 0 <= pipe["x"] < WIDTH:
                    screen[y][pipe["x"]] = PIPE_CHAR
                    if 0<= pipe["x"] + 1 < WIDTH:
                      screen[y][pipe["x"]+1] = PIPE_CHAR

    # Print screen
    clear_screen()
    for row in screen:
        print("".join(row))

def generate_pipe():
    """Generates a new pipe."""
    return {"x": WIDTH - 1, "gap_y": random.randint(2, HEIGHT - PIPE_GAP - 2)}

def main():
    """Main game loop."""
    bird_y = HEIGHT / 2.0  # Use float for bird_y
    bird_velocity = 0.0 #use float for bird velocity.
    pipes = [generate_pipe()]
    score = 0
    game_over = False

    def on_press(key):
        nonlocal bird_velocity
        try:
            if key == keyboard.Key.space:
                bird_velocity = FLAP_STRENGTH
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while not game_over:
        # Update bird position
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        # Update pipes
        for pipe in pipes:
            pipe["x"] -= PIPE_SPEED

        # Generate new pipes
        if pipes[-1]["x"] < WIDTH - WIDTH // 3:
            pipes.append(generate_pipe())

        # Remove old pipes
        if pipes[0]["x"] < -2:
            pipes.pop(0)
            score += 1

        # Collision detection
        if bird_y < 0 or bird_y >= HEIGHT:
            game_over = True
        for pipe in pipes:
            if 3 <= pipe["x"] <= 6:
                if bird_y < pipe["gap_y"] or bird_y >= pipe["gap_y"] + PIPE_GAP:
                    game_over = True

        # Draw screen
        draw_screen(bird_y, pipes)
        print(f"Score: {score}")

        time.sleep(0.05) #Adjusted time.sleep.

    listener.stop()
    print("Game Over!")
    print(f"Final Score: {score}")

if __name__ == "__main__":
    main()