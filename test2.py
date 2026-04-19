"""
Tests that mirror the exact syntax examples from the FLang spec document.
Each test group maps directly to a section of the spec.
"""
import sys
import os
import textwrap
import unittest
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flang import transpile, FLangError


def run_flang(source: str, stdin: str = "") -> str:
    source = textwrap.dedent(source).strip()
    py_code = transpile(source)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(py_code)
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, tmp],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Execution failed:\n{result.stderr}")
        return result.stdout
    finally:
        os.unlink(tmp)


def transpile_ok(source: str) -> str:
    return transpile(textwrap.dedent(source).strip())


# ---------------------------------------------------------------------------
# COMMENTS
# ---------------------------------------------------------------------------

class TestComments(unittest.TestCase):
    """-- starts a comment; the rest of the line is ignored."""

    def test_single_comment_ignored(self):
        out = run_flang("""
            -- this is a comment
            SET x TO 7
            DISP x
        """)
        self.assertEqual(out.strip(), "7")

    def test_comment_at_end_of_code(self):
        out = run_flang("""
            SET x TO 3
            DISP x
            -- nothing after this
        """)
        self.assertEqual(out.strip(), "3")

    def test_multiple_comments(self):
        out = run_flang("""
            -- line one comment
            -- line two comment
            SET a TO 1
            -- line three comment
            DISP a
        """)
        self.assertEqual(out.strip(), "1")

    def test_comment_only_file(self):
        py = transpile_ok("-- just a comment")
        self.assertNotIn("print", py)

    def test_inline_comment_after_statement(self):
        out = run_flang("""
            SET x TO 42  -- set x to 42
            DISP x       -- display it
        """)
        self.assertEqual(out.strip(), "42")


# ---------------------------------------------------------------------------
# VARIABLES — SET and DISP
# ---------------------------------------------------------------------------

class TestVariablesSyntax(unittest.TestCase):
    """Spec: SET x TO 10  /  DISP x"""

    def test_set_int_disp(self):
        out = run_flang("""
            SET x TO 10
            DISP x
        """)
        self.assertEqual(out.strip(), "10")

    def test_set_float(self):
        out = run_flang("""
            SET pi TO 3.14159
            DISP pi
        """)
        self.assertEqual(out.strip(), "3.14159")

    def test_set_string(self):
        out = run_flang("""
            SET name TO "Alice"
            DISP name
        """)
        self.assertEqual(out.strip(), "Alice")

    def test_set_bool_true(self):
        out = run_flang("""
            SET flag TO TRUE
            DISP flag
        """)
        self.assertEqual(out.strip(), "True")

    def test_set_bool_false(self):
        out = run_flang("""
            SET flag TO FALSE
            DISP flag
        """)
        self.assertEqual(out.strip(), "False")

    def test_set_expression(self):
        out = run_flang("""
            SET x TO 5 + 3
            DISP x
        """)
        self.assertEqual(out.strip(), "8")

    def test_set_from_variable(self):
        out = run_flang("""
            SET x TO 10
            SET y TO x
            DISP y
        """)
        self.assertEqual(out.strip(), "10")

    def test_reassign(self):
        out = run_flang("""
            SET x TO 1
            SET x TO x + 1
            DISP x
        """)
        self.assertEqual(out.strip(), "2")

    def test_multiple_variables(self):
        out = run_flang("""
            SET a TO 2
            SET b TO 3
            SET c TO a * b
            DISP c
        """)
        self.assertEqual(out.strip(), "6")

    def test_disp_literal_int(self):
        out = run_flang("DISP 99")
        self.assertEqual(out.strip(), "99")

    def test_disp_literal_string(self):
        out = run_flang('DISP "hello"')
        self.assertEqual(out.strip(), "hello")

    def test_disp_expression(self):
        out = run_flang("DISP 2 + 2")
        self.assertEqual(out.strip(), "4")

    def test_identifiers_are_prefixed(self):
        py = transpile_ok("SET myVar TO 5")
        self.assertIn("fun_myVar = 5", py)

    def test_keywords_are_not_prefixed(self):
        py = transpile_ok("SET x TO 5")
        self.assertNotIn("fun_SET", py)
        self.assertNotIn("fun_TO", py)


# ---------------------------------------------------------------------------
# OPERATORS
# ---------------------------------------------------------------------------

