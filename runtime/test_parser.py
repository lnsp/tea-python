"""Test the runtime.parser module."""

import unittest

import runtime.lexer
import runtime.env
import runtime.flags
from runtime.parser import *

def token(value, kind):
    return lexer.TokenTuple(value=value, kind=kind)

asgn_token = token("=", lexer.OPERATOR)
asgnadd_token = token("+=", lexer.OPERATOR)
asgnsub_token = token("-=", lexer.OPERATOR)
asgnmul_token = token("*=", lexer.OPERATOR)
asgndiv_token = token("/=", lexer.OPERATOR)
asgnpow_token = token("^=", lexer.OPERATOR)
asgnmod_token = token("%=", lexer.OPERATOR)
plus_token = token("+", lexer.OPERATOR)
minus_token = token("-", lexer.OPERATOR)
neg_token = token("!", lexer.OPERATOR)
and_token = token("&&", lexer.OPERATOR)
or_token = token("||", lexer.OPERATOR)
xor_token = token("^|", lexer.OPERATOR)
equal_token = token("==", lexer.OPERATOR)
unequal_token = token("!=", lexer.OPERATOR)
smaller_token = token("<", lexer.OPERATOR)
larger_token = token(">", lexer.OPERATOR)
smequ_token = token("<=", lexer.OPERATOR)
lgequ_token = token(">=", lexer.OPERATOR)
mod_token = token("%", lexer.OPERATOR)
type_token = token(":", lexer.OPERATOR)
multiply_token = token("*", lexer.OPERATOR)
divide_token = token("/", lexer.OPERATOR)
power_token = token("^", lexer.OPERATOR)
lprt_token = token(")", lexer.LPRT)
sep_token = token(",", lexer.SEPARATOR)
identifier_token = token("abc", lexer.IDENTIFIER)
string_token = token("\"abc\"", lexer.STRING)
rprt_token = token("(", lexer.RPRT)
number_token = token("1", lexer.NUMBER)

operation_tokens = [plus_token, minus_token, sep_token, lprt_token, None]
value_tokens = [identifier_token, string_token, rprt_token, number_token]
all_tokens = operation_tokens + value_tokens

def clean_lex(expr):
    clean = lexer.run(expr)
    output = []
    for e in clean:
        if e.kind is not lexer.WHITESPACE:
            output.append(e)
    return output

