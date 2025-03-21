import time
import random
import platform
import os
import subprocess
import pexpect
import psutil
from pynput import keyboard
import readline  # Import readline
import shutil
import sys

processor_name = platform.processor()

def rainbow_print(text):
    """Prints text with a rainbow effect."""
    colors = [31, 33, 32, 36, 34, 35]
    for char in text:
        color = random.choice(colors)
        print(f"\033[{color}m{char}", end="", flush=True)
        time.sleep(0.02)
    print("\033[0m")

def custom_neofetch():
    """Displays custom system information."""
    print("-------------------------")
    print(f"OS: PyOS Mini Console")
    print(f"Kernel: {platform.version()}")
    print(f"Python: {platform.python_version()}")
    print(f"Username: {os.getlogin()}")
    if platform.system() == "Windows":
        try:
            processor_info = subprocess.check_output("wmic cpu get Name", shell=True, text=True).strip().split('\n')[1].strip()
            print(f"Processor: {processor_info}")
            gpu_info = subprocess.check_output("wmic path win32_VideoController get Name", shell=True, text=True).strip().split('\n')[1].strip()
            print(f"GPU: {gpu_info}")
        except Exception:
            print("Processor/GPU: Unknown")
    elif platform.system() == "Linux":
        try:
            processor_info = subprocess.check_output("lscpu | grep 'Model name' | cut -d':' -f2 | sed 's/^ //'", shell=True, text=True).strip()
            print(f"Processor: {processor_info}")
            gpu_info = subprocess.check_output("lspci | grep -E 'VGA|3D|Display'", shell=True, text=True).strip()
            print(f"GPU: {gpu_info}")
        except Exception:
            print("Processor/GPU: Unknown")
    else:
        print(f"Processor: {platform.processor()}")
    print(f"RAM: {round(psutil.virtual_memory().total / (1024.0 **3))} GB")
    print("-------------------------")
    print("    \033[32m   _____\033[0m")
    print("    \033[32m  |     |\033[0m")
    print("    \033[32m  |_____|\033[0m")
    print("    \033[32m  |     \033[0m")
    print("    \033[32m  |     \033[0m")

def run_ollama(command_parts):
    """Runs the 'ollama' command with pexpect or subprocess based on OS."""
    system = platform.system()

    try:
        if system == "Windows":
            command = " ".join(command_parts)
            subprocess.run(command, shell=True, check=True)
        elif system == "Linux" or system == "Darwin":
            command = " ".join(command_parts)
            child = pexpect.spawn(command, env=os.environ.copy())

            while True:
                try:
                    index = child.expect([r"(.+)\n", r">>> "], timeout=0.1)
                    if index == 0:
                        print(child.match.group(1).decode())
                    elif index == 1:
                        user_input = input(">>> ") + "\n"
                        child.send(user_input)
                except pexpect.TIMEOUT:
                    pass
                except pexpect.EOF:
                    break
            child.close()
        else:
            print(f"Unsupported operating system: {system}")

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"\033[31mError: {e}\033[0m")
    except FileNotFoundError:
        print("\033[31mError: Command not found. Make sure it is installed.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\033[31mError: {e}\033[0m")
    except Exception as e:
        print(f"\033[31mAn unexpected error occurred: {e}\033[0m")

def install_script(script_name):
    """Installs a Python script as a command and returns the command name."""

    if not script_name.endswith(".py"):
        print("Error: Script name must end with '.py'")
        return None  # Return None on error

    if not os.path.exists(script_name):
        print(f"Error: Script '{script_name}' not found.")
        return None  # Return None on error

    command_name = script_name[:-3]  # Remove '.py' extension

    # Determine the installation directory (e.g., /usr/local/bin or ~/.local/bin)
    if os.name == 'posix':  # Linux or macOS
        if os.geteuid() == 0:  # Check if running as root
            install_dir = "/usr/local/bin"
        else:
            install_dir = os.path.expanduser("~/.local/bin")

        if not os.path.exists(install_dir):
            try:
                os.makedirs(install_dir)
            except OSError as e:
                print(f"Error creating installation directory: {e}")
                return

        install_path = os.path.join(install_dir, command_name)

        # wrapper thing
        with open(install_path, "w") as wrapper_script:
            wrapper_script.write(f"#!/usr/bin/env python3\n")
            wrapper_script.write(f"import os\n")
            wrapper_script.write(f"os.chdir(r'{os.getcwd()}')\n") #change dir
            wrapper_script.write(f"import {command_name}\n")

        os.chmod(install_path, 0o755)  # execute ts

        if os.name == 'posix':
            # ... (POSIX installation) ...
            print(f"Script '{script_name}' installed as command '{command_name}' in {install_dir}")
        elif os.name == 'nt':
            # ... (Windows installation) ...
            print(f"Script '{script_name}' installed as command '{command_name}' in {install_dir}")
        else:
            print("Error: Unsupported operating system.")
            return None #return nothing on error

        return command_name  # Return the command name

        print(f"Script '{script_name}' installed as command '{command_name}' in {install_dir}")

    elif os.name == 'nt':  # Windows
        install_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs") #add to start menu
        install_path = os.path.join(install_dir, f"{command_name}.bat") #create bat file
        with open(install_path, "w") as bat_file:
            bat_file.write(f"@echo off\n")
            bat_file.write(f"python \"{os.path.join(os.getcwd(),script_name)}\" %*\n") #run python script

        print(f"Script '{script_name}' installed as command '{command_name}' in {install_dir}")

    else:
        print("Error: Unsupported operating system.")

