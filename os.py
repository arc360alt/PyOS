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
    print(f"Version: 0.3b")
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

def uninstall_package(pkg_name, installed_commands):
    """Uninstalls a package installed via pyinstall or pypkg."""

    default_commands = ["help", "hello", "about", "exit", "clear", "time", "pyfetch", 
                        "ollama", "echo", "tetris", "image", "flappybird", "calculator", 
                        "snake", "pyinstall", "pypkg", "pyremove"]

    if pkg_name in default_commands:
        print(f"\033[31m  >> '{pkg_name}' is a built-in command and cannot be removed.\033[0m")
        return

    if pkg_name not in installed_commands:
        print(f"\033[31m  >> '{pkg_name}' is not an installed command.\033[0m")
        return

    removed_anything = False

    # Remove the .py script file if it exists in the current directory
    script_path = os.path.join(os.getcwd(), f"{pkg_name}.py")
    if os.path.exists(script_path):
        try:
            os.remove(script_path)
            print(f"\033[32m  >> Removed script file '{pkg_name}.py'.\033[0m")
            removed_anything = True
        except Exception as e:
            print(f"\033[31m  >> Could not remove script file: {e}\033[0m")

    # Remove the wrapper command from ~/.local/bin or /usr/local/bin
    for install_dir in [os.path.expanduser("~/.local/bin"), "/usr/local/bin"]:
        wrapper_path = os.path.join(install_dir, pkg_name)
        if os.path.exists(wrapper_path):
            try:
                os.remove(wrapper_path)
                print(f"\033[32m  >> Removed command wrapper from '{install_dir}'.\033[0m")
                removed_anything = True
            except Exception as e:
                print(f"\033[31m  >> Could not remove wrapper from '{install_dir}': {e}\033[0m")

    # Remove from installed_commands list and save
    installed_commands.remove(pkg_name)
    save_installed_commands(installed_commands)
    print(f"\033[32m  >> '{pkg_name}' removed from command list.\033[0m")

    if not removed_anything:
        print(f"\033[33m  >> No files were found to delete, but '{pkg_name}' has been unregistered.\033[0m")

    print(f"\033[32m  >> '{pkg_name}' uninstalled successfully.\033[0m")

# package manager starts here

import json
import urllib.request

