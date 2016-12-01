"""Test the runtime.parser module."""

import unittest

import runtime.lexer
from runtime.parser import *

def clean_lex(expr):
    clean = lexer.run(expr)
    output = []
    for e in clean:
        if e.kind is not lexer.WHITESPACE:
            output.append(e)
    return output

class TestParser(unittest.TestCase):
    """Test the parser."""

    def test_matching_block(self):
        cases = [
            (clean_lex("{}"), 1),
            (clean_lex("{"), -1),
            (clean_lex("}"), -1),
            (clean_lex("{{}"), -1),
            (clean_lex("{{}}"), 3),
            (clean_lex("{ 123; }"), 3),
        ]

        for tc in cases:
            self.assertEqual(find_matching_block(tc[0], 1), tc[1])


    def test_matching_prt(self):
        cases = [
            (clean_lex("()"), 1),
            (clean_lex("("), -1),
            (clean_lex(")"), -1),
            (clean_lex("(()"), -1),
            (clean_lex("(123)"), 2),
            (clean_lex("(12 12)"), 3),
        ]

        for tc in cases:
            self.assertEqual(find_matching_prt(tc[0], 1), tc[1])

