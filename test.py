import sys
import os
import io
import textwrap
import unittest
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flang import transpile, FLangError


def run_flang(source: str) -> str:
    """Transpile and execute FLang code, returning captured stdout."""
    source = textwrap.dedent(source).strip()
    py_code = transpile(source)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(py_code)
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, tmp],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Execution failed:\n{result.stderr}")
        return result.stdout
    finally:
        os.unlink(tmp)


class TestVariables(unittest.TestCase):
    def test_set_and_disp_int(self):
        out = run_flang("""
            SET x TO 10
            DISP x
        """)
        self.assertEqual(out.strip(), "10")

    def test_set_and_disp_float(self):
        out = run_flang("""
            SET f TO 3.14
            DISP f
        """)
        self.assertEqual(out.strip(), "3.14")

    def test_set_and_disp_string(self):
        out = run_flang("""
            SET s TO "hello world"
            DISP s
        """)
        self.assertEqual(out.strip(), "hello world")

    def test_set_and_disp_bool_true(self):
        out = run_flang("""
            SET b TO TRUE
            DISP b
        """)
        self.assertEqual(out.strip(), "True")

    def test_set_and_disp_bool_false(self):
        out = run_flang("""
            SET b TO FALSE
            DISP b
        """)
        self.assertEqual(out.strip(), "False")

    def test_arithmetic_add(self):
        out = run_flang("""
            SET a TO 5
            SET b TO 3
            SET c TO a + b
            DISP c
        """)
        self.assertEqual(out.strip(), "8")

    def test_arithmetic_sub(self):
        out = run_flang("""
            SET a TO 10
            SET b TO 4
            DISP a - b
        """)
        self.assertEqual(out.strip(), "6")

    def test_arithmetic_mul(self):
        out = run_flang("""
            DISP 6 * 7
        """)
        self.assertEqual(out.strip(), "42")

    def test_arithmetic_div(self):
        out = run_flang("""
            DISP 10 / 4
        """)
        self.assertEqual(out.strip(), "2.5")

    def test_arithmetic_fdiv(self):
        out = run_flang("""
            DISP 10 // 3
        """)
        self.assertEqual(out.strip(), "3")

    def test_arithmetic_mod(self):
        out = run_flang("""
            DISP 10 % 3
        """)
        self.assertEqual(out.strip(), "1")

    def test_arithmetic_power(self):
        out = run_flang("""
            DISP 2 ** 10
        """)
        self.assertEqual(out.strip(), "1024")

    def test_string_interpolation(self):
        out = run_flang("""
            SET name TO "Alice"
            DISP "Hello {name}!"
        """)
        self.assertEqual(out.strip(), "Hello Alice!")

    def test_reassign_variable(self):
        out = run_flang("""
            SET x TO 5
            SET x TO x + 1
            DISP x
        """)
        self.assertEqual(out.strip(), "6")


class TestConditionals(unittest.TestCase):
    def test_if_true(self):
        out = run_flang("""
            SET x TO 5
            IF x > 0:
                DISP "positive"
        """)
        self.assertEqual(out.strip(), "positive")

    def test_if_false_no_else(self):
        out = run_flang("""
            SET x TO -1
            IF x > 0:
                DISP "positive"
        """)
        self.assertEqual(out.strip(), "")

    def test_if_else(self):
        out = run_flang("""
            SET x TO -1
            IF x > 0:
                DISP "positive"
            ELSE:
                DISP "not positive"
        """)
        self.assertEqual(out.strip(), "not positive")

    def test_if_elif_else(self):
        out = run_flang("""
            SET x TO 0
            IF x > 0:
                DISP "positive"
            ELIF x < 0:
                DISP "negative"
            ELSE:
                DISP "zero"
        """)
        self.assertEqual(out.strip(), "zero")

    def test_elif_branch_taken(self):
        out = run_flang("""
            SET x TO -5
            IF x > 0:
                DISP "positive"
            ELIF x < 0:
                DISP "negative"
            ELSE:
                DISP "zero"
        """)
        self.assertEqual(out.strip(), "negative")

    def test_equality_operator(self):
        out = run_flang("""
            SET x TO 5
            IF x = 5:
                DISP "five"
        """)
        self.assertEqual(out.strip(), "five")

    def test_and_operator(self):
        out = run_flang("""
            SET x TO 5
            IF x > 0 & x < 10:
                DISP "in range"
        """)
        self.assertEqual(out.strip(), "in range")

    def test_or_operator(self):
        out = run_flang("""
            SET x TO 15
            IF x < 0 | x > 10:
                DISP "out of range"
        """)
        self.assertEqual(out.strip(), "out of range")

    def test_not_operator(self):
        out = run_flang("""
            SET x TO FALSE
            IF !x:
                DISP "not false"
        """)
        self.assertEqual(out.strip(), "not false")

    def test_nested_if(self):
        out = run_flang("""
            SET x TO 5
            IF x > 0:
                IF x > 3:
                    DISP "big positive"
        """)
        self.assertEqual(out.strip(), "big positive")