class TestOperators(unittest.TestCase):
    """Spec: + - * ** / // % = > < >= <= & | !"""

    def test_add(self):
        self.assertEqual(run_flang("DISP 3 + 4").strip(), "7")

    def test_sub(self):
        self.assertEqual(run_flang("DISP 10 - 4").strip(), "6")

    def test_mul(self):
        self.assertEqual(run_flang("DISP 6 * 7").strip(), "42")

    def test_pow(self):
        self.assertEqual(run_flang("DISP 2 ** 8").strip(), "256")

    def test_div(self):
        self.assertEqual(run_flang("DISP 7 / 2").strip(), "3.5")

    def test_fdiv(self):
        self.assertEqual(run_flang("DISP 7 // 2").strip(), "3")

    def test_mod(self):
        self.assertEqual(run_flang("DISP 7 % 3").strip(), "1")

    def test_eq(self):
        out = run_flang("""
            SET x TO 5
            IF x = 5:
                DISP "yes"
        """)
        self.assertEqual(out.strip(), "yes")

    def test_gt(self):
        out = run_flang("""
            IF 10 > 5:
                DISP "gt"
        """)
        self.assertEqual(out.strip(), "gt")

    def test_lt(self):
        out = run_flang("""
            IF 3 < 7:
                DISP "lt"
        """)
        self.assertEqual(out.strip(), "lt")

    def test_geq(self):
        out = run_flang("""
            IF 5 >= 5:
                DISP "geq"
        """)
        self.assertEqual(out.strip(), "geq")

    def test_seq(self):
        out = run_flang("""
            IF 4 <= 5:
                DISP "seq"
        """)
        self.assertEqual(out.strip(), "seq")

    def test_and(self):
        out = run_flang("""
            IF 1 < 2 & 3 < 4:
                DISP "both"
        """)
        self.assertEqual(out.strip(), "both")

    def test_or(self):
        out = run_flang("""
            IF 1 > 100 | 2 > 1:
                DISP "either"
        """)
        self.assertEqual(out.strip(), "either")

    def test_not(self):
        out = run_flang("""
            SET b TO FALSE
            IF !b:
                DISP "negated"
        """)
        self.assertEqual(out.strip(), "negated")

    def test_string_concatenation(self):
        out = run_flang("""
            SET a TO "Hello"
            SET b TO " World"
            DISP a + b
        """)
        self.assertEqual(out.strip(), "Hello World")

    def test_mod_no_spaces(self):
        """Spec uses z%2 without spaces — must be valid."""
        out = run_flang("""
            SET x TO 10
            DISP x%3
        """)
        self.assertEqual(out.strip(), "1")

    def test_operator_precedence_mul_before_add(self):
        self.assertEqual(run_flang("DISP 2 + 3 * 4").strip(), "14")

    def test_operator_precedence_pow_before_mul(self):
        self.assertEqual(run_flang("DISP 2 * 3 ** 2").strip(), "18")

    def test_parentheses_override_precedence(self):
        self.assertEqual(run_flang("DISP (2 + 3) * 4").strip(), "20")


# ---------------------------------------------------------------------------
# CONDITIONALS — IF / ELIF / ELSE
# ---------------------------------------------------------------------------

class TestConditionalsSyntax(unittest.TestCase):
    """Spec:
        IF x > 0:
            DISP "..."
        ELIF x < 0:
            DISP "..."
        ELSE:
            DISP "..."
    """

    def test_if_taken(self):
        out = run_flang("""
            SET x TO 10
            IF x > 0:
                DISP "x is greater than 10 with value {x}"
        """)
        self.assertEqual(out.strip(), "x is greater than 10 with value 10")

    def test_elif_taken(self):
        out = run_flang("""
            SET x TO -5
            IF x > 0:
                DISP "positive"
            ELIF x < 0:
                DISP "x is smaller than 10 with value {x}"
        """)
        self.assertEqual(out.strip(), "x is smaller than 10 with value -5")

    def test_else_taken(self):
        out = run_flang("""
            SET x TO 0
            IF x > 0:
                DISP "positive"
            ELIF x < 0:
                DISP "negative"
            ELSE:
                DISP "x is equal to 10"
        """)
        self.assertEqual(out.strip(), "x is equal to 10")

    def test_if_only_not_taken(self):
        out = run_flang("""
            SET x TO -1
            IF x > 0:
                DISP "yes"
        """)
        self.assertEqual(out.strip(), "")

    def test_multiple_elif(self):
        out = run_flang("""
            SET x TO 2
            IF x = 1:
                DISP "one"
            ELIF x = 2:
                DISP "two"
            ELIF x = 3:
                DISP "three"
            ELSE:
                DISP "other"
        """)
        self.assertEqual(out.strip(), "two")

    def test_nested_conditionals(self):
        out = run_flang("""
            SET x TO 5
            IF x > 0:
                IF x > 3:
                    DISP "big positive"
                ELSE:
                    DISP "small positive"
        """)
        self.assertEqual(out.strip(), "big positive")

    def test_string_interpolation_in_condition_body(self):
        out = run_flang("""
            SET name TO "Bob"
            IF TRUE:
                DISP "Hello {name}"
        """)
        self.assertEqual(out.strip(), "Hello Bob")

    def test_condition_with_and(self):
        out = run_flang("""
            SET x TO 5
            IF x > 0 & x < 10:
                DISP "in range"
        """)
        self.assertEqual(out.strip(), "in range")

    def test_condition_with_or(self):
        out = run_flang("""
            SET x TO 15
            IF x < 0 | x > 10:
                DISP "out of range"
        """)
        self.assertEqual(out.strip(), "out of range")


# ---------------------------------------------------------------------------
# FOR LOOP — all three range forms + array iteration
# ---------------------------------------------------------------------------

