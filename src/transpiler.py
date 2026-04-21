from typing import List
from .parser import Node, parse
from .fun_builtins import Builtins, BUILTIN_IMPLEMENTATIONS
from .errors import FLangError


OP_MAP = {
    "=":  "==",
    "&":  "and",
    "|":  "or",
    "!":  "not",
    ">":  ">",
    "<":  "<",
    ">=": ">=",
    "<=": "<=",
    "!=": "!=",
    "+":  "+",
    "-":  "-",
    "*":  "*",
    "**": "**",
    "/":  "/",
    "//": "//",
    "%":  "%",
}

INDENT = "    "


def _prefix(name: str) -> str:
    if name in Builtins:
        return Builtins[name]
    return f"fun_{name}"


def _fmt_string(raw: str) -> str:
    parts = raw.split("{")
    if len(parts) == 1:
        return repr(raw)
    result = 'f"'
    for i, part in enumerate(parts):
        if i == 0:
            result += part.replace('"', '\\"')
        else:
            if "}" in part:
                expr_part, rest = part.split("}", 1)
                result += "{" + _prefix(expr_part.strip()) + "}"
                result += rest.replace('"', '\\"')
            else:
                result += "{" + part.replace('"', '\\"')
    result += '"'
    return result


def emit_expr(node: Node) -> str:
    if node.kind == "number":
        return repr(node.value)

    if node.kind == "string":
        raw = node.value
        if "{" in raw:
            return _fmt_string(raw)
        return repr(raw)

    if node.kind == "bool":
        return "True" if node.value else "False"

    if node.kind == "ident":
        return _prefix(node.value)

    if node.kind == "array":
        items = ", ".join(emit_expr(c) for c in node.children)
        return f"[{items}]"

    if node.kind == "index":
        obj = emit_expr(node.children[0])
        idx = emit_expr(node.children[1])
        return f"{obj}[{idx}]"

    if node.kind == "call":
        func_name = _prefix(node.value)
        args = ", ".join(emit_expr(c) for c in node.children)
        return f"{func_name}({args})"

    if node.kind == "binop":
        left = emit_expr(node.children[0])
        right = emit_expr(node.children[1])
        op = OP_MAP.get(node.value, node.value)
        return f"({left} {op} {right})"

    if node.kind == "unop":
        operand = emit_expr(node.children[0])
        if node.value == "!":
            return f"(not {operand})"
        if node.value == "-":
            return f"(-{operand})"

    if node.kind == "cast":
        inner = emit_expr(node.children[0])
        return f"{node.value}({inner})"

    if node.kind == "ask":
        ask_type, prompt = node.value
        if ask_type == "int":
            return f"int(input({repr(prompt)}))"
        elif ask_type == "float":
            return f"float(input({repr(prompt)}))"
        else:
            return f"input({repr(prompt)})"

    raise FLangError(f"I don't know how to emit expression of kind '{node.kind}'", node.line)


def emit_stmt(node: Node, depth: int) -> List[str]:
    pad = INDENT * depth
    lines = []

    if node.kind == "set":
        target = _prefix(node.children[0].value)
        val = emit_expr(node.children[1])
        lines.append(f"{pad}{target} = {val}")

    elif node.kind == "set_index":
        obj = _prefix(node.children[0].value)
        idx = emit_expr(node.children[1])
        val = emit_expr(node.children[2])
        lines.append(f"{pad}{obj}[{idx}] = {val}")

    elif node.kind == "disp":
        val = emit_expr(node.children[0])
        lines.append(f"{pad}print({val})")

    elif node.kind == "if":
        for bi, branch in enumerate(node.children):
            if branch.kind == "if_branch":
                cond = emit_expr(branch.children[0])
                lines.append(f"{pad}if {cond}:")
                for stmt in branch.children[1:]:
                    lines.extend(emit_stmt(stmt, depth + 1))
            elif branch.kind == "elif_branch":
                cond = emit_expr(branch.children[0])
                lines.append(f"{pad}elif {cond}:")
                for stmt in branch.children[1:]:
                    lines.extend(emit_stmt(stmt, depth + 1))
            elif branch.kind == "else_branch":
                lines.append(f"{pad}else:")
                for stmt in branch.children:
                    lines.extend(emit_stmt(stmt, depth + 1))
        if not node.children:
            lines.append(f"{pad}if True:")
            lines.append(f"{pad}{INDENT}pass")

    elif node.kind == "for_iter":
        var = _prefix(node.children[0].value)
        iterable = emit_expr(node.children[1])
        body_nodes = node.children[2:]
        lines.append(f"{pad}for {var} in {iterable}:")
        for stmt in body_nodes:
            lines.extend(emit_stmt(stmt, depth + 1))
        if not body_nodes:
            lines.append(f"{pad}{INDENT}pass")

    elif node.kind == "while":
        cond = emit_expr(node.children[0])
        body_nodes = node.children[1:]
        lines.append(f"{pad}while {cond}:")
        for stmt in body_nodes:
            lines.extend(emit_stmt(stmt, depth + 1))
        if not body_nodes:
            lines.append(f"{pad}{INDENT}pass")

    elif node.kind == "def":
        fname = _prefix(node.children[0].value)
        params = [_prefix(c.value) for c in node.children if c.kind == "param"]
        body_nodes = [c for c in node.children[1:] if c.kind not in ("param",)]
        lines.append(f"{pad}def {fname}({', '.join(params)}):")
        for stmt in body_nodes:
            lines.extend(emit_stmt(stmt, depth + 1))
        if not body_nodes:
            lines.append(f"{pad}{INDENT}pass")

    elif node.kind == "return":
        val = emit_expr(node.children[0])
        lines.append(f"{pad}return {val}")

    elif node.kind == "break":
        lines.append(f"{pad}break")

    elif node.kind == "continue":
        lines.append(f"{pad}continue")

    elif node.kind == "expr_stmt":
        val = emit_expr(node.children[0])
        lines.append(f"{pad}{val}")

    else:
        raise FLangError(f"Unknown statement kind '{node.kind}'", node.line)
    return lines


def transpile(source: str) -> str:
    ast = parse(source)
    code_lines = [BUILTIN_IMPLEMENTATIONS, ""]
    for node in ast:
        code_lines.extend(emit_stmt(node, 0))
    return "\n".join(code_lines)