class TestForLoop(unittest.TestCase):
    def test_for_range_single_arg(self):
        out = run_flang("""
            FOR RANGE 3 AS i:
                DISP i
        """)
        self.assertEqual(out.strip(), "0\n1\n2")

    def test_for_range_two_args(self):
        out = run_flang("""
            FOR RANGE 1 TO 4 AS i:
                DISP i
        """)
        self.assertEqual(out.strip(), "1\n2\n3")

    def test_for_range_step(self):
        out = run_flang("""
            FOR RANGE 0 TO 10 STEP 3 AS i:
                DISP i
        """)
        self.assertEqual(out.strip(), "0\n3\n6\n9")

    def test_for_array(self):
        out = run_flang("""
            SET arr TO [10, 20, 30]
            FOR arr AS item:
                DISP item
        """)
        self.assertEqual(out.strip(), "10\n20\n30")

    def test_for_break(self):
        out = run_flang("""
            FOR RANGE 5 AS i:
                IF i = 3:
                    END
                DISP i
        """)
        self.assertEqual(out.strip(), "0\n1\n2")

    def test_for_continue(self):
        out = run_flang("""
            FOR RANGE 5 AS i:
                IF i = 2:
                    NEXT
                DISP i
        """)
        self.assertEqual(out.strip(), "0\n1\n3\n4")


class TestWhileLoop(unittest.TestCase):
    def test_while_basic(self):
        out = run_flang("""
            SET y TO 0
            WHILE y < 3:
                DISP y
                SET y TO y + 1
        """)
        self.assertEqual(out.strip(), "0\n1\n2")

    def test_while_break(self):
        out = run_flang("""
            SET y TO 0
            WHILE y < 10:
                SET y TO y + 1
                IF y = 4:
                    END
            DISP y
        """)
        self.assertEqual(out.strip(), "4")

    def test_while_continue(self):
        out = run_flang("""
            SET y TO 0
            WHILE y < 5:
                SET y TO y + 1
                IF y = 3:
                    NEXT
                DISP y
        """)
        self.assertEqual(out.strip(), "1\n2\n4\n5")


