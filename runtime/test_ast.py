"""The unit test for runtime.ast"""
import unittest
from runtime import ast, env, lib

NULL_LITERAL = ast.Literal(env.Value(env.NULL))
INT_LITERAL = ast.Literal(env.Value(lib.INTEGER, 0))
TRUE_LITERAL = ast.Literal(env.Value(lib.BOOLEAN, True))
FALSE_LITERAL = ast.Literal(env.Value(lib.BOOLEAN, False))
STRING_LITERAL = ast.Literal(
    env.Value(lib.STRING, "Hallo Welt!", "identifier"))

class SumNode(ast.Node):
    """A sum node."""
    name = "sum"

    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Sums up the value of its children."""
        value = 0
        for child in self.children:
            value += child.eval(context).data
        return env.Value(lib.INTEGER, value)


class AccessNode(ast.Node):
    """A access node."""
    def __init__(self):
        super().__init__()

    @classmethod
    def eval(cls, context):
        """Stores a string in the current namespace."""
        context.store(STRING_LITERAL.value)
        return STRING_LITERAL.eval(context)

class TestAst(unittest.TestCase):
    """The abstract syntax tree test cases."""

    def test_sequence_node(self):
        """Test the sequence node."""
        context = env.empty_context()
        return_node = ast.Return()
        return_node.children = [TRUE_LITERAL]
        # empty sequence
        empty_seq = ast.Sequence()
        self.assertEqual(empty_seq.eval(context), NULL_LITERAL.value)

        # non-empty sequence
        non_seq = ast.Sequence()
        non_seq.children = [NULL_LITERAL, TRUE_LITERAL]
        self.assertEqual(non_seq.eval(context), TRUE_LITERAL.value)
        non_seq.children = [TRUE_LITERAL, NULL_LITERAL]
        self.assertEqual(non_seq.eval(context), NULL_LITERAL.value)

        # sequence with return
        ret_seq = ast.Sequence()
        ret_seq.children = [return_node, NULL_LITERAL]
        self.assertEqual(ret_seq.eval(context), TRUE_LITERAL.value)
        self.assertEqual(ret_seq.__str__(), "<Node (sequence)>")

    def test_conditional_node(self):
        """Test the conditional node."""
        context = env.empty_context()

        # Test bad conditional error
        bad_conditional = ast.Conditional()
        bad_conditional.add(NULL_LITERAL)  # if None:
        bad_conditional.add(NULL_LITERAL)  # then None
        self.assertRaises(Exception, bad_conditional.eval, context)

        # Test correct result
        good_conditional = ast.Conditional()
        good_conditional.add(TRUE_LITERAL)
        good_conditional.add(NULL_LITERAL)
        self.assertEqual(good_conditional.eval(context), NULL_LITERAL.value)
        self.assertEqual(good_conditional.__str__(), "<Node (conditional)>")

    def test_branch_node(self):
        """Test the branch node."""
        context = env.empty_context()
        # always evaluates
        true_cond = ast.Conditional()
        true_cond.children = [TRUE_LITERAL, STRING_LITERAL]
        false_cond = ast.Conditional()
        false_cond.children = [FALSE_LITERAL, NULL_LITERAL]
        # Test if branch
        if_branch = ast.Branch()
        if_branch.children = [true_cond, NULL_LITERAL]
        self.assertEqual(if_branch.eval(context), STRING_LITERAL.value)
        # Test if-else branch
        ifelse_branch = ast.Branch()
        ifelse_branch.children = [false_cond, STRING_LITERAL]
        self.assertEqual(ifelse_branch.eval(context), STRING_LITERAL.value)
        # Test if-elif-else branch
        ifelifelse_branch = ast.Branch()
        ifelifelse_branch.children = [false_cond, true_cond, NULL_LITERAL]
        self.assertEqual(ifelifelse_branch.eval(context), STRING_LITERAL.value)
        self.assertEqual(if_branch.__str__(), "<Node (branch)>")

    def test_loop_node(self):
        """Test the loop node."""
        break_node = ast.Break()
        return_node = ast.Return()
        return_node.children = [TRUE_LITERAL]
        context = env.empty_context()

        # check for exception
        bad_loop = ast.Loop()
        bad_loop.children = [NULL_LITERAL, TRUE_LITERAL]
        self.assertRaises(Exception, bad_loop.eval, context)

        # check for break
        break_loop = ast.Loop()
        break_loop.children = [TRUE_LITERAL, break_node]
        self.assertEqual(break_loop.eval(context), NULL_LITERAL.value)
        self.assertEqual(context.behaviour, ast.DEFAULT_BEHAVIOUR)

        # check for return
        return_loop = ast.Loop()
        return_loop.children = [TRUE_LITERAL, return_node]
        self.assertEqual(return_loop.eval(context), TRUE_LITERAL.value)
        self.assertEqual(context.behaviour, ast.RETURN_BEHAVIOUR)
        self.assertEqual(return_loop.__str__(), "<Node (loop)>")

    def test_return_node(self):
        """Test the return node."""
        # test empty return node
        context = env.empty_context()
        empty_return = ast.Return()
        self.assertEqual(empty_return.eval(context), NULL_LITERAL.value)
        self.assertEqual(context.behaviour, ast.RETURN_BEHAVIOUR)

        # test return with value
        context = env.empty_context()
        value_return = ast.Return()
        value_return.add(TRUE_LITERAL)
        self.assertEqual(value_return.eval(context), TRUE_LITERAL.value)
        self.assertEqual(context.behaviour, ast.RETURN_BEHAVIOUR)
        self.assertEqual(value_return.__str__(), "<Node (return)>")

    def test_break_node(self):
        """Test the break node."""
        context = env.empty_context()
        break_node = ast.Break()
        self.assertEqual(break_node.eval(context), NULL_LITERAL.value)
        self.assertEqual(context.behaviour, ast.BREAK_BEHAVIOUR)
        self.assertEqual(break_node.__str__(), "<Node (break)>")

    def test_continue_node(self):
        """Test the continue node."""
        context = env.empty_context()
        continue_node = ast.Continue()
        self.assertEqual(continue_node.eval(context), NULL_LITERAL.value)
        self.assertEqual(context.behaviour, ast.CONTINUE_BEHAVIOUR)
        self.assertEqual(continue_node.__str__(), "<Node (continue)>")

    def test_call_node(self):
        """Test the function node."""
        # Create sample namespace
        sum_function = SumNode()
        sgn1 = env.Value(lib.INTEGER, None, "a")
        sgn2 = env.Value(lib.INTEGER, None, "b")
        sum_function.children = [
            ast.Identifier("a"),
            ast.Identifier("b"),
        ]
        context = env.empty_context()
        func = env.Function([
            env.Signature([sgn1, sgn2], sum_function),
        ], "my_func")
        context.store(func)

        arg1 = SumNode()
        arg1.children = [
            ast.Literal(env.Value(lib.INTEGER, 1)),
            ast.Literal(env.Value(lib.INTEGER, 2)),
        ]
        arg2 = SumNode()
        arg2.children = [
            ast.Literal(env.Value(lib.INTEGER, 3)),
            ast.Literal(env.Value(lib.INTEGER, 4)),
        ]
        call_node = ast.Call("my_func")
        call_node.children = [arg1, arg2]

        self.assertEqual(call_node.eval(context), env.Value(lib.INTEGER, 10))
        bad_node = ast.Call("missing")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_operation_node(self):
        """Test the operation node."""
        # Works completely like the call node
        # Create sample namespace
        sum_function = SumNode()
        sgn1 = env.Value(lib.INTEGER, None, "a")
        sgn2 = env.Value(lib.INTEGER, None, "b")
        sum_function.children = [
            ast.Identifier("a"),
            ast.Identifier("b"),
        ]
        context = env.empty_context()
        func = env.Function([
            env.Signature([sgn1, sgn2], sum_function),
        ])
        operator = env.Operator(func, "+")
        context.store(operator)

        arg1 = SumNode()
        arg1.children = [
            ast.Literal(env.Value(lib.INTEGER, 1)),
            ast.Literal(env.Value(lib.INTEGER, 2)),
        ]
        arg2 = SumNode()
        arg2.children = [
            ast.Literal(env.Value(lib.INTEGER, 3)),
            ast.Literal(env.Value(lib.INTEGER, 4)),
        ]
        call_node = ast.Operation("+")
        call_node.children = [arg1, arg2]

        self.assertEqual(call_node.eval(context), env.Value(lib.INTEGER, 10))
        bad_node = ast.Operation("?")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_cast_node(self):
        """Test the cast node."""
        context = env.empty_context()
        context.store(lib.INTEGER)
        cast_node = ast.Cast(lib.INTEGER.name)
        cast_node.children = [NULL_LITERAL]
        self.assertEqual(cast_node.eval(context), INT_LITERAL.value)
        bad_node = ast.Cast("missing")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_identifier_node(self):
        """Test the identifier node."""
        context = env.empty_context()
        # Search in local ns
        context.store(STRING_LITERAL.value)
        ident_node = ast.Identifier(STRING_LITERAL.value.name)
        self.assertEqual(ident_node.eval(context), STRING_LITERAL.value)

        # Search in parent ns
        context.substitute()
        self.assertEqual(ident_node.eval(context), STRING_LITERAL.value)

        # Identifier does not exist
        bad_node = ast.Identifier("missing")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_literal_node(self):
        """Test the literal node."""
        context = env.empty_context()
        self.assertEqual(NULL_LITERAL.eval(context), NULL_LITERAL.value)
        self.assertEqual(STRING_LITERAL.eval(context), STRING_LITERAL.value)
        self.assertEqual(TRUE_LITERAL.eval(context), TRUE_LITERAL.value)
        self.assertEqual(FALSE_LITERAL.eval(context), FALSE_LITERAL.value)

    def test_declaration_node(self):
        """Test the declaration node."""
        context = env.empty_context()
        decl_node = ast.Declaration("val", lib.INTEGER)
        self.assertEqual(decl_node.eval(context), INT_LITERAL.value)
        self.assertEqual(context.find("id", "val"), INT_LITERAL.value)
        self.assertRaises(env.RuntimeException, decl_node.eval, context)

    def test_syntax_tree(self):
        """Test the syntax_tree method."""
        syntax_tree = ast.syntax_tree()
        self.assertTrue(syntax_tree is not None)
        self.assertEqual(syntax_tree.name, ast.Sequence.name)

    def test_run_in_substitution(self):
        """Test the run_in_substitution method."""
        context = env.empty_context()
        access_node = AccessNode()
        result = ast.run_in_substitution(access_node, context)
        self.assertEqual(result, STRING_LITERAL.value)
        self.assertRaises(Exception, context.find, "id",
                          STRING_LITERAL.value.name)