class TestForLoopSyntax(unittest.TestCase):
    """Spec:
        FOR RANGE 1 TO 2 AS x:      (start inclusive, end exclusive)
        FOR RANGE 1 TO 2 STEP 6 AS x:
        FOR RANGE 3 AS x:           (0 to 2)
        FOR arr AS i:
    """

    def test_for_range_two_args_spec(self):
        """FOR RANGE 1 TO 2 AS x: should iterate just x=1."""
        out = run_flang("""
            FOR RANGE 1 TO 2 AS x:
                DISP x
        """)
        self.assertEqual(out.strip(), "1")

    def test_for_range_two_args_wider(self):
        out = run_flang("""
            FOR RANGE 1 TO 5 AS x:
                DISP x
        """)
        self.assertEqual(out.strip().splitlines(), ["1", "2", "3", "4"])

    def test_for_range_step_spec(self):
        """FOR RANGE 1 TO 2 STEP 6 AS x: — step > range, so just x=1."""
        out = run_flang("""
            FOR RANGE 1 TO 2 STEP 6 AS x:
                DISP x
        """)
        self.assertEqual(out.strip(), "1")

    def test_for_range_step_typical(self):
        out = run_flang("""
            FOR RANGE 0 TO 10 STEP 3 AS x:
                DISP x
        """)
        self.assertEqual(out.strip().splitlines(), ["0", "3", "6", "9"])

    def test_for_range_single_arg_spec(self):
        """FOR RANGE 3 AS x: iterates 0, 1, 2."""
        out = run_flang("""
            FOR RANGE 3 AS x:
                DISP x
        """)
        self.assertEqual(out.strip().splitlines(), ["0", "1", "2"])

    def test_for_range_single_arg_zero(self):
        out = run_flang("""
            FOR RANGE 0 AS x:
                DISP x
        """)
        self.assertEqual(out.strip(), "")

    def test_for_array_spec(self):
        """FOR arr AS i: should iterate over each element."""
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            FOR arr AS i:
                DISP i
        """)
        self.assertEqual(out.strip().splitlines(), ["1", "2", "3", "4"])

    def test_for_array_strings(self):
        out = run_flang("""
            SET words TO ["cat", "dog", "fish"]
            FOR words AS w:
                DISP w
        """)
        self.assertEqual(out.strip().splitlines(), ["cat", "dog", "fish"])

    def test_for_loop_accumulator(self):
        out = run_flang("""
            SET total TO 0
            FOR RANGE 1 TO 6 AS n:
                SET total TO total + n
            DISP total
        """)
        self.assertEqual(out.strip(), "15")

    def test_for_loop_variable_scoped(self):
        out = run_flang("""
            FOR RANGE 3 AS i:
                DISP i
        """)
        lines = out.strip().splitlines()
        self.assertEqual(lines, ["0", "1", "2"])

    def test_for_nested(self):
        out = run_flang("""
            FOR RANGE 1 TO 3 AS i:
                FOR RANGE 1 TO 3 AS j:
                    DISP i * j
        """)
        vals = [int(x) for x in out.strip().splitlines()]
        self.assertEqual(vals, [1, 2, 2, 4])


# ---------------------------------------------------------------------------
# WHILE LOOP
# ---------------------------------------------------------------------------

class TestWhileLoopSyntax(unittest.TestCase):
    """Spec:
        SET y TO 0
        WHILE y < 10:
            DISP y
            SET y TO y + 1
    """

    def test_while_spec_exact(self):
        out = run_flang("""
            SET y TO 0
            WHILE y < 3:
                DISP y
                SET y TO y + 1
        """)
        self.assertEqual(out.strip().splitlines(), ["0", "1", "2"])

    def test_while_not_entered(self):
        out = run_flang("""
            SET y TO 10
            WHILE y < 5:
                DISP y
                SET y TO y + 1
        """)
        self.assertEqual(out.strip(), "")

    def test_while_single_iteration(self):
        out = run_flang("""
            SET y TO 9
            WHILE y < 10:
                DISP y
                SET y TO y + 1
        """)
        self.assertEqual(out.strip(), "9")

    def test_while_countdown(self):
        out = run_flang("""
            SET n TO 3
            WHILE n > 0:
                DISP n
                SET n TO n - 1
        """)
        self.assertEqual(out.strip().splitlines(), ["3", "2", "1"])

    def test_while_with_accumulator(self):
        out = run_flang("""
            SET i TO 1
            SET product TO 1
            WHILE i <= 5:
                SET product TO product * i
                SET i TO i + 1
            DISP product
        """)
        self.assertEqual(out.strip(), "120")


# ---------------------------------------------------------------------------
# END (break) and NEXT (continue)
# ---------------------------------------------------------------------------

class TestEndAndNext(unittest.TestCase):
    """Spec:
        SET z TO 0
        WHILE z < 10:
            SET z TO z + 1
            IF z%2 = 0:
                DISP z
            ELIF z%3 = 0:
                NEXT
            ELIF z%4 = 0:
                END
    """

    def test_spec_end_next_example(self):
        """Verbatim spec example — z goes 1..10, display evens, skip %3, break on %4."""
        out = run_flang("""
            SET z TO 0
            WHILE z < 10:
                SET z TO z + 1
                IF z%2 = 0:
                    DISP z
                ELIF z%3 = 0:
                    NEXT
                ELIF z%4 = 0:
                    END
        """)
        lines = out.strip().splitlines()
        self.assertIn("2", lines)
        self.assertIn("4", lines)
        self.assertIn("6", lines)
        self.assertIn("8", lines)
        self.assertIn("10", lines)
        for line in lines:
            self.assertEqual(int(line) % 2, 0)

    def test_end_breaks_for_loop(self):
        out = run_flang("""
            FOR RANGE 10 AS i:
                IF i = 5:
                    END
                DISP i
        """)
        lines = out.strip().splitlines()
        self.assertEqual(lines, ["0", "1", "2", "3", "4"])

    def test_end_breaks_while_loop(self):
        out = run_flang("""
            SET i TO 0
            WHILE i < 100:
                SET i TO i + 1
                IF i = 3:
                    END
            DISP i
        """)
        self.assertEqual(out.strip(), "3")

    def test_next_skips_iteration_for_loop(self):
        out = run_flang("""
            FOR RANGE 6 AS i:
                IF i = 3:
                    NEXT
                DISP i
        """)
        lines = out.strip().splitlines()
        self.assertNotIn("3", lines)
        self.assertIn("0", lines)
        self.assertIn("5", lines)

    def test_next_skips_iteration_while_loop(self):
        out = run_flang("""
            SET i TO 0
            WHILE i < 5:
                SET i TO i + 1
                IF i = 3:
                    NEXT
                DISP i
        """)
        lines = out.strip().splitlines()
        self.assertNotIn("3", lines)
        self.assertIn("1", lines)
        self.assertIn("5", lines)

    def test_next_with_mod_no_spaces(self):
        """NEXT triggered by z%2 without spaces (spec style)."""
        out = run_flang("""
            FOR RANGE 1 TO 7 AS z:
                IF z%2 = 0:
                    NEXT
                DISP z
        """)
        lines = out.strip().splitlines()
        for line in lines:
            self.assertNotEqual(int(line) % 2, 0)

    def test_end_inside_nested_if(self):
        out = run_flang("""
            SET found TO 0
            FOR RANGE 1 TO 10 AS i:
                IF i = 5:
                    SET found TO i
                    END
            DISP found
        """)
        self.assertEqual(out.strip(), "5")


# ---------------------------------------------------------------------------
# ARRAYS
# ---------------------------------------------------------------------------

class TestArraysSyntax(unittest.TestCase):
    """Spec:
        SET arr TO [1, 2, 3, 4]
        DISP arr
        FOR arr AS i:
            DISP i
        SET arr[3] TO 5
        DISP arr
    """

    def test_array_literal_and_disp(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            DISP arr
        """)
        self.assertEqual(out.strip(), "[1, 2, 3, 4]")

    def test_array_for_iteration_spec(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            FOR arr AS i:
                DISP i
        """)
        self.assertEqual(out.strip().splitlines(), ["1", "2", "3", "4"])

    def test_array_set_index_spec(self):
        """SET arr[3] TO 5 changes fourth element."""
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            SET arr[3] TO 5
            DISP arr
        """)
        self.assertEqual(out.strip(), "[1, 2, 3, 5]")

    def test_array_index_read(self):
        out = run_flang("""
            SET arr TO [10, 20, 30]
            DISP arr[0]
            DISP arr[1]
            DISP arr[2]
        """)
        self.assertEqual(out.strip().splitlines(), ["10", "20", "30"])

    def test_array_index_zero(self):
        out = run_flang("""
            SET arr TO [99, 1, 2]
            DISP arr[0]
        """)
        self.assertEqual(out.strip(), "99")

    def test_array_string_elements(self):
        out = run_flang("""
            SET names TO ["Alice", "Bob", "Carol"]
            FOR names AS n:
                DISP n
        """)
        self.assertEqual(out.strip().splitlines(), ["Alice", "Bob", "Carol"])

    def test_array_nested(self):
        out = run_flang("""
            SET m TO [[1, 2], [3, 4]]
            DISP m[0][1]
            DISP m[1][0]
        """)
        self.assertEqual(out.strip().splitlines(), ["2", "3"])

    def test_array_empty(self):
        out = run_flang("""
            SET arr TO []
            DISP arr
        """)
        self.assertEqual(out.strip(), "[]")

    def test_array_mixed_types(self):
        out = run_flang("""
            SET arr TO [1, "two", TRUE]
            DISP arr[0]
            DISP arr[1]
            DISP arr[2]
        """)
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "1")
        self.assertEqual(lines[1], "two")
        self.assertEqual(lines[2], "True")

    def test_array_index_with_variable(self):
        out = run_flang("""
            SET arr TO [10, 20, 30]
            SET i TO 2
            DISP arr[i]
        """)
        self.assertEqual(out.strip(), "30")

    def test_array_set_index_with_expression(self):
        out = run_flang("""
            SET arr TO [1, 2, 3]
            SET arr[1] TO arr[0] + arr[2]
            DISP arr
        """)
        self.assertEqual(out.strip(), "[1, 4, 3]")