def run_package_manager(installed_commands):
    """A simple package manager that installs from packages.json"""

    PACKAGES_FILE = "packages.json"

    def load_packages():
        if not os.path.exists(PACKAGES_FILE):
            print("\033[31mError: packages.json not found.\033[0m")
            return None
        try:
            with open(PACKAGES_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("\033[31mError: packages.json is malformed.\033[0m")
            return None

    def list_packages(packages):
        print("\033[36m╔══════════════════════════════════════╗\033[0m")
        print("\033[36m║        PyOS Package Manager          ║\033[0m")
        print("\033[36m╚══════════════════════════════════════╝\033[0m")
        print(f"  {'NAME':<20} {'DESCRIPTION'}")
        print(f"  {'────':<20} {'───────────'}")
        for pkg in packages:
            name = pkg.get("name", "?")
            desc = pkg.get("description", "No description")
            print(f"  \033[33m{name:<20}\033[0m {desc}")
        print()

    def install_package(packages, pkg_name, installed_commands):
        match = next((p for p in packages if p["name"] == pkg_name), None)
        if not match:
            print(f"\033[31mPackage '{pkg_name}' not found. Run 'pypkg list' to see available packages.\033[0m")
            return

        url = match.get("url")
        filename = match.get("file", pkg_name + ".py")

        if not url:
            print(f"\033[31mError: No URL defined for package '{pkg_name}'.\033[0m")
            return

        # Install pip dependencies first
        dependencies = match.get("dependencies", [])
        if dependencies:
            print(f"\033[36m  >> Installing {len(dependencies)} dependency/dependencies...\033[0m")
            for dep in dependencies:
                print(f"\033[36m  >> Installing '{dep}'...\033[0m", end="", flush=True)
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", dep],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"\r\033[32m  >> '{dep}' installed.          \033[0m")
                    else:
                        print(f"\r\033[31m  >> '{dep}' failed.             \033[0m")
                        print(f"\033[31m     {result.stderr.splitlines()[-1]}\033[0m")
                except Exception as e:
                    print(f"\r\033[31m  >> '{dep}' error: {e}\033[0m")
            print()

        print(f"\033[36m  >> Fetching '{pkg_name}'...\033[0m")

        try:
            def progress_hook(count, block_size, total_size):
                if total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    percent = min(percent, 100)
                    bar = ("█" * (percent // 5)).ljust(20)
                    print(f"\r  \033[32m[{bar}] {percent}%\033[0m", end="", flush=True)

            urllib.request.urlretrieve(url, filename, reporthook=progress_hook)
            print()  # newline after progress bar
            print(f"\033[32m  >> '{pkg_name}' installed successfully as '{filename}'.\033[0m")

            # Register the command if it's a .py file
            cmd_name = filename[:-3] if filename.endswith(".py") else filename
            if cmd_name not in installed_commands:
                installed_commands.append(cmd_name)
                save_installed_commands(installed_commands)
                print(f"\033[32m  >> Command '{cmd_name}' is now available.\033[0m")

        except Exception as e:
            print(f"\n\033[31m  >> Failed to install '{pkg_name}': {e}\033[0m")

    # --- Package manager UI loop ---
    packages = load_packages()
    if packages is None:
        return

    print()
    print("\033[36m  PyOS Package Manager  |  type 'help' for commands, 'exit' to quit\033[0m")
    print()

    while True:
        try:
            cmd = input("\033[35mpypkg>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd == "exit" or cmd == "quit":
            break
        elif cmd == "help":
            print("  list              - Show all available packages")
            print("  install <name>    - Install a package")
            print("  exit              - Exit the package manager")
        elif cmd == "list":
            list_packages(packages)
        elif cmd.startswith("install "):
            pkg_name = cmd[8:].strip()
            if pkg_name:
                install_package(packages, pkg_name, installed_commands)
            else:
                print("  Usage: install <package_name>")
        elif cmd == "":
            pass
        else:
            print(f"  Unknown command '{cmd}'. Type 'help' for help.")

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
                return None

        install_path = os.path.join(install_dir, command_name)

        # wrapper thing
        with open(install_path, "w") as wrapper_script:
            wrapper_script.write(f"#!/usr/bin/env python3\n")
            wrapper_script.write(f"import os\n")
            wrapper_script.write(f"os.chdir(r'{os.getcwd()}')\n")  # change dir
            wrapper_script.write(f"import {command_name}\n")

        os.chmod(install_path, 0o755)  # execute ts

        print(f"Script '{script_name}' installed as command '{command_name}' in {install_dir}")
        return command_name  # Return command_name after successful installation

    elif os.name == 'nt':  # Windows
        install_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs")  # add to start menu
        install_path = os.path.join(install_dir, f"{command_name}.bat")  # create bat file
        with open(install_path, "w") as bat_file:
            bat_file.write(f"@echo off\n")
            bat_file.write(f"python \"{os.path.join(os.getcwd(), script_name)}\" %*\n")  # run python script

        print(f"Script '{script_name}' installed as command '{command_name}' in {install_dir}")
        return command_name  # Return command_name after successful installation

    else:
        print("Error: Unsupported operating system.")
        return None  # return nothing on error

def load_installed_commands():
    try:
        with open("installed_commands.txt", "r") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        default_commands = ["help", "hello", "about", "exit", "clear", "time", "pyfetch", "ollama", "echo", "tetris", "image", "flappybird", "calculator", "snake", "pyinstall", "pypkg", "pyremove"]
        save_installed_commands(default_commands)
        return default_commands

def save_installed_commands(commands):
    """Saves installed commands to a file."""
    with open("installed_commands.txt", "w") as f:
        for command in commands:
            f.write(command + "\n")

def fake_os():

    os_name = "PyOS Mini Console"
    rainbow_print(os_name + "\n")
    rainbow_print("version 0.3 beta\n")
    rainbow_print("https://arc360hub.com (c) 2020-2026\n")
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
            elif command_parts[0] == "pyremove":
                if len(command_parts) == 2:
                    confirm = input(f"  Are you sure you want to remove '{command_parts[1]}'? (y/n): ").strip().lower()
                    if confirm == "y":
                        uninstall_package(command_parts[1], installed_commands)
                    else:
                        print("  Uninstall cancelled.")
                else:
                    print("  Usage: pyremove <package_name>")
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
            elif command_parts[0] == "pypkg":
                run_package_manager(installed_commands)
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
