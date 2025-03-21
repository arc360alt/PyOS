# PyOS (BETA, PLEASE REPORT ISSUES)
A Fake gaming console made in python.

## Requierments:
- Git
- Python (3.13 or newer)
- Pip (3.13)
- *Ollama* (If you want to use the included ollama intigration, not requiered)

## Installation (Linux and Maybe Windows)
- ```git clone https://github.com/arc360alt/PyOS.git```

- ```cd PyOS```

- ```pip install -r requirements.txt``` (ON LINUX)

- ```pip install -r requierments-win.txt``` (ON WINDOWS)

- ```python os.py```

## How to develop apps/games and publish them
This fake console runs on python, so all you have to do is make a TUI or GUI app/game, and upload it onto github or a store i might make in the future, and the user can just run "pyinstall yourapp.py" to install your app as a command onto the system, the command will be the python file name w/o the .py ending.

## Included Commands
- help, included commands
- hello, simple test command
- about, discription of the os n stuff
- exit, exit's you from PyOS
- clear, clears the console
- time, current time
- pyfetch, your system info (spin on neofetch)
- ollama, Ai chatbot (needs ollama to be installed on host)
- echo, echos whatever you type after the echo command
- tetris, a simple TUI tetris game
- image, turns a PNG or JPG image into Color ascii art
- flappybird, TUI flappybird game
- calculator, self explanitory, TUI
- snake, simple snake game
- pyinstall, how you install outside apps.

## How to use pyinstall
All you have to do is download a game or app from a store i may make in the future or just any game or app made or not made for this that has a .py extention, drag that .py file into the PyOS directory, then run "pyinstall APPNAME.py" replace APPNAME whith the name of the python file you had just put into the PyOS file, and that will install that app as a command, that command is just the python file name whithout the .py extention, example, tetris.py would become just tetris as a command.

### Summary:

- Put downloaded python file into PyOS directory (usaly found in your home directory or users directory on windows)
- In PyOS, run ```pyinstall APP.PY``` making app.py the name of the app you just moved into the PyOS dir
- Then run the python files name whithout the .py extention, for example app.py would just become app as a command.
