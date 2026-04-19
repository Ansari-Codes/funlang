import sys
import os
import tempfile
import subprocess
from .transpiler import transpile
from .errors import FLangError


def main():
    if len(sys.argv) < 2:
        print("FLang Interpreter")
        print("Usage: python -m flang <file.fun>")
        print("       python -m flang --transpile <file.fun>   (show Python code only)")
        sys.exit(1)

    show_only = False
    filename = sys.argv[1]

    if sys.argv[1] == "--transpile" and len(sys.argv) >= 3:
        show_only = True
        filename = sys.argv[2]

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

    if show_only:
        print(py_code)
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(py_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=False,
        )
        sys.exit(result.returncode)
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