def load_installed_commands():
    """Loads installed commands from a file."""
    try:
        with open("installed_commands.txt", "r") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return ["help", "hello", "about", "exit", "clear", "time", "pyfetch", "ollama", "echo", "tetris", "image", "flappybird", "calculator", "snake", "pyinstall"]

def save_installed_commands(commands):
    """Saves installed commands to a file."""
    with open("installed_commands.txt", "w") as f:
        for command in commands:
            f.write(command + "\n")


def fake_os():
    """Simulates a fake terminal-based OS with command history."""

    os_name = "PyOS Mini Console"
    rainbow_print(os_name + "\n")
    rainbow_print("version 0.1 beta\n")
    rainbow_print("https://arc360hub.com (c) 2020-2025\n")
    rainbow_print("Enter help to get supported commands\n")
    print("\n")

    command_history = []
    history_index = -1
    current_command = ""
    installed_commands = load_installed_commands() #load commands

    def on_press(key):
        nonlocal history_index, current_command
        try:
            if key == keyboard.Key.up:
                if len(command_history) > 0 and history_index < len(command_history) - 1:
                    history_index += 1
                    current_command = command_history[history_index]
                    readline.set_startup_hook(lambda: readline.insert_text(current_command))
            elif key == keyboard.Key.down:
                if history_index > -1:
                    history_index -= 1
                    if history_index == -1:
                        current_command = ""
                    else:
                        current_command = command_history[history_index]
                    readline.set_startup_hook(lambda: readline.insert_text(current_command))
        except AttributeError:
            pass
        except IndexError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while True:
        try:
            current_command = input("> ")
        except EOFError:
            print("\nExiting...")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        command_history.insert(0, current_command)
        history_index = -1
        command_parts = current_command.split()

        if command_parts:
            if command_parts[0] == "help":
                print(f"Available commands: {', '.join(installed_commands)}") #print all commands
            elif command_parts[0] == "hello":
                print("Hello, user!")
            elif command_parts[0] == "about":
                print("This is a Fake OS named PyOS made in Python by Arc360 and a tiny bit of gemini helping me get started.")
            elif command_parts[0] == "exit":
                print("Exiting...")
                break
            elif command_parts[0] == "clear":
                print("\033c", end="")
            elif command_parts[0] == "time":
                import datetime
                now = datetime.datetime.now()
                print(now.strftime("%Y-%m-%d %H:%M:%S"))
            elif command_parts[0] == "pyfetch":
                custom_neofetch()
            elif command_parts[0] == "ollama":
                run_ollama(command_parts)
            elif command_parts[0] == "echo":
                if len(command_parts) > 1:
                    print(" ".join(command_parts[1:]))
                else:
                    print()
            elif command_parts[0] == "tetris":
                try:
                    subprocess.run(["python", "tetris.py"])
                except FileNotFoundError:
                    print("Error: tetris.py not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif command_parts[0] == "image":
                try:
                    subprocess.run(["python", "image.py"])
                except FileNotFoundError:
                    print("Error: image.py not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif command_parts[0] == "iusepybtw":
                print("I use PyOS Btw")
                custom_neofetch()
            elif command_parts[0] == "flappybird":
                try:
                    subprocess.run(["python", "flap.py"])
                except FileNotFoundError:
                    print("Error: flap.py not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif command_parts[0] == "calculator":
                try:
                    subprocess.run(["python", "calculator.py"])
                except FileNotFoundError:
                    print("Error: calculator.py not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif command_parts[0] == "snake":
                try:
                    subprocess.run(["python", "snake.py"])
                except FileNotFoundError:
                    print("Error: snake.py not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif command_parts[0] == "pyinstall":
                if len(command_parts) == 2:
                    new_command = install_script(command_parts[1])
                    if new_command is not None: #check if the returned command is not None
                        installed_commands.append(new_command) #add to list
                        save_installed_commands(installed_commands) #save the list
                else:
                    print("Usage: pyinstall <script_name.py>")
            elif command_parts[0] in installed_commands: #check if command is in the list
                try:
                    subprocess.run(["python", f"{command_parts[0]}.py"])
                except FileNotFoundError:
                    print(f"Error: {command_parts[0]}.py not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                print("Unknown command.")
        elif current_command.strip() != "":
            print("Unknown command.")

        readline.set_startup_hook(None) # clear readline

    listener.stop()

if __name__ == "__main__":
    fake_os()