# ---------------------------------------------------------------------------
# FUNCTIONS — DEF and RETURN
# ---------------------------------------------------------------------------

class TestFunctionsSyntax(unittest.TestCase):
    """Spec:
        DEF square(n):
            RETURN n**2

        DISP square(10)
    """

    def test_def_and_call_spec(self):
        out = run_flang("""
            DEF square(n):
                RETURN n**2
            DISP square(10)
        """)
        self.assertEqual(out.strip(), "100")

    def test_function_prefix_applied(self):
        py = transpile_ok("""
            DEF square(n):
                RETURN n**2
        """)
        self.assertIn("def fun_square(fun_n):", py)
        self.assertIn("return", py)

    def test_function_call_prefixed_in_output(self):
        py = transpile_ok("""
            DEF square(n):
                RETURN n**2
            DISP square(10)
        """)
        self.assertIn("fun_square(10)", py)

    def test_function_multi_param(self):
        out = run_flang("""
            DEF add(a, b):
                RETURN a + b
            DISP add(7, 8)
        """)
        self.assertEqual(out.strip(), "15")

    def test_function_used_in_expression(self):
        out = run_flang("""
            DEF double(n):
                RETURN n * 2
            SET result TO double(5) + 1
            DISP result
        """)
        self.assertEqual(out.strip(), "11")

    def test_function_recursive(self):
        out = run_flang("""
            DEF fact(n):
                IF n <= 1:
                    RETURN 1
                RETURN n * fact(n - 1)
            DISP fact(6)
        """)
        self.assertEqual(out.strip(), "720")

    def test_function_calling_another_function(self):
        out = run_flang("""
            DEF square(n):
                RETURN n ** 2
            DEF sumSquares(a, b):
                RETURN square(a) + square(b)
            DISP sumSquares(3, 4)
        """)
        self.assertEqual(out.strip(), "25")

    def test_function_with_conditional(self):
        out = run_flang("""
            DEF abs_val(n):
                IF n < 0:
                    RETURN n * -1
                RETURN n
            DISP abs_val(-7)
            DISP abs_val(5)
        """)
        self.assertEqual(out.strip().splitlines(), ["7", "5"])

    def test_function_with_loop(self):
        out = run_flang("""
            DEF sum_to(n):
                SET total TO 0
                FOR RANGE 1 TO n + 1 AS i:
                    SET total TO total + i
                RETURN total
            DISP sum_to(5)
        """)
        self.assertEqual(out.strip(), "15")

    def test_function_no_conflict_with_builtin(self):
        """User-defined 'square' must not conflict with builtins."""
        out = run_flang("""
            DEF square(n):
                RETURN n ** 2
            DISP square(3)
            DISP square(4)
        """)
        self.assertEqual(out.strip().splitlines(), ["9", "16"])


