"""Unit test for runtime.env"""
import unittest
import collections
from runtime import env, ast, lib

INT_VALUE = env.Value(lib.INTEGER, 1, "x")
FLOAT_VALUE = env.Value(lib.FLOAT, 1.0, "y")
STRING_VALUE = env.Value(lib.STRING, "Hello", "identifier")
LIST_VALUE = env.Value(lib.LIST, ["H", "e", "l", "l", "o"])
SET_VALUE = env.Value(lib.SET, set(LIST_VALUE.data))
BOOL_VALUE = env.Value(lib.BOOLEAN, True, "b")
TRUE_STRING_VALUE = env.Value(lib.STRING, "true")
MISSING_INT_VALUE = env.Value(lib.INTEGER, 0, "missing")
NULL_VALUE = env.Value(env.NULL)
USELESS_OPERATOR = env.Operator(None, "+")
ANOTHER_USELESS_OPERATOR = env.Operator(None, "?")
USELESS_FUNCTION = env.Value(lib.FUNCTION, None)
OBJECT_VALUE = env.Value(lib.OBJECT, None)
LIBRARY = collections.namedtuple("Library", "EXPORTS")


class TestEnv(unittest.TestCase):
    """Test cases for the runtime environment."""

    def test_namespace(self):
        """Test the Namespace class."""
        namespace = env.Namespace(None)
        self.assertEqual(namespace.parent, None)
        self.assertRaises(Exception, namespace.find, "id", "identifier")
        self.assertRaises(Exception, namespace.find, "op", "operator")
        # store example operator
        namespace.store(STRING_VALUE)
        namespace.store(USELESS_OPERATOR)
        self.assertEqual(namespace.find("id", STRING_VALUE.name), STRING_VALUE)
        self.assertEqual(
            namespace.find("op", USELESS_OPERATOR.symbol), USELESS_OPERATOR)
        # test upper namspace
        sub = namespace.child()
        self.assertEqual(namespace.find("id", STRING_VALUE.name), STRING_VALUE)
        self.assertEqual(
            namespace.find("op", USELESS_OPERATOR.symbol), USELESS_OPERATOR)
        # check independence
        sub.store(MISSING_INT_VALUE)
        sub.store(ANOTHER_USELESS_OPERATOR)
        self.assertRaises(Exception, namespace.find,
                          "id", MISSING_INT_VALUE.name)
        self.assertRaises(Exception, namespace.find, "op",
                          ANOTHER_USELESS_OPERATOR.symbol)

    def test_datatype(self):
        """Test the Datatype class."""
        self.assertTrue(lib.INTEGER.kind_of(lib.NUMBER))
        self.assertTrue(lib.FLOAT.kind_of(lib.NUMBER))
        self.assertTrue(lib.INTEGER.kind_of(env.ANY))

    def test_context(self):
        """Test the Context class."""
        namespace = env.Namespace(None)
        context = env.Context(namespace)
        context.store(INT_VALUE)
        self.assertEqual(context.find("id", INT_VALUE.name), INT_VALUE)
        self.assertRaises(Exception, context.find, "id", STRING_VALUE.name)
        custom_library = LIBRARY(EXPORTS=[STRING_VALUE])
        context.load(custom_library)
        self.assertEqual(context.find("id", STRING_VALUE.name), STRING_VALUE)
        self.assertIs(context.substitute(), namespace)
        self.assertIsNot(context.namespace, namespace)

    def test_value(self):
        """Test the Value class."""
        self.assertNotEqual(INT_VALUE, FLOAT_VALUE)
        self.assertEqual(INT_VALUE, INT_VALUE)
        self.assertEqual(str(NULL_VALUE), "<Value ? <T null> *(None)>")

    def test_signature(self):
        """Test the signature class."""
        expected_values = [
            env.Value(lib.NUMBER, None, "x"),
            env.Value(lib.NUMBER, None, "delta"),
            env.Value(lib.FLOAT, -1.0, "phi"),
        ]
        sign = env.Signature(expected_values, "works!")
        # Case 1: Too many arguments
        first_case = [
            env.Value(lib.INTEGER, 3),
            env.Value(lib.FLOAT, 3.0),
            env.Value(lib.FLOAT, -3.0),
            env.Value(lib.INTEGER, 3.0),
        ]
        self.assertRaises(env.ArgumentError, sign.match, first_case)

        # Case 2: Too less arguments
        second_case = [
            env.Value(lib.INTEGER, 3),
        ]
        self.assertRaises(env.ArgumentError, sign.match, second_case)

        # Case 3: Fitting arguments
        third_case = [
            env.Value(lib.INTEGER, 3),
            env.Value(lib.INTEGER, 0),
            env.Value(lib.FLOAT, 0.0),
        ]
        third_case_result = [
            env.Value(lib.INTEGER, 3, "x"),
            env.Value(lib.INTEGER, 0, "delta"),
            env.Value(lib.FLOAT, 0.0, "phi"),
        ]
        self.assertEqual(sign.match(third_case), (third_case_result, "works!"))

        # Case 4: default values
        fourth_case = [
            env.Value(lib.INTEGER, 3),
            env.Value(lib.INTEGER, 0),
        ]
        fourth_case_result = [
            env.Value(lib.INTEGER, 3, "x"),
            env.Value(lib.INTEGER, 0, "delta"),
            env.Value(lib.FLOAT, -1.0, "phi"),
        ]
        self.assertEqual(sign.match(fourth_case),
                         (fourth_case_result, "works!"))

    def test_function(self):
        """Test the function class."""
        context = env.empty_context()

        # FUNCTIONtion without signatures
        func = env.Function([])
        self.assertRaises(env.FunctionError, func.eval, [], context)

        # FUNCTIONtion with one signature, perfect match
        identifier_literal = ast.Identifier("str")
        func = env.Function([
            env.Signature([env.Value(lib.STRING, None, "str")],
                          identifier_literal),
        ])
        args = [
            STRING_VALUE,
        ]
        self.assertEqual(func.eval(args, context), STRING_VALUE)

        # FUNCTIONtion with one signature, optional argument
        func = env.Function([
            env.Signature(
                [env.Value(lib.STRING, STRING_VALUE.data, "str")], identifier_literal),
        ])
        self.assertEqual(func.eval(args, context), STRING_VALUE)

        # FUNCTIONtion with two signatures, second perfect match
        func = env.Function([
            env.Signature([env.Value(lib.INTEGER, None, "i")], None),
            env.Signature([env.Value(lib.STRING, None, "str")],
                          identifier_literal),
        ])
        self.assertEqual(func.eval(args, context), STRING_VALUE)

        # Check function sandboxing
        class CustomNode(ast.Node):
            """A custom node."""
            name = "custom"

            def __init__(self):
                super().__init__()

            @classmethod
            def eval(cls, context):
                """Stores a an INTEGER at x."""
                context.store(env.Value(lib.INTEGER, 1, "x"))
                return env.Value(env.NULL)

        func = env.Function([
            env.Signature([], CustomNode()),
        ])
        self.assertRaises(Exception, context.find, "id", "x")

    def test_operator(self):
        """Test the operator class."""
        context = env.empty_context()
        int_literal = ast.Literal(INT_VALUE)
        # Test forwarding
        func = env.Function([
            env.Signature([], int_literal)
        ])
        operator = env.Operator(func, "+")
        self.assertEqual(str(operator), "<Operator (+)>")
        self.assertEqual(operator.eval([], context), INT_VALUE)
