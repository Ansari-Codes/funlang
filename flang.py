import sys
import os
from src.transpiler import transpile
from src.errors import FLangError


def main():
    if len(sys.argv) < 2:
        print("FLang Interpreter")
        print("Usage: flang <file.fun>")
        print("       flang --transpile <file.fun>   (show Python code only)")
        print("       flang -o <output.py> <file.fun>   (write transpiled code to file and run)")
        print("       flang --transpile -o <output.py> <file.fun>   (write and show, no run)")
        sys.exit(1)

    show_only = False
    output_file = None
    filename = None
    
    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--transpile":
            show_only = True
        elif arg == "-o":
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 1  # Skip the next argument (the filename)
            else:
                print("Error: -o flag requires an output filename")
                sys.exit(1)
        else:
            filename = arg
        i += 1
    
    if not filename:
        print("Error: No input file specified")
        print("Usage: python -m flang <file.fun>")
        sys.exit(1)

    if not os.path.exists(filename):
        print(f"Uh oh! I can't find the file '{filename}'. Are you sure it exists?")
        sys.exit(1)

    with open(filename, "r") as f:
        source = f.read()

    try:
        py_code = transpile(source)
    except FLangError as e:
        print(str(e))
        sys.exit(1)

    # Write to output file if specified (but don't use it for execution)
    if output_file:
        try:
            with open(output_file, "w") as f:
                f.write(py_code)
            print(f"Transpiled code written to: {output_file}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            sys.exit(1)

    if show_only:
        print(py_code)
        return

    # Always execute the transpiled Python code directly using exec
    try:
        exec_globals = {
            '__name__': '__main__',
            '__file__': filename,
        }
        exec(py_code, exec_globals)
    except Exception as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()