# ---------------------------------------------------------------------------
# ASK — user input
# ---------------------------------------------------------------------------

class TestAskSyntax(unittest.TestCase):
    """Spec: SET input TO ASK INT "Number? " """

    def test_ask_int(self):
        # input() writes the prompt to stdout, so output is "Number? 42"
        out = run_flang("""
            SET n TO ASK INT "Number? "
            DISP n
        """, stdin="42\n")
        self.assertIn("42", out)

    def test_ask_float(self):
        out = run_flang("""
            SET f TO ASK FLOAT "Float? "
            DISP f
        """, stdin="3.14\n")
        self.assertIn("3.14", out)

    def test_ask_str(self):
        out = run_flang("""
            SET s TO ASK STR "Name? "
            DISP s
        """, stdin="Alice\n")
        self.assertIn("Alice", out)

    def test_ask_int_used_in_expression(self):
        """Spec: DISP square(input) after ASK INT."""
        out = run_flang("""
            DEF square(n):
                RETURN n ** 2
            SET inp TO ASK INT "Number? "
            DISP square(inp)
        """, stdin="5\n")
        self.assertIn("25", out)

    def test_ask_int_transpile(self):
        py = transpile_ok('SET x TO ASK INT "Enter: "')
        self.assertIn("int(input(", py)

    def test_ask_float_transpile(self):
        py = transpile_ok('SET x TO ASK FLOAT "Enter: "')
        self.assertIn("float(input(", py)

    def test_ask_str_transpile(self):
        py = transpile_ok('SET x TO ASK STR "Enter: "')
        self.assertIn("input(", py)


# ---------------------------------------------------------------------------
# STRING INTERPOLATION
# ---------------------------------------------------------------------------

class TestStringInterpolation(unittest.TestCase):
    """Spec uses {x} inside strings for variable substitution."""

    def test_basic_interpolation(self):
        out = run_flang("""
            SET x TO 42
            DISP "value is {x}"
        """)
        self.assertEqual(out.strip(), "value is 42")

    def test_interpolation_in_if_body(self):
        out = run_flang("""
            SET x TO 5
            IF x > 0:
                DISP "x is greater than 10 with value {x}"
        """)
        self.assertEqual(out.strip(), "x is greater than 10 with value 5")

    def test_interpolation_in_elif_body(self):
        out = run_flang("""
            SET x TO -3
            IF x > 0:
                DISP "positive"
            ELIF x < 0:
                DISP "x is smaller than 10 with value {x}"
        """)
        self.assertEqual(out.strip(), "x is smaller than 10 with value -3")

    def test_multiple_interpolations(self):
        out = run_flang("""
            SET a TO 3
            SET b TO 4
            DISP "{a} plus {b} is {a}"
        """)
        self.assertEqual(out.strip(), "3 plus 4 is 3")

    def test_interpolation_with_string_variable(self):
        out = run_flang("""
            SET name TO "World"
            DISP "Hello {name}!"
        """)
        self.assertEqual(out.strip(), "Hello World!")

    def test_no_interpolation_without_braces(self):
        out = run_flang("""
            SET x TO 10
            DISP "no variable here"
        """)
        self.assertEqual(out.strip(), "no variable here")


