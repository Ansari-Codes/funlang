import re
from dataclasses import dataclass
from typing import List, Optional
from .errors import unknown_token_error, FLangError

KEYWORDS = {
    "SET", "TO", "DISP", "IF", "ELIF", "ELSE", "FOR", "AS",
    "WHILE", "END", "NEXT", "DEF", "RETURN", "ASK", "INT", "FLOAT", "STR",
    "BOOL", "TRUE", "FALSE", "AND", "OR", "NOT",
}

TOKEN_PATTERNS = [
    ("COMMENT",    r"--[^\n]*"),
    ("NEWLINE",    r"\n"),
    ("INDENT",     r"^[ \t]+"),
    ("NUMBER",     r"\d+\.\d+|\d+"),
    ("STRING",     r'"(?:[^"\\]|\\.)*"'),
    ("BOOL",       r"\b(TRUE|FALSE)\b"),
    ("LBRACKET",   r"\["),
    ("RBRACKET",   r"\]"),
    ("LPAREN",     r"\("),
    ("RPAREN",     r"\)"),
    ("COMMA",      r","),
    ("COLON",      r":"),
    ("OP",         r"\*\*|//|>=|<=|!=|[+\-*/%><=!&|]"),
    ("IDENT",      r"[A-Za-z_][A-Za-z0-9_]*"),
    ("WHITESPACE", r"[ \t]+"),
]

COMPILED = [(name, re.compile(pat)) for name, pat in TOKEN_PATTERNS
            if name not in ("INDENT",)]


@dataclass
class Token:
    type: str
    value: str
    line: int


def tokenize(source: str) -> List[Token]:
    tokens: List[Token] = []
    lines = source.split("\n")
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line
        col = 0

        if line.strip() == "" or line.strip().startswith("--"):
            continue

        indent_match = re.match(r"^([ \t]+)", line)
        indent_val = indent_match.group(1) if indent_match else ""

        tokens.append(Token("INDENT", indent_val, lineno))

        pos = 0
        while pos < len(line):
            matched = False
            for name, pattern in COMPILED:
                m = pattern.match(line, pos)
                if m:
                    val = m.group(0)
                    if name == "COMMENT":
                        pos = len(line)
                        matched = True
                        break
                    if name == "WHITESPACE":
                        pos += len(val)
                        matched = True
                        break
                    if name == "NEWLINE":
                        pos += len(val)
                        matched = True
                        break
                    if name == "IDENT" and val in KEYWORDS:
                        tokens.append(Token(val, val, lineno))
                    elif name == "BOOL":
                        tokens.append(Token("BOOL", val, lineno))
                    else:
                        tokens.append(Token(name, val, lineno))
                    pos += len(val)
                    matched = True
                    break
            if not matched:
                raise unknown_token_error(line[pos], lineno)

        tokens.append(Token("NEWLINE", "\n", lineno))

    tokens.append(Token("EOF", "", len(lines) + 1))
    return tokens