class TestParser(unittest.TestCase):
    """Test the parser."""

    def test_is_assignment(self):
        cases = [
            (asgn_token, True),
            (asgnadd_token, True),
            (asgnsub_token, True),
            (asgnmul_token, True),
            (asgndiv_token, True),
            (asgnmod_token, True),
            (asgnpow_token, True),
            (None, False),
            (number_token, False),
        ]

        for tc in cases:
            self.assertEqual(is_assignment(tc[0]), tc[1],
                             "%s mistakingly reported as assignment" % str(tc[0]))

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

    def test_arg_count(self):

        cases = [
            (plus_token, value_tokens, 2),
            (plus_token, operation_tokens, 1),
            (minus_token, value_tokens, 2),
            (minus_token, operation_tokens, 1),
            (neg_token, value_tokens, 1),
            (neg_token, operation_tokens, 1),
            (and_token, all_tokens, 2),
            (or_token, all_tokens, 2),
            (xor_token, all_tokens, 2),
            (equal_token, all_tokens, 2),
            (unequal_token, all_tokens, 2),
            (smaller_token, all_tokens, 2),
            (larger_token, all_tokens, 2),
            (smequ_token, all_tokens, 2),
            (lgequ_token, all_tokens, 2),
            (mod_token, all_tokens, 2),
            (type_token, all_tokens, 2),
            (multiply_token, all_tokens, 2),
            (divide_token, all_tokens, 2),
            (power_token, all_tokens, 2),
            (asgn_token, all_tokens, 2),
            (asgnadd_token, all_tokens, 2),
            (asgnsub_token, all_tokens, 2),
            (asgnmul_token, all_tokens, 2),
            (asgndiv_token, all_tokens, 2),
            (asgnpow_token, all_tokens, 2),
            (asgnmod_token, all_tokens, 2),
        ]

        for tc in cases:
            for e in tc[1]:
                self.assertEqual(get_arg_count(tc[0].value, e), tc[2],
                                 "bad operator arg count for %s when tested against %s" % (tc[0].value, e))

    def test_precedence(self):
        cases = [
            (neg_token, all_tokens, 7),
            (plus_token, operation_tokens, 7),
            (minus_token, operation_tokens, 7),
            (power_token, all_tokens, 6),
            (divide_token, all_tokens, 5),
            (multiply_token, all_tokens, 5),
            (plus_token, value_tokens, 4),
            (minus_token, value_tokens, 4),
            (type_token, all_tokens, 4),
            (mod_token, all_tokens, 3),
            (smaller_token, all_tokens, 2),
            (larger_token, all_tokens, 2),
            (smequ_token, all_tokens, 2),
            (lgequ_token, all_tokens, 2),
            (equal_token, all_tokens, 2),
            (unequal_token, all_tokens, 2),
            (and_token, all_tokens, 1),
            (or_token, all_tokens, 1),
            (xor_token, all_tokens, 1),
            (asgn_token, all_tokens, 0),
            (asgnadd_token, all_tokens, 0),
            (asgnsub_token, all_tokens, 0),
            (asgnmul_token, all_tokens, 0),
            (asgndiv_token, all_tokens, 0),
            (asgnpow_token, all_tokens, 0),
            (asgnmod_token, all_tokens, 0),
        ]

        for tc in cases:
            for e in tc[1]:
                self.assertEqual(get_precedence(tc[0].value, e), tc[2],
                                 "bad operator precedence for %s when tested against %s" % (tc[0].value, e))

    def test_associativity(self):
        cases = [
            (neg_token, all_tokens, False),
            (plus_token, operation_tokens, False),
            (minus_token, operation_tokens, False),
            (power_token, all_tokens, False),
            (divide_token, all_tokens, True),
            (multiply_token, all_tokens, True),
            (plus_token, value_tokens, True),
            (minus_token, value_tokens, True),
            (type_token, all_tokens, True),
            (mod_token, all_tokens, True),
            (smaller_token, all_tokens, True),
            (larger_token, all_tokens, True),
            (smequ_token, all_tokens, True),
            (lgequ_token, all_tokens, True),
            (equal_token, all_tokens, True),
            (unequal_token, all_tokens, True),
            (and_token, all_tokens, True),
            (or_token, all_tokens, True),
            (xor_token, all_tokens, True),
            (asgn_token, all_tokens, True),
            (asgnadd_token, all_tokens, True),
            (asgnsub_token, all_tokens, True),
            (asgnmul_token, all_tokens, True),
            (asgndiv_token, all_tokens, True),
            (asgnpow_token, all_tokens, True),
            (asgnmod_token, all_tokens, True),
        ]

        for tc in cases:
            for e in tc[1]:
                self.assertEqual(is_left_associative(tc[0].value, e), tc[2],
                                 "bad operator associativity for %s when tested against %s" % (tc[0].value, e))


    def test_expression(self):
        pass

    def test_declaration(self):
        # case 1: var a: int, length 4
        case1 = ast.Sequence()
        case1.add(ast.Declaration("a", "int"))

        # case 2: var a = null, length 4
        case2 = ast.Sequence()
        case2.add(ast.Declaration("a", "null"))
        case2_assgn = ast.Assignment("a", True)
        case2_assgn.add(ast.Literal(env.Value(env.NULL)))
        case2.add(case2_assgn)

        # case 3: var a: int = null, length 6
        case3 = ast.Sequence()
        case3.add(ast.Declaration("a", "int"))
        case3_assgn = ast.Assignment("a", False)
        case3_assgn.add(ast.Literal(env.Value(env.NULL)))
        case3.add(case3_assgn)

        # case 4: var a, b = null, length 6
        case4 = ast.Sequence()
        case4.add(ast.Declaration("a", "null"))
        case4.add(ast.Declaration("b", "null"))
        case4_assgn_a = ast.Assignment("a", True)
        case4_assgn_a.add(ast.Literal(env.Value(env.NULL)))
        case4_assgn_b = ast.Assignment("b", True)
        case4_assgn_b.add(case4_assgn_a)
        case4.add(case4_assgn_b)

        # case 5: var a, b, c: int = null, length 10
        case5 = ast.Sequence()
        case5.add(ast.Declaration("a", "int"))
        case5.add(ast.Declaration("b", "int"))
        case5.add(ast.Declaration("c", "int"))
        case5_assgn_a = ast.Assignment("a", False)
        case5_assgn_a.add(ast.Literal(env.Value(env.NULL)))
        case5_assgn_b = ast.Assignment("b", False)
        case5_assgn_b.add(case5_assgn_a)
        case5_assgn_c = ast.Assignment("c", False)
        case5_assgn_c.add(case5_assgn_b)
        case5.add(case5_assgn_c)

        cases = [
            ("var a: int", case1, 3),
            ("var a = null", case2, 3),
            ("var a: int = null", case3, 5),
            ("var a, b = null", case4, 5),
            ("var a, b, c: int = null", case5, 9)
        ]

        for tc in cases:
            output, offset = generate_declaration(clean_lex(tc[0]))
            self.assertEqual(output, tc[1],
                             "%s is not equal to %s" % (str(output), str(tc[1])))
            self.assertEqual(offset, tc[2],
                             "%s offset %d is not equal to %d" % (str(output), offset, tc[2]))

        # error-case 6: var a
        # error-case 7: var a: null, b: null
        # error-case 8: var a: null, b
        error_cases = [
            ("var a", ParseException),
            ("var a: null, b: null", ParseException),
            ("var a: null, b", ParseException),
        ]

        for tc in error_cases:
            tokens = clean_lex(tc[0])
            self.assertRaises(tc[1], generate_declaration, tokens)

    def test_assignment(self):
        case1_assgn = ast.Assignment("a")
        case1_assgn.add(ast.Identifier("a"))
        case1 = case1_assgn

        case2_assgn = ast.Assignment("a")
        case2_assgnadd = ast.Operation("+")
        case2_assgnadd.add(ast.Identifier("a"))
        case2_assgnadd.add(ast.Literal(env.Value(env.NULL)))
        case2_assgn.add(case2_assgnadd)
        case2 = case2_assgn

        case3_assgn = ast.Assignment("a")
        case3_assgnsub = ast.Operation("-")
        case3_assgnsub.add(ast.Identifier("a"))
        case3_assgnsub.add(ast.Literal(env.Value(env.NULL)))
        case3_assgn.add(case3_assgnsub)
        case3 = case3_assgn

        case4_assgn = ast.Assignment("a")
        case4_assgnmul = ast.Operation("*")
        case4_assgnmul.add(ast.Identifier("a"))
        case4_assgnmul.add(ast.Literal(env.Value(env.NULL)))
        case4_assgn.add(case4_assgnmul)
        case4 = case4_assgn

        case5_assgn = ast.Assignment("a")
        case5_assgndiv = ast.Operation("/")
        case5_assgndiv.add(ast.Identifier("a"))
        case5_assgndiv.add(ast.Literal(env.Value(env.NULL)))
        case5_assgn.add(case5_assgndiv)
        case5 = case5_assgn

        case6_assgn = ast.Assignment("a")
        case6_assgnpow = ast.Operation("^")
        case6_assgnpow.add(ast.Identifier("a"))
        case6_assgnpow.add(ast.Literal(env.Value(env.NULL)))
        case6_assgn.add(case6_assgnpow)
        case6 = case6_assgn

        case7_assgn = ast.Assignment("a")
        case7_assgnmod = ast.Operation("%")
        case7_assgnmod.add(ast.Identifier("a"))
        case7_assgnmod.add(ast.Literal(env.Value(env.NULL)))
        case7_assgn.add(case7_assgnmod)
        case7 = case7_assgn

        cases = [
            ("a = a", case1, 2),
            ("a += null", case2, 2),
            ("a = a + null", case2, 4),
            ("a -= null", case3, 2),
            ("a = a - null", case3, 4),
            ("a *= null", case4, 2),
            ("a = a * null", case4, 4),
            ("a /= null", case5, 2),
            ("a = a / null", case5, 4),
            ("a ^= null", case6, 2),
            ("a = a ^ null", case6, 4),
        ]

        for tc in cases:
            output, offset = generate_assignment(clean_lex(tc[0]))
            self.assertEqual(output, tc[1], "%s is not equal to %s" % (output, tc[1]))
            self.assertEqual(offset, tc[2], "%s offset %d is not equal to %d" % (output, offset, tc[2]))

        error_cases = [
            ("a =", ParseException),
            ("a", ParseException),
            ("= 2", ParseException),
            ("a == 2", ParseException),
            ("a = = 2", ParseException),
            ("a ; = 2", ParseException),
        ]

        for tc in error_cases:
            self.assertRaises(tc[1], generate_assignment, clean_lex(tc[0]))


    def test_function(self):
        pass

    def test_if(self):
        # case 1: if (null) {;}, offset 6
        case1 = ast.Branch()
        case1_cond = ast.Conditional()
        case1_cond.add(ast.Literal(env.Value(env.NULL)))
        case1_cond.add(ast.Sequence())
        case1.add(case1_cond)
        # case 2: if (null) {;} else {;}, offset 10
        case2 = ast.Branch()
        case2_cond = ast.Conditional()
        case2_cond.add(ast.Literal(env.Value(env.NULL)))
        case2_cond.add(ast.Sequence())
        case2.add(case2_cond)
        case2.add(ast.Sequence())
        # case 3: if (null) {;} else if (null) {;}, offset 14
        case3 = ast.Branch()
        case3_if = ast.Conditional()
        case3_if.add(ast.Literal(env.Value(env.NULL)))
        case3_if.add(ast.Sequence())
        case3_elif = ast.Branch()
        case3_elif_cond = ast.Conditional()
        case3_elif_cond.add(ast.Literal(env.Value(env.NULL)))
        case3_elif_cond.add(ast.Sequence())
        case3_elif.add(case3_elif_cond)
        case3.add(case3_if)
        case3.add(case3_elif)
        # case 4: if (null) {;} else if (null) {;} else {;}, offset 18
        case4 = ast.Branch()
        case4_if = ast.Conditional()
        case4_if.add(ast.Literal(env.Value(env.NULL)))
        case4_if.add(ast.Sequence())
        case4_elif = ast.Branch()
        case4_elif_cond = ast.Conditional()
        case4_elif_cond.add(ast.Literal(env.Value(env.NULL)))
        case4_elif_cond.add(ast.Sequence())
        case4_elif.add(case4_elif_cond)
        case4_elif.add(ast.Sequence())
        case4.add(case4_if)
        case4.add(case4_elif)

        cases = [
            ("if (null) {;}", case1, 6),
            ("if (null) {;} else {;}", case2, 10),
            ("if (null) {;} else if (null) {;}", case3, 14),
            ("if (null) {;} else if (null) {;} else {;}", case4, 18)
        ]

        for tc in cases:
            output, offset = generate_if(clean_lex(tc[0]))
            self.assertEqual(output, tc[1], "%s is not equal to %s" % (output, tc[1]))
            self.assertEqual(offset, tc[2], "%s offset %d is not equal to %d" % (output, offset, tc[2]))

        error_cases = [
            ("if () {}", ParseException),
            ("if {} else ()", ParseException),
            ("if () else if {}", ParseException),
        ]

        for tc in error_cases:
            tokens = clean_lex(tc[0])
            self.assertRaises(tc[1], generate_if, tokens)

    def test_for(self):
        pass

    def test_while(self):
        # case 1: while (null) {}
        case1 = ast.Loop()
        case1.add(ast.Literal(env.Value(env.NULL)))
        case1.add(ast.Sequence())

        cases = [
            ("while (null) {}", case1, 5),
            ("while (null) {;}", case1, 6),
        ]

        for tc in cases:
            output, offset = generate_while(clean_lex(tc[0]))
            self.assertEqual(output, tc[1], "%s is not equal to %s" % (output, tc[1]))
            self.assertEqual(offset, tc[2], "%s offset %d is not equal to %d" % (output, offset, tc[2]))

        error_cases = [
            ("while () {}", ParseException),
            ("while ()", ParseException),
            ("() {}", ParseException),
            ("while () {}", ParseException),
            ("while (false) {", ParseException),
            ("while ) {}}}", ParseException),
        ]

        for tc in error_cases:
            self.assertRaises(tc[1], generate_while, clean_lex(tc[0]))

    def test_sequence(self):
        pass

    def test_optimize(self):
        pass

    def test_generate(self):
        pass