# ---------------------------------------------------------------------------
# TYPES — int / float / str / bool / arr
# ---------------------------------------------------------------------------

class TestTypes(unittest.TestCase):
    """Spec allowed types: int, float, str, bool, arr."""

    def test_int_arithmetic(self):
        out = run_flang("DISP 3 + 4")
        self.assertEqual(out.strip(), "7")

    def test_float_arithmetic(self):
        out = run_flang("DISP 1.5 + 2.5")
        self.assertEqual(out.strip(), "4.0")

    def test_int_and_float_mixed(self):
        out = run_flang("DISP 1 + 0.5")
        self.assertEqual(out.strip(), "1.5")

    def test_string_type(self):
        out = run_flang('SET s TO "hello"\nDISP s')
        self.assertEqual(out.strip(), "hello")

    def test_bool_true(self):
        out = run_flang("SET b TO TRUE\nDISP b")
        self.assertEqual(out.strip(), "True")

    def test_bool_false(self):
        out = run_flang("SET b TO FALSE\nDISP b")
        self.assertEqual(out.strip(), "False")

    def test_arr_type(self):
        out = run_flang("SET arr TO [1, 2, 3]\nDISP arr")
        self.assertEqual(out.strip(), "[1, 2, 3]")

    def test_cast_int(self):
        out = run_flang("DISP INT 3.9")
        self.assertEqual(out.strip(), "3")

    def test_cast_float(self):
        out = run_flang("DISP FLOAT 5")
        self.assertEqual(out.strip(), "5.0")

    def test_cast_str(self):
        out = run_flang("DISP STR 42")
        self.assertEqual(out.strip(), "42")


# ---------------------------------------------------------------------------
# BUILT-INS — fun_builtins.py Builtins dict
# ---------------------------------------------------------------------------

class TestBuiltinsRegistry(unittest.TestCase):
    """The Builtins dict in fun_builtins.py must map FLang names to fun_* Python names."""

    def test_builtins_dict_exists(self):
        from flang.fun_builtins import Builtins
        self.assertIsInstance(Builtins, dict)

    def test_builtins_keys_are_strings(self):
        from flang.fun_builtins import Builtins
        for k in Builtins:
            self.assertIsInstance(k, str)

    def test_builtins_values_start_with_fun_(self):
        from flang.fun_builtins import Builtins
        for k, v in Builtins.items():
            self.assertTrue(v.startswith("fun_"), f"{k} maps to {v}, expected fun_ prefix")

    def test_strlower_in_builtins(self):
        from flang.fun_builtins import Builtins
        self.assertIn("strlower", Builtins)
        self.assertEqual(Builtins["strlower"], "fun_strlower")

    def test_builtins_replaced_in_transpiled_code(self):
        py = transpile_ok('DISP strlower("HELLO")')
        self.assertIn("fun_strlower", py)
        self.assertNotIn('"strlower"', py)

    def test_strlower_executes(self):
        out = run_flang('DISP strlower("HELLO WORLD")')
        self.assertEqual(out.strip(), "hello world")

    def test_strupper_executes(self):
        out = run_flang('DISP strupper("hello")')
        self.assertEqual(out.strip(), "HELLO")

    def test_strlen_executes(self):
        out = run_flang('DISP strlen("hello")')
        self.assertEqual(out.strip(), "5")

    def test_abs_executes(self):
        out = run_flang("DISP abs(-99)")
        self.assertEqual(out.strip(), "99")

    def test_len_executes(self):
        out = run_flang("SET arr TO [1, 2, 3]\nDISP len(arr)")
        self.assertEqual(out.strip(), "3")

    def test_sum_executes(self):
        out = run_flang("SET arr TO [10, 20, 30]\nDISP sum(arr)")
        self.assertEqual(out.strip(), "60")

    def test_sort_executes(self):
        out = run_flang("SET arr TO [3, 1, 2]\nDISP sort(arr)")
        self.assertEqual(out.strip(), "[1, 2, 3]")

    def test_reverse_executes(self):
        out = run_flang("SET arr TO [1, 2, 3]\nDISP reverse(arr)")
        self.assertEqual(out.strip(), "[3, 2, 1]")

    def test_max_executes(self):
        out = run_flang("DISP max(5, 10, 3)")
        self.assertEqual(out.strip(), "10")

    def test_min_executes(self):
        out = run_flang("DISP min(5, 10, 3)")
        self.assertEqual(out.strip(), "3")

    def test_round_executes(self):
        out = run_flang("DISP round(3.14159, 2)")
        self.assertEqual(out.strip(), "3.14")

    def test_tostr_executes(self):
        out = run_flang("DISP tostr(100)")
        self.assertEqual(out.strip(), "100")

    def test_toint_executes(self):
        out = run_flang("DISP toint(7.9)")
        self.assertEqual(out.strip(), "7")

    def test_tofloat_executes(self):
        out = run_flang("DISP tofloat(3)")
        self.assertEqual(out.strip(), "3.0")

    def test_strcontains_executes(self):
        out = run_flang('DISP strcontains("hello world", "world")')
        self.assertEqual(out.strip(), "True")

    def test_strsplit_executes(self):
        out = run_flang('DISP strsplit("a,b,c", ",")')
        self.assertEqual(out.strip(), "['a', 'b', 'c']")

    def test_strreplace_executes(self):
        out = run_flang('DISP strreplace("hello world", "world", "FLang")')
        self.assertEqual(out.strip(), "hello FLang")


