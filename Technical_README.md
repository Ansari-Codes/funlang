# 🔧 FLang Technical Documentation

## Overview
FLang is a Domain Specific Language (DSL) designed for educational purposes. It features a SQL-like syntax with Python-inspired control structures. The interpreter acts as a transpiler, converting FLang source code into Python source code, which is then executed dynamically.

## Architecture
1.  **Lexer/Parser**: The FLang interpreter reads the raw script, tokenizing keywords (`SET`, `IF`, `TO`) and operators.
2.  **Transpiler**: The core engine translates FLang syntax into valid Python 3 code.
3.  **Runtime**: The generated Python code is executed using `exec()` within a controlled environment that includes the standard library and custom built-in functions.
4.  **Error Handling**: The system wraps execution in try-except blocks to capture Python exceptions and re-raise them as user-friendly FLang error messages.

## Syntax Reference

### Variable Declaration
FLang uses explicit assignment.
*   **Syntax**: `SET <identifier> TO <expression>`
*   **Transpilation**: `<identifier> = <expression>`

### Operators
FLang supports standard mathematical and logical operators.
*   **Math**: `+`, `-`, `*`, `**`, `/`, `//`, `%`
*   **Comparison**: `=`, `>`, `<`, `>=`, `<=`
*   **Logical**: `&` (and), `|` (or), `!` (not)

### Control Structures

#### Conditionals
Structure requires colons and indentation (implicit in Python).
```sql
IF condition:
    ...
ELIF condition:
    ...
ELSE:
    ...
```
*   **Note**: The equality check `=` in FLang is transpiled to Python `==`.

#### Loops
**For Loop**:
```sql
FOR iterable AS var:
    ...
```
**While Loop**:
```sql
WHILE condition:
    ...
```

#### Flow Control
*   **`NEXT`**: Transpiled to `continue`.
*   **`END`**: Transpiled to `break`.

### Functions
Functions are defined using `DEF` and support arguments.
```sql
DEF func_name(arg1, arg2):
    RETURN result
```

### Input / Output
*   **`DISP`**: Transpiled to `print(...)`.
*   **`ASK`**: Transpiled to `input(...)` with type casting logic.
    *   `ASK INT "Prompt"` -> `int(input("Prompt"))`

## Standard Library (Built-ins)
The FLang environment is populated with the following built-in functions prior to code execution. These map to Python's standard library or custom helper functions.

| FLang Function | Python Equivalent | Description |
| :--- | :--- | :--- |
| **String Utils** | | |
| `strlower` | `str.lower()` | Converts string to lowercase. |
| `strupper` | `str.upper()` | Converts string to uppercase. |
| `strlen` | `len()` | Returns string length. |
| `strreplace` | `str.replace()` | Replaces substrings. |
| `strsplit` | `str.split()` | Splits string by delimiter. |
| `strcontains` | `in` operator | Checks for substring. |
| `strstarts` | `str.startswith()` | Checks prefix. |
| `strends` | `str.endswith()` | Checks suffix. |
| **Math Utils** | | |
| `abs` | `abs()` | Absolute value. |
| `round` | `round()` | Rounds number. |
| `floor` | `math.floor()` | Rounds down. |
| `ceil` | `math.ceil()` | Rounds up. |
| `max` | `max()` | Maximum value. |
| `min` | `min()` | Minimum value. |
| `sum` | `sum()` | Sum of iterable. |
| `random` | `random.random()` | Random float [0.0, 1.0). |
| `randint` | `random.randint()` | Random integer in range. |
| **List/Array Utils** | | |
| `len` | `len()` | Length of iterable. |
| `range` | `range()` | Generates number sequence. |
| `sort` | `sorted()` | Returns sorted list. |
| `reverse` | `list.reverse()` | Reverses list in-place. |
| `append` | `list.append()` | Appends item to list. |
| `pop` | `list.pop()` | Removes and returns item. |
| **Type Utils** | | |
| `type` | `type()` | Returns type of object. |
| `tostr` | `str()` | Casts to string. |
| `toint` | `int()` | Casts to integer. |
| `tofloat` | `float()` | Casts to float. |

## Error Handling Strategy
Since FLang transpiles to Python, runtime errors (like `NameError`, `TypeError`, `IndentationError`) will naturally occur in Python. The FLang runtime catches these exceptions and maps them back to the FLang context where possible, providing simplified error messages suitable for beginners.