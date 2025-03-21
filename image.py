import os
import subprocess
from PIL import Image
import platform

def get_file_path():
    """Opens the system's file selector and returns the selected file path."""
    system = platform.system()
    if system == "Windows":
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
            return file_path
        except ImportError:
            print("tkinter not installed. Please install tkinter for file selection.")
            return None
    elif system == "Linux" or system == "Darwin": #Mac os included
        try:
            file_path = subprocess.check_output(["zenity", "--file-selection", "--file-filter=*.png *.jpg *.jpeg *.gif *.bmp"]).decode().strip()
            return file_path
        except FileNotFoundError:
            try: #try kdialog if zenity is not found.
                file_path = subprocess.check_output(["kdialog", "--getopenfilename", "*.png *.jpg *.jpeg *.gif *.bmp"]).decode().strip()
                return file_path
            except FileNotFoundError:
                print("zenity or kdialog not found. Please install either for file selection.")
                return None
        except subprocess.CalledProcessError:
            return None  # User canceled the file selection
    else:
        print(f"Unsupported operating system: {system}")
        return None

def image_to_ascii(image_path, width=100):
    """Converts an image to color ASCII art and prints it to the terminal."""
    try:
        img = Image.open(image_path).convert('RGB')
    except FileNotFoundError:
        print("Image not found.")
        return
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.5)
    img = img.resize((width, height))

    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    ascii_len = len(ascii_chars)

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            brightness = (r + g + b) // 3
            ascii_index = int(brightness * (ascii_len - 1) / 255)
            char = ascii_chars[ascii_index]
            print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="")  # Color ASCII
        print()

def main():
    """Main function to run the image to ASCII art conversion."""
    image_path = get_file_path()
    if image_path:
        image_to_ascii(image_path)

if __name__ == "__main__":
    main()