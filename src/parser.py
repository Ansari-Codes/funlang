from dataclasses import dataclass, field
from typing import List, Optional, Any
from .lexer import Token, tokenize
from .errors import (
    FLangError, unexpected_token_error, missing_to_error, missing_as_error,
    bad_for_range_error, bad_function_def_error, missing_colon_error,
    ask_type_error,
)


@dataclass
class Node:
    kind: str
    line: int = 0
    children: List[Any] = field(default_factory=list)
    value: Any = None


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self._skip_indent_newline()

    def _skip_indent_newline(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ("INDENT", "NEWLINE"):
            self.pos += 1

    def peek(self) -> Token:
        i = self.pos
        while i < len(self.tokens) and self.tokens[i].type in ("INDENT", "NEWLINE"):
            i += 1
        if i < len(self.tokens):
            return self.tokens[i]
        return Token("EOF", "", -1)

    def peek_raw(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", "", -1)

    def consume(self, expected_type=None, expected_value=None) -> Token:
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ("INDENT", "NEWLINE"):
            self.pos += 1
        if self.pos >= len(self.tokens):
            tok = Token("EOF", "", -1)
            if expected_type:
                raise unexpected_token_error(expected_type, "end of file", None)
            return tok
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise unexpected_token_error(expected_type, tok.value, tok.line)
        if expected_value and tok.value != expected_value:
            raise unexpected_token_error(expected_value, tok.value, tok.line)
        self.pos += 1
        return tok

    def consume_raw(self) -> Token:
        if self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            self.pos += 1
            return tok
        return Token("EOF", "", -1)

    def _get_indent(self) -> str:
        i = self.pos
        while i < len(self.tokens) and self.tokens[i].type == "NEWLINE":
            i += 1
        if i < len(self.tokens) and self.tokens[i].type == "INDENT":
            return self.tokens[i].value
        return ""

    def _get_current_line_indent(self) -> str:
        i = self.pos
        if i < len(self.tokens) and self.tokens[i].type == "INDENT":
            return self.tokens[i].value
        return ""

    def parse(self) -> List[Node]:
        return self.parse_block("root")

    def parse_block(self, parent_indent: str) -> List[Node]:
        """
        Parse a block of statements. parent_indent is the indentation of the
        block opener (e.g. DEF/IF/WHILE line). Statements must be indented
        MORE than parent_indent. The block ends when we see a line with indent
        <= parent_indent.

        For the root block, parent_indent is "" but we still use the same rule:
        the root is special because root-level statements ARE at "" indent, so
        we track the "block_indent" from the first line and require all lines
        in the block to be at that exact level.
        """
        stmts = []
        block_indent: Optional[str] = None

        while True:
            self._eat_blank_lines()
            if self.pos >= len(self.tokens):
                break
            tok = self.tokens[self.pos]
            if tok.type == "EOF":
                break

            if tok.type == "INDENT":
                curr_indent = tok.value

                if block_indent is None:
                    if len(curr_indent) <= len(parent_indent) and parent_indent != "root":
                        break
                    block_indent = curr_indent

                if curr_indent != block_indent:
                    if len(curr_indent) < len(block_indent):
                        break
                    if len(curr_indent) > len(block_indent):
                        self.pos += 1
                        continue

                self.pos += 1
                stmt = self.parse_statement(block_indent)
                if stmt:
                    stmts.append(stmt)

            elif tok.type == "NEWLINE":
                self.pos += 1
            else:
                if block_indent is None:
                    block_indent = ""
                if block_indent == "":
                    stmt = self.parse_statement("")
                    if stmt:
                        stmts.append(stmt)
                else:
                    break
        return stmts

    def parse_root(self) -> List[Node]:
        return self.parse_block("root")

    def _eat_blank_lines(self):
        while self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            if tok.type == "NEWLINE":
                self.pos += 1
            elif tok.type == "INDENT":
                j = self.pos + 1
                if j < len(self.tokens) and self.tokens[j].type == "NEWLINE":
                    self.pos += 2
                else:
                    break
            else:
                break

    def parse_statement(self, indent: str) -> Optional[Node]:
        tok = self.peek()
        line = tok.line

        if tok.type == "SET":
            return self.parse_set(line)
        elif tok.type == "DISP":
            return self.parse_disp(line)
        elif tok.type == "IF":
            return self.parse_if(indent, line)
        elif tok.type == "FOR":
            return self.parse_for(indent, line)
        elif tok.type == "WHILE":
            return self.parse_while(indent, line)
        elif tok.type == "END":
            self.consume("END")
            self._eat_line_end()
            return Node("break", line)
        elif tok.type == "NEXT":
            self.consume("NEXT")
            self._eat_line_end()
            return Node("continue", line)
        elif tok.type == "DEF":
            return self.parse_def(indent, line)
        elif tok.type == "RETURN":
            return self.parse_return(line)
        elif tok.type == "IDENT":
            return self.parse_expr_or_call_stmt(line)
        elif tok.type == "EOF":
            return None
        else:
            raise FLangError(
                f"I don't know what to do with '{tok.value}' here!",
                line,
            )

    def _eat_line_end(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == "NEWLINE":
            self.pos += 1

    def parse_set(self, line) -> Node:
        self.consume("SET")
        name_tok = self.consume("IDENT")
        name = name_tok.value

        if self.peek().type == "LBRACKET":
            self.consume("LBRACKET")
            idx_expr = self.parse_expr()
            self.consume("RBRACKET")
            if self.peek().type != "TO":
                raise missing_to_error(line)
            self.consume("TO")
            val_expr = self.parse_expr()
            self._eat_line_end()
            return Node("set_index", line, [Node("ident", line, value=name), idx_expr, val_expr])

        if self.peek().type != "TO":
            raise missing_to_error(line)
        self.consume("TO")
        val_expr = self.parse_expr()
        self._eat_line_end()
        return Node("set", line, [Node("ident", line, value=name), val_expr])

    def parse_disp(self, line) -> Node:
        self.consume("DISP")
        expr = self.parse_expr()
        self._eat_line_end()
        return Node("disp", line, [expr])

    def _peek_keyword_at_indent(self, target_indent: str) -> Optional[str]:
        """Look ahead for a keyword at target_indent level without consuming."""
        i = self.pos
        while i < len(self.tokens) and self.tokens[i].type in ("NEWLINE",):
            i += 1
        if i >= len(self.tokens):
            return None
        if self.tokens[i].type == "INDENT":
            ind = self.tokens[i].value
            i += 1
            if i >= len(self.tokens):
                return None
            kw = self.tokens[i]
            if ind == target_indent and kw.type in ("ELIF", "ELSE"):
                return kw.type
        elif self.tokens[i].type in ("ELIF", "ELSE") and target_indent == "":
            return self.tokens[i].type
        return None

    def parse_if(self, indent: str, line: int) -> Node:
        self.consume("IF")
        cond = self.parse_expr()
        if self.peek().type != "COLON":
            raise missing_colon_error("IF", line)
        self.consume("COLON")
        self._eat_line_end()
        body = self.parse_block(indent)
        branches = [Node("if_branch", line, [cond] + body)]

        while True:
            self._eat_blank_lines()
            kw = self._peek_keyword_at_indent(indent)
            if kw is None:
                break
            saved = self.pos
            while self.pos < len(self.tokens) and self.tokens[self.pos].type in ("NEWLINE", "INDENT"):
                self.pos += 1
            tok = self.tokens[self.pos]
            if tok.type == "ELIF":
                self.consume("ELIF")
                elif_cond = self.parse_expr()
                if self.peek().type != "COLON":
                    raise missing_colon_error("ELIF", tok.line)
                self.consume("COLON")
                self._eat_line_end()
                elif_body = self.parse_block(indent)
                branches.append(Node("elif_branch", tok.line, [elif_cond] + elif_body))
            elif tok.type == "ELSE":
                self.consume("ELSE")
                if self.peek().type != "COLON":
                    raise missing_colon_error("ELSE", tok.line)
                self.consume("COLON")
                self._eat_line_end()
                else_body = self.parse_block(indent)
                branches.append(Node("else_branch", tok.line, else_body))
                break
            else:
                self.pos = saved
                break

        return Node("if", line, branches)

    def peek_at_raw(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", "", -1)

    def parse_for(self, indent: str, line: int) -> Node:
        self.consume("FOR")
        tok = self.peek()

        if tok.type == "RANGE":
            self.consume("RANGE")
            args = []
            args.append(self.parse_expr())
            if self.peek().type == "TO":
                self.consume("TO")
                args.append(self.parse_expr())
                if self.peek().type == "STEP":
                    self.consume("STEP")
                    args.append(self.parse_expr())
            if self.peek().type != "AS":
                raise missing_as_error(line)
            self.consume("AS")
            var_tok = self.consume("IDENT")
            if self.peek().type != "COLON":
                raise missing_colon_error("FOR RANGE", line)
            self.consume("COLON")
            self._eat_line_end()
            body = self.parse_block(indent)
            return Node("for_range", line, [Node("ident", line, value=var_tok.value)] + [Node("arg", line, value=a) for a in args] + body)

        else:
            iter_expr = self.parse_expr()
            if self.peek().type != "AS":
                raise missing_as_error(line)
            self.consume("AS")
            var_tok = self.consume("IDENT")
            if self.peek().type != "COLON":
                raise missing_colon_error("FOR", line)
            self.consume("COLON")
            self._eat_line_end()
            body = self.parse_block(indent)
            return Node("for_iter", line, [Node("ident", line, value=var_tok.value), iter_expr] + body)

    def parse_while(self, indent: str, line: int) -> Node:
        self.consume("WHILE")
        cond = self.parse_expr()
        if self.peek().type != "COLON":
            raise missing_colon_error("WHILE", line)
        self.consume("COLON")
        self._eat_line_end()
        body = self.parse_block(indent)
        return Node("while", line, [cond] + body)

    def parse_def(self, indent: str, line: int) -> Node:
        self.consume("DEF")
        name_tok = self.consume("IDENT")
        if self.peek().type != "LPAREN":
            raise bad_function_def_error(line)
        self.consume("LPAREN")
        params = []
        while self.peek().type != "RPAREN":
            p = self.consume("IDENT")
            params.append(Node("param", p.line, value=p.value))
            if self.peek().type == "COMMA":
                self.consume("COMMA")
        self.consume("RPAREN")
        if self.peek().type != "COLON":
            raise missing_colon_error("DEF", line)
        self.consume("COLON")
        self._eat_line_end()
        body = self.parse_block(indent)
        return Node("def", line, [Node("ident", line, value=name_tok.value)] + params + body)

    def parse_return(self, line: int) -> Node:
        self.consume("RETURN")
        expr = self.parse_expr()
        self._eat_line_end()
        return Node("return", line, [expr])

    def parse_expr_or_call_stmt(self, line: int) -> Node:
        expr = self.parse_expr()
        self._eat_line_end()
        return Node("expr_stmt", line, [expr])

    def parse_expr(self) -> Node:
        return self.parse_or()

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.peek().type == "OP" and self.peek().value == "|":
            op_tok = self.consume("OP")
            right = self.parse_and()
            left = Node("binop", op_tok.line, [left, right], value="|")
        return left

    def parse_and(self) -> Node:
        left = self.parse_not()
        while self.peek().type == "OP" and self.peek().value == "&":
            op_tok = self.consume("OP")
            right = self.parse_not()
            left = Node("binop", op_tok.line, [left, right], value="&")
        return left

    def parse_not(self) -> Node:
        if self.peek().type == "OP" and self.peek().value == "!":
            op_tok = self.consume("OP")
            operand = self.parse_not()
            return Node("unop", op_tok.line, [operand], value="!")
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        left = self.parse_addition()
        cmp_ops = {"=", ">", "<", ">=", "<=", "!="}
        while self.peek().type == "OP" and self.peek().value in cmp_ops:
            op_tok = self.consume("OP")
            right = self.parse_addition()
            left = Node("binop", op_tok.line, [left, right], value=op_tok.value)
        return left

    def parse_addition(self) -> Node:
        left = self.parse_multiplication()
        while self.peek().type == "OP" and self.peek().value in ("+", "-"):
            op_tok = self.consume("OP")
            right = self.parse_multiplication()
            left = Node("binop", op_tok.line, [left, right], value=op_tok.value)
        return left

    def parse_multiplication(self) -> Node:
        left = self.parse_power()
        while self.peek().type == "OP" and self.peek().value in ("*", "/", "//", "%"):
            op_tok = self.consume("OP")
            right = self.parse_power()
            left = Node("binop", op_tok.line, [left, right], value=op_tok.value)
        return left

    def parse_power(self) -> Node:
        left = self.parse_unary()
        if self.peek().type == "OP" and self.peek().value == "**":
            op_tok = self.consume("OP")
            right = self.parse_power()
            return Node("binop", op_tok.line, [left, right], value="**")
        return left

    def parse_unary(self) -> Node:
        if self.peek().type == "OP" and self.peek().value == "-":
            op_tok = self.consume("OP")
            operand = self.parse_primary()
            return Node("unop", op_tok.line, [operand], value="-")
        return self.parse_primary()

    def parse_primary(self) -> Node:
        tok = self.peek()

        if tok.type == "NUMBER":
            self.consume("NUMBER")
            val = float(tok.value) if "." in tok.value else int(tok.value)
            return Node("number", tok.line, value=val)

        if tok.type == "STRING":
            self.consume("STRING")
            raw = tok.value[1:-1]
            return Node("string", tok.line, value=raw)

        if tok.type == "BOOL":
            self.consume("BOOL")
            return Node("bool", tok.line, value=tok.value == "TRUE")

        if tok.type == "LBRACKET":
            return self.parse_array_literal(tok.line)

        if tok.type == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expr()
            self.consume("RPAREN")
            return expr

        if tok.type == "ASK":
            return self.parse_ask(tok.line)

        if tok.type == "INT":
            self.consume("INT")
            inner = self.parse_primary()
            return Node("cast", tok.line, [inner], value="int")

        if tok.type == "FLOAT":
            self.consume("FLOAT")
            inner = self.parse_primary()
            return Node("cast", tok.line, [inner], value="float")

        if tok.type == "STR":
            self.consume("STR")
            inner = self.parse_primary()
            return Node("cast", tok.line, [inner], value="str")

        if tok.type == "IDENT":
            self.consume("IDENT")
            name = tok.value

            if self.peek().type == "LPAREN":
                self.consume("LPAREN")
                args = []
                while self.peek().type != "RPAREN":
                    args.append(self.parse_expr())
                    if self.peek().type == "COMMA":
                        self.consume("COMMA")
                self.consume("RPAREN")
                node = Node("call", tok.line, args, value=name)
            else:
                node = Node("ident", tok.line, value=name)

            while self.peek().type == "LBRACKET":
                self.consume("LBRACKET")
                idx = self.parse_expr()
                self.consume("RBRACKET")
                node = Node("index", tok.line, [node, idx])
            return node

        raise FLangError(
            f"I was expecting a value but got '{tok.value}'. Check your expression!",
            tok.line,
        )

    def parse_array_literal(self, line: int) -> Node:
        self.consume("LBRACKET")
        items = []
        while self.peek().type != "RBRACKET":
            items.append(self.parse_expr())
            if self.peek().type == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACKET")
        return Node("array", line, items)

    def parse_ask(self, line: int) -> Node:
        self.consume("ASK")
        type_tok = self.peek()
        if type_tok.type not in ("INT", "FLOAT", "STR"):
            raise ask_type_error(type_tok.value, line)
        self.consume(type_tok.type)
        prompt_tok = self.peek()
        if prompt_tok.type == "STRING":
            self.consume("STRING")
            prompt = prompt_tok.value[1:-1]
        else:
            prompt = ""
        return Node("ask", line, value=(type_tok.value.lower(), prompt))


def parse(source: str) -> List[Node]:
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
