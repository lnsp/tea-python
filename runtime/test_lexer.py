"""Test the runtime.lexer module."""
import unittest

from runtime.lexer import TokenTuple, NUMBER, OPERATOR, WHITESPACE, IDENTIFIER, STRING, run

class TestLexer(unittest.TestCase):
    """Test the lexer."""
    def test_simple(self):
        """A small collection of simple test cases."""
        test_cases = [
            ("3", [TokenTuple(value="3", kind=NUMBER)]),
            ("+", [TokenTuple(value="+", kind=OPERATOR)]),
            (" ", [TokenTuple(value=" ", kind=WHITESPACE)]),
            ("a", [TokenTuple(value="a", kind=IDENTIFIER)]),
            ("\"\"", [TokenTuple(value="\"\"", kind=STRING)]),
            ("\"a\" + \"4\"", [
                TokenTuple(value="\"a\"", kind=STRING),
                TokenTuple(value=" ", kind=WHITESPACE),
                TokenTuple(value="+", kind=OPERATOR),
                TokenTuple(value=" ", kind=WHITESPACE),
                TokenTuple(value="\"4\"", kind=STRING),
            ]),
        ]
        for (case, expected) in test_cases:
            self.assertEqual(run(case), expected)
            