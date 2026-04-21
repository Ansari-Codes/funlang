class FLangError(Exception):
    def __init__(self, message, line=None):
        self.line = line
        self.message = message
        loc = f" (line {line})" if line is not None else ""
        full = f"Uh oh!{loc} {message}"
        super().__init__(full)


def unknown_token_error(token, line=None):
    return FLangError(
        f"I don't understand '{token}'. Did you make a typo? Check your spelling!",
        line,
    )


def unexpected_token_error(expected, got, line=None):
    return FLangError(
        f"I was expecting '{expected}' but got '{got}' instead. Something looks off!",
        line,
    )


def undefined_variable_error(name, line=None):
    return FLangError(
        f"I can't find a variable called '{name}'. Did you forget to SET it first?",
        line,
    )


def undefined_function_error(name, line=None):
    return FLangError(
        f"I don't know any function called '{name}'. Did you DEF it before using it?",
        line,
    )


def wrong_type_error(expected, got, line=None):
    return FLangError(
        f"I was expecting a {expected} but got a {got}. Types need to match!",
        line,
    )


def index_out_of_range_error(index, length, line=None):
    return FLangError(
        f"Whoops! You tried to access index {index} but the array only has {length} item(s). Remember, arrays start at 0!",
        line,
    )


def missing_colon_error(keyword, line=None):
    return FLangError(
        f"The '{keyword}' block needs a colon ':' at the end. Add it and try again!",
        line,
    )


def indent_error(line=None):
    return FLangError(
        "Indentation problem! Make sure the code inside blocks is indented (use spaces).",
        line,
    )


def invalid_assignment_error(target, line=None):
    return FLangError(
        f"I can't assign to '{target}'. You can only SET variables or array items!",
        line,
    )


def missing_to_error(line=None):
    return FLangError(
        "Missing TO in the SET statement. It should look like: SET x TO 5",
        line,
    )


def missing_as_error(line=None):
    return FLangError(
        "Missing AS in the FOR loop. It should look like: FOR arr AS i",
        line,
    )


def bad_function_def_error(line=None):
    return FLangError(
        "Function definition looks wrong. It should be: DEF myFunc(a, b):",
        line,
    )


def ask_type_error(typename, line=None):
    return FLangError(
        f"'{typename}' is not a valid ASK type. Use INT, FLOAT, or STR.",
        line,
    )