# ---------------------------------------------------------------------------
# IDENTIFIER PREFIXING — fun_ rules
# ---------------------------------------------------------------------------

class TestIdentifierPrefixing(unittest.TestCase):
    """Every user-defined identifier gets fun_ prefix in Python output."""

    def test_variable_gets_prefix(self):
        py = transpile_ok("SET myVar TO 5")
        self.assertIn("fun_myVar", py)

    def test_function_name_gets_prefix(self):
        py = transpile_ok("DEF myFunc(x):\n    RETURN x")
        self.assertIn("def fun_myFunc", py)

    def test_parameter_gets_prefix(self):
        py = transpile_ok("DEF myFunc(x):\n    RETURN x")
        self.assertIn("fun_x", py)

    def test_call_site_uses_prefix(self):
        py = transpile_ok("DEF sq(n):\n    RETURN n**2\nDISP sq(5)")
        self.assertIn("fun_sq(5)", py)

    def test_loop_variable_gets_prefix(self):
        py = transpile_ok("FOR RANGE 3 AS i:\n    DISP i")
        self.assertIn("fun_i", py)

    def test_loop_array_variable_gets_prefix(self):
        py = transpile_ok("SET arr TO [1]\nFOR arr AS item:\n    DISP item")
        self.assertIn("fun_item", py)

    def test_builtin_not_double_prefixed(self):
        py = transpile_ok('DISP strlower("X")')
        self.assertIn("fun_strlower", py)
        self.assertNotIn("fun_fun_strlower", py)

    def test_keywords_not_prefixed(self):
        py = transpile_ok("SET x TO 1")
        self.assertNotIn("fun_SET", py)
        self.assertNotIn("fun_TO", py)
        self.assertNotIn("fun_DISP", py)


# ---------------------------------------------------------------------------
# CASE SENSITIVITY
# ---------------------------------------------------------------------------

class TestCaseSensitivity(unittest.TestCase):
    """Spec: SET and set are different things. SQUARE and square are different."""

    def test_SET_is_keyword(self):
        py = transpile_ok("SET x TO 1")
        self.assertIn("fun_x = 1", py)

    def test_set_lowercase_is_identifier(self):
        py = transpile_ok("set(1)")
        self.assertIn("fun_set", py)

    def test_DISP_is_keyword(self):
        py = transpile_ok("DISP 1")
        self.assertIn("print(1)", py)

    def test_disp_lowercase_is_identifier(self):
        py = transpile_ok("disp(1)")
        self.assertIn("fun_disp", py)

    def test_SQUARE_user_defined_vs_square(self):
        """SQUARE as user def and square as user def are different identifiers."""
        py1 = transpile_ok("DEF SQUARE(n):\n    RETURN n**2")
        py2 = transpile_ok("DEF square(n):\n    RETURN n**2")
        self.assertIn("fun_SQUARE", py1)
        self.assertIn("fun_square", py2)

    def test_TRUE_is_bool_keyword(self):
        py = transpile_ok("SET b TO TRUE")
        self.assertIn("True", py)

    def test_FALSE_is_bool_keyword(self):
        py = transpile_ok("SET b TO FALSE")
        self.assertIn("False", py)


# ---------------------------------------------------------------------------
# ERROR MESSAGES — kids friendly
# ---------------------------------------------------------------------------

