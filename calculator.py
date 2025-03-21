import math
import curses

def calculator_tui(stdscr):
    """Creates a simple calculator TUI."""

    stdscr.clear()
    stdscr.refresh()

    expression = ""
    result = "0"
    history = []  # Store calculation history

    def print_display(display_str):
        stdscr.clear()
        stdscr.addstr(0, 0, "Calculator")
        stdscr.addstr(2, 0, f"Expression: {expression}")
        stdscr.addstr(3, 0, f"Result: {result}")
        stdscr.addstr(5, 0, "History:")
        for i, h in enumerate(history):
            stdscr.addstr(6 + i, 2, h)
        stdscr.refresh()

    def evaluate_expression(expr):
        try:
            expr = expr.replace("^", "**")
            expr = expr.replace("sqrt", "math.sqrt")
            expr = expr.replace("sin", "math.sin")
            expr = expr.replace("cos", "math.cos")
            expr = expr.replace("tan", "math.tan")
            expr = expr.replace("log10", "math.log10")
            expr = expr.replace("log", "math.log")
            expr = expr.replace("factorial", "math.factorial")
            expr = expr.replace("pi", str(math.pi))
            expr = expr.replace("e", str(math.e))
            expr = expr.replace("abs", "abs")
            expr = expr.replace("floor", "math.floor")
            expr = expr.replace("ceil", "math.ceil")
            return eval(expr)
        except (SyntaxError, TypeError, ValueError, ZeroDivisionError):
            return "Error"

    print_display(result)

    while True:
        key = stdscr.getch()

        if key == ord('\n'):  # Enter key
            res = evaluate_expression(expression)
            history.insert(0, f"{expression} = {res}") #insert the calculation to the history
            if len(history) > 10: # Only keep the last 10 calculations
                history.pop()
            result = str(res)
            expression = str(res) #continue calculations
            print_display(result)
        elif key == 27:  # Escape key
            break
        elif key == ord('c') or key == ord('C'): #clear
            expression = ""
            result = "0"
            print_display(result)
        elif key == curses.KEY_BACKSPACE or key == 127: #backspace
            expression = expression[:-1]
            print_display(result)
        elif key == ord('q') or key == ord('Q'): #quit
            break
        elif key == ord('s') or key == ord('S'):
            expression += "sqrt("
            print_display(result)
        elif key == ord('i') or key == ord('I'):
            expression += "sin("
            print_display(result)
        elif key == ord('o') or key == ord('O'):
            expression += "cos("
            print_display(result)
        elif key == ord('t') or key == ord('T'):
            expression += "tan("
            print_display(result)
        elif key == ord('l') or key == ord('L'):
            expression += "log10("
            print_display(result)
        elif key == ord('n') or key == ord('N'):
            expression += "log("
            print_display(result)
        elif key == ord('!'):
            expression += "factorial("
            print_display(result)
        elif key == ord('p') or key == ord('P'):
            expression += str(math.pi)
            print_display(result)
        elif key == ord('e'):
            expression += str(math.e)
            print_display(result)
        elif key == ord('a') or key == ord('A'):
            expression += "abs("
            print_display(result)
        elif key == ord('f') or key == ord('F'):
            expression += "floor("
            print_display(result)
        elif key == ord('g') or key == ord('G'):
            expression += "ceil("
            print_display(result)
        elif chr(key) in "0123456789+-*/().^":
            expression += chr(key)
            print_display(result)

curses.wrapper(calculator_tui)