"""Test the runtime.lexer module."""
import unittest

from runtime.lexer import *

def t(value, kind):
    return TokenTuple(value=value, kind=kind)

class TestLexer(unittest.TestCase):
    """Test the lexer."""

    def test_asgn(self):
        self.assertEqual(run("="), [t("=", OPERATOR)])

    def test_asgn_add(self):
        self.assertEqual(run("+="),[ t("+=", OPERATOR)])

    def test_asgn_sub(self):
        self.assertEqual(run("-="),[ t("-=", OPERATOR)])

    def test_asgn_mul(self):
        self.assertEqual(run("*="),[ t("*=", OPERATOR)])

    def test_asgn_div(self):
        self.assertEqual(run("/="),[ t("/=", OPERATOR)])

    def test_asgn_mod(self):
        self.assertEqual(run("%="),[ t("%=", OPERATOR)])

    def test_asgn_pow(self):
        self.assertEqual(run("^="),[ t("^=", OPERATOR)])

    def test_and(self):
        self.assertEqual(run("&&"),[ t("&&", OPERATOR)])

    def test_or(self):
        self.assertEqual(run("||"),[ t("||", OPERATOR)])

    def test_xor(self):
        self.assertEqual(run("^|"),[ t("^|", OPERATOR)])

    def test_equal(self):
        self.assertEqual(run("=="),[ t("==", OPERATOR)])

    def test_unequal(self):
        self.assertEqual(run("!="),[ t("!=", OPERATOR)])

    def test_sm(self):
        self.assertEqual(run("<"), [t("<", OPERATOR)])

    def test_lg(self):
        self.assertEqual(run(">"), [t(">", OPERATOR)])

    def test_smeq(self):
        self.assertEqual(run(">="),[ t(">=", OPERATOR)])

    def test_lgeq(self):
        self.assertEqual(run("<="),[ t("<=", OPERATOR)])

    def test_mod(self):
        self.assertEqual(run("%"), [t("%", OPERATOR)])

    def test_type(self):
        self.assertEqual(run(":"), [t(":", OPERATOR)])

    def test_add(self):
        self.assertEqual(run("+"), [t("+", OPERATOR)])

    def test_sub(self):
        self.assertEqual(run("-"), [t("-", OPERATOR)])

    def test_mul(self):
        self.assertEqual(run("*"), [t("*", OPERATOR)])

    def test_div(self):
        self.assertEqual(run("/"), [t("/", OPERATOR)])

    def test_pow(self):
        self.assertEqual(run("^"), [t("^", OPERATOR)])

    def test_sep(self):
        self.assertEqual(run(","), [t(",", SEPARATOR)])

    def test_neg(self):
        self.assertEqual(run("!"), [t("!", OPERATOR)])

    def test_parentheses(self):
        self.assertEqual(run("("), [t("(", LPRT)])
        self.assertEqual(run(")"), [t(")", RPRT)])

    def test_statement(self):
        self.assertEqual(run(";"), [t(";", STATEMENT)])

    def test_block(self):
        self.assertEqual(run("{"), [t("{", LBLOCK)])
        self.assertEqual(run("}"), [t("}", RBLOCK)])

    def test_identifiers(self):
        test_cases = [
            ("#add", t("#add", IDENTIFIER)),
            ("#", t("#", IDENTIFIER)),
            ("#123", t("#123", IDENTIFIER)),
            ("#abc", t("#abc", IDENTIFIER)),
            ("#a12", t("#a12", IDENTIFIER)),
            ("a", t("a", IDENTIFIER)),
            ("_", t("_", IDENTIFIER)),
            ("_abc", t("_abc", IDENTIFIER)),
            ("_123", t("_123", IDENTIFIER)),
        ]
        for tc in test_cases:
            self.assertEqual(run(tc[0]), [tc[1]])

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
            ("3.14", [TokenTuple(value="3.14", kind=NUMBER)]),
        ]
        for (case, expected) in test_cases:
            self.assertEqual(run(case), expected)