class TestKidFriendlyErrors(unittest.TestCase):
    """Spec: kid-friendly error messages."""

    def _expect_flang_error(self, source: str) -> FLangError:
        with self.assertRaises(FLangError) as ctx:
            transpile(textwrap.dedent(source).strip())
        return ctx.exception

    def test_error_message_starts_with_uh_oh(self):
        err = self._expect_flang_error("SET x 10")
        self.assertTrue(str(err).startswith("Uh oh!"))

    def test_missing_to_in_set(self):
        err = self._expect_flang_error("SET x 10")
        self.assertIn("TO", str(err))

    def test_missing_colon_after_if(self):
        err = self._expect_flang_error("IF x > 0\n    DISP x")
        self.assertIn("colon", str(err).lower())

    def test_missing_colon_after_while(self):
        err = self._expect_flang_error("WHILE x < 10\n    DISP x")
        self.assertIn("colon", str(err).lower())

    def test_missing_colon_after_for(self):
        err = self._expect_flang_error("FOR RANGE 3 AS i\n    DISP i")
        self.assertIn("colon", str(err).lower())

    def test_missing_colon_after_def(self):
        err = self._expect_flang_error("DEF f(x)\n    RETURN x")
        self.assertIn("colon", str(err).lower())

    def test_missing_as_in_for_array(self):
        err = self._expect_flang_error("FOR arr i:\n    DISP i")
        self.assertIn("AS", str(err))

    def test_missing_as_in_for_range(self):
        err = self._expect_flang_error("FOR RANGE 5 i:\n    DISP i")
        self.assertIn("AS", str(err))

    def test_unknown_token(self):
        err = self._expect_flang_error("SET x TO @5")
        self.assertIn("@", str(err))

    def test_bad_ask_type(self):
        err = self._expect_flang_error('SET x TO ASK BOOL "ok"')
        self.assertIn("valid ASK type", str(err))

    def test_error_includes_line_number(self):
        err = self._expect_flang_error("SET x TO 5\nSET y 3")
        self.assertIn("line 2", str(err))

    def test_error_message_is_descriptive(self):
        try:
            transpile("SET x 5")
        except FLangError as e:
            msg = str(e)
            self.assertGreater(len(msg), 10)
            self.assertNotIn("Traceback", msg)


# ---------------------------------------------------------------------------
# FULL PROGRAMS — combining multiple spec features
# ---------------------------------------------------------------------------

class TestFullPrograms(unittest.TestCase):

    def test_fizzbuzz(self):
        out = run_flang("""
            FOR RANGE 1 TO 16 AS i:
                IF i%3 = 0 & i%5 = 0:
                    DISP "FizzBuzz"
                ELIF i%3 = 0:
                    DISP "Fizz"
                ELIF i%5 = 0:
                    DISP "Buzz"
                ELSE:
                    DISP i
        """)
        expected = [
            "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8",
            "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz",
        ]
        self.assertEqual(out.strip().splitlines(), expected)

    def test_array_sum_with_for(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            FOR arr AS i:
                DISP i
            SET arr[3] TO 5
            DISP arr
        """)
        lines = out.strip().splitlines()
        self.assertEqual(lines[:4], ["1", "2", "3", "4"])
        self.assertEqual(lines[4], "[1, 2, 3, 5]")

    def test_factorial_with_while(self):
        out = run_flang("""
            SET n TO 5
            SET result TO 1
            WHILE n > 1:
                SET result TO result * n
                SET n TO n - 1
            DISP result
        """)
        self.assertEqual(out.strip(), "120")

    def test_square_function_spec_example(self):
        """Verbatim from spec: DEF square, DISP square(10)."""
        out = run_flang("""
            DEF square(n):
                RETURN n**2
            DISP square(10)
        """)
        self.assertEqual(out.strip(), "100")

    def test_square_function_with_ask(self):
        """Spec: SET input TO ASK INT / DISP square(input)."""
        out = run_flang("""
            DEF square(n):
                RETURN n**2
            SET inp TO ASK INT "Number? "
            DISP square(inp)
        """, stdin="7\n")
        self.assertIn("49", out)

    def test_search_array_for_value(self):
        out = run_flang("""
            SET arr TO [10, 20, 30, 40, 50]
            SET target TO 30
            SET found TO FALSE
            FOR arr AS val:
                IF val = target:
                    SET found TO TRUE
                    END
            DISP found
        """)
        self.assertEqual(out.strip(), "True")

    def test_count_evens_in_range(self):
        out = run_flang("""
            SET count TO 0
            FOR RANGE 1 TO 11 AS i:
                IF i%2 = 0:
                    SET count TO count + 1
            DISP count
        """)
        self.assertEqual(out.strip(), "5")

    def test_collatz_steps(self):
        out = run_flang("""
            SET n TO 6
            SET steps TO 0
            WHILE n > 1:
                IF n%2 = 0:
                    SET n TO n // 2
                ELSE:
                    SET n TO n * 3 + 1
                SET steps TO steps + 1
            DISP steps
        """)
        self.assertEqual(out.strip(), "8")

    def test_string_processing_with_builtins(self):
        out = run_flang("""
            SET word TO "Hello World"
            DISP strlower(word)
            DISP strupper(word)
            DISP strlen(word)
        """)
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "hello world")
        self.assertEqual(lines[1], "HELLO WORLD")
        self.assertEqual(lines[2], "11")

    def test_variables_conditional_and_loop(self):
        """Full program: find first prime > 10."""
        out = run_flang("""
            SET n TO 11
            SET found TO FALSE
            WHILE !found:
                SET isPrime TO TRUE
                SET i TO 2
                WHILE i * i <= n:
                    IF n%i = 0:
                        SET isPrime TO FALSE
                        END
                    SET i TO i + 1
                IF isPrime:
                    SET found TO TRUE
                ELSE:
                    SET n TO n + 1
            DISP n
        """)
        self.assertEqual(out.strip(), "11")


if __name__ == "__main__":
    unittest.main(verbosity=2)
