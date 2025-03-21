import os
import shutil
import sys

def install_script(script_name):
    """Installs a Python script as a command."""

    if not script_name.endswith(".py"):
        print("Error: Script name must end with '.py'")
        return

    if not os.path.exists(script_name):
        print(f"Error: Script '{script_name}' not found.")
        return

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

        # Create a wrapper script with the correct shebang
        with open(install_path, "w") as wrapper_script:
            wrapper_script.write(f"#!/usr/bin/env python3\n")
            wrapper_script.write(f"import os\n")
            wrapper_script.write(f"os.chdir(r'{os.getcwd()}')\n") #change dir
            wrapper_script.write(f"import {command_name}\n")

        os.chmod(install_path, 0o755)  # Make the wrapper executable

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: pyinstall <script_name.py>")
    else:
        install_script(sys.argv[1])