class TestArrays(unittest.TestCase):
    def test_array_disp(self):
        out = run_flang("""
            SET arr TO [1, 2, 3]
            DISP arr
        """)
        self.assertEqual(out.strip(), "[1, 2, 3]")

    def test_array_index_access(self):
        out = run_flang("""
            SET arr TO [10, 20, 30]
            DISP arr[1]
        """)
        self.assertEqual(out.strip(), "20")

    def test_array_index_set(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            SET arr[2] TO 99
            DISP arr
        """)
        self.assertEqual(out.strip(), "[1, 2, 99, 4]")

    def test_array_iteration(self):
        out = run_flang("""
            SET arr TO [5, 10, 15]
            FOR arr AS v:
                DISP v
        """)
        self.assertEqual(out.strip(), "5\n10\n15")

    def test_array_of_strings(self):
        out = run_flang("""
            SET words TO ["hello", "world"]
            FOR words AS w:
                DISP w
        """)
        self.assertEqual(out.strip(), "hello\nworld")

    def test_nested_array(self):
        out = run_flang("""
            SET m TO [[1, 2], [3, 4]]
            DISP m[0][1]
        """)
        self.assertEqual(out.strip(), "2")


class TestFunctions(unittest.TestCase):
    def test_def_and_call(self):
        out = run_flang("""
            DEF square(n):
                RETURN n ** 2
            DISP square(10)
        """)
        self.assertEqual(out.strip(), "100")

    def test_multi_param_function(self):
        out = run_flang("""
            DEF add(a, b):
                RETURN a + b
            DISP add(3, 4)
        """)
        self.assertEqual(out.strip(), "7")

    def test_function_used_in_expr(self):
        out = run_flang("""
            DEF double(n):
                RETURN n * 2
            SET x TO double(5) + 1
            DISP x
        """)
        self.assertEqual(out.strip(), "11")

    def test_function_name_prefix(self):
        py = transpile("DEF myFunc(x):\n    RETURN x")
        self.assertIn("def fun_myFunc(fun_x):", py)
        self.assertIn("return fun_x", py)

    def test_recursive_function(self):
        out = run_flang("""
            DEF fact(n):
                IF n <= 1:
                    RETURN 1
                RETURN n * fact(n - 1)
            DISP fact(5)
        """)
        self.assertEqual(out.strip(), "120")


class TestBuiltins(unittest.TestCase):
    def test_strlower(self):
        out = run_flang("""
            DISP strlower("HELLO")
        """)
        self.assertEqual(out.strip(), "hello")

    def test_strupper(self):
        out = run_flang("""
            DISP strupper("hello")
        """)
        self.assertEqual(out.strip(), "HELLO")

    def test_strlen(self):
        out = run_flang("""
            DISP strlen("abc")
        """)
        self.assertEqual(out.strip(), "3")

    def test_abs(self):
        out = run_flang("""
            DISP abs(-7)
        """)
        self.assertEqual(out.strip(), "7")

    def test_round(self):
        out = run_flang("""
            DISP round(3.567, 2)
        """)
        self.assertEqual(out.strip(), "3.57")

    def test_len(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4, 5]
            DISP len(arr)
        """)
        self.assertEqual(out.strip(), "5")

    def test_max(self):
        out = run_flang("""
            DISP max(3, 7, 2)
        """)
        self.assertEqual(out.strip(), "7")

    def test_min(self):
        out = run_flang("""
            DISP min(3, 7, 2)
        """)
        self.assertEqual(out.strip(), "2")

    def test_sum(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            DISP sum(arr)
        """)
        self.assertEqual(out.strip(), "10")

    def test_sort(self):
        out = run_flang("""
            SET arr TO [3, 1, 2]
            DISP sort(arr)
        """)
        self.assertEqual(out.strip(), "[1, 2, 3]")

    def test_reverse(self):
        out = run_flang("""
            SET arr TO [1, 2, 3]
            DISP reverse(arr)
        """)
        self.assertEqual(out.strip(), "[3, 2, 1]")

    def test_tostr(self):
        out = run_flang("""
            DISP tostr(42)
        """)
        self.assertEqual(out.strip(), "42")

    def test_toint(self):
        out = run_flang("""
            DISP toint(3.9)
        """)
        self.assertEqual(out.strip(), "3")

    def test_strcontains(self):
        out = run_flang("""
            DISP strcontains("hello world", "world")
        """)
        self.assertEqual(out.strip(), "True")

    def test_strsplit(self):
        out = run_flang("""
            DISP strsplit("a,b,c", ",")
        """)
        self.assertEqual(out.strip(), "['a', 'b', 'c']")

    def test_strreplace(self):
        out = run_flang("""
            DISP strreplace("hello world", "world", "FLang")
        """)
        self.assertEqual(out.strip(), "hello FLang")


class TestTranspilation(unittest.TestCase):
    def test_comment_ignored(self):
        out = run_flang("""
            -- this is a comment
            SET x TO 5
            DISP x
        """)
        self.assertEqual(out.strip(), "5")

    def test_variable_prefix_in_transpiled(self):
        py = transpile("SET myVar TO 42")
        self.assertIn("fun_myVar = 42", py)

    def test_function_prefix_in_transpiled(self):
        py = transpile("DEF greet(name):\n    RETURN name")
        self.assertIn("def fun_greet(fun_name):", py)

    def test_builtin_replaced_in_transpiled(self):
        py = transpile("DISP strlower(\"HI\")")
        self.assertIn("fun_strlower", py)
        self.assertNotIn("fun_fun_strlower", py)

    def test_case_sensitivity_upper_keyword(self):
        py = transpile("SET x TO 1")
        self.assertIn("fun_x = 1", py)

    def test_case_sensitivity_lower_not_keyword(self):
        py = transpile("set(1)")
        self.assertIn("fun_set", py)


class TestErrors(unittest.TestCase):
    def test_missing_to_in_set(self):
        with self.assertRaises(FLangError) as ctx:
            transpile("SET x 5")
        self.assertIn("TO", str(ctx.exception))

    def test_missing_colon_if(self):
        with self.assertRaises(FLangError) as ctx:
            transpile("IF x > 0\n    DISP x")
        self.assertIn("colon", str(ctx.exception).lower())

    def test_missing_as_for(self):
        with self.assertRaises(FLangError) as ctx:
            transpile("FOR arr i:\n    DISP i")
        self.assertIn("AS", str(ctx.exception))

    def test_unknown_token(self):
        with self.assertRaises(FLangError) as ctx:
            transpile("SET x TO @5")
        self.assertIn("@", str(ctx.exception))

    def test_kids_friendly_message_prefix(self):
        try:
            transpile("SET x 5")
        except FLangError as e:
            self.assertTrue(str(e).startswith("Uh oh!"))

    def test_ask_bad_type(self):
        with self.assertRaises(FLangError) as ctx:
            transpile('SET x TO ASK BOOL "Enter: "')
        self.assertIn("valid ASK type", str(ctx.exception))


class TestComplexPrograms(unittest.TestCase):
    def test_fizzbuzz(self):
        out = run_flang("""
            FOR RANGE 1 TO 16 AS i:
                IF i % 3 = 0 & i % 5 = 0:
                    DISP "FizzBuzz"
                ELIF i % 3 = 0:
                    DISP "Fizz"
                ELIF i % 5 = 0:
                    DISP "Buzz"
                ELSE:
                    DISP i
        """)
        expected = [
            "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8",
            "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz",
        ]
        self.assertEqual(out.strip().splitlines(), expected)

    def test_sum_array_with_loop(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4, 5]
            SET total TO 0
            FOR arr AS n:
                SET total TO total + n
            DISP total
        """)
        self.assertEqual(out.strip(), "15")

    def test_counting_evens(self):
        out = run_flang("""
            SET count TO 0
            FOR RANGE 1 TO 11 AS i:
                IF i % 2 = 0:
                    SET count TO count + 1
            DISP count
        """)
        self.assertEqual(out.strip(), "5")

    def test_while_collatz(self):
        out = run_flang("""
            SET n TO 6
            SET steps TO 0
            WHILE n > 1:
                IF n % 2 = 0:
                    SET n TO n // 2
                ELSE:
                    SET n TO n * 3 + 1
                SET steps TO steps + 1
            DISP steps
        """)
        self.assertEqual(out.strip(), "8")

    def test_string_concat(self):
        out = run_flang("""
            SET first TO "Hello"
            SET second TO " World"
            DISP first + second
        """)
        self.assertEqual(out.strip(), "Hello World")

    def test_nested_functions(self):
        out = run_flang("""
            DEF square(n):
                RETURN n ** 2
            DEF sumOfSquares(a, b):
                RETURN square(a) + square(b)
            DISP sumOfSquares(3, 4)
        """)
        self.assertEqual(out.strip(), "25")

    def test_end_and_next_mixed(self):
        out = run_flang("""
            SET z TO 0
            WHILE z < 10:
                SET z TO z + 1
                IF z % 2 = 0:
                    DISP z
                ELIF z % 3 = 0:
                    NEXT
                ELIF z = 7:
                    END
        """)
        lines = out.strip().splitlines()
        self.assertIn("2", lines)
        self.assertIn("4", lines)
        self.assertIn("6", lines)

    def test_multiline_array_ops(self):
        out = run_flang("""
            SET arr TO [1, 2, 3, 4]
            SET arr[3] TO 5
            DISP arr
        """)
        self.assertEqual(out.strip(), "[1, 2, 3, 5]")


if __name__ == "__main__":
    unittest.main(verbosity=2)
