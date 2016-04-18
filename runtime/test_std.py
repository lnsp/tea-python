import unittest
from runtime import env, ast, lib

int_value = env.Value(lib.Integer, 1)
float_value = env.Value(lib.Float, 1.0)
string_value = env.Value(lib.String, "Hello", "identifier")
list_value = env.Value(lib.List, ["H", "e", "l", "l", "o"])
set_value = env.Value(lib.Set, set(list_value.data))
bool_value = env.Value(lib.Boolean, True, "b")
true_str_value = env.Value(lib.String, "true")
missing_value = env.Value(lib.Integer, 0, "missing")
null_value = env.Value(env.Null)
example_operator = env.Operator(None, "+")
missing_operator = env.Operator(None, "?")
empty_function = env.Value(lib.Func, None)
object_value = env.Value(lib.Object, None)


class TestStd(unittest.TestCase):

    def test_namespace(self):
        """Test the Namespace class."""
        ns = env.Namespace(None)
        self.assertEqual(ns.parent, None)
        self.assertRaises(Exception, ns.find, "id", "identifier")
        self.assertRaises(Exception, ns.find, "op", "operator")
        # store example operator
        ns.store(string_value)
        ns.store(example_operator)
        self.assertEqual(ns.find("id", string_value.name), string_value)
        self.assertEqual(
            ns.find("op", example_operator.symbol), example_operator)
        # test upper namspace
        sub = ns.child()
        self.assertEqual(ns.find("id", string_value.name), string_value)
        self.assertEqual(
            ns.find("op", example_operator.symbol), example_operator)
        # check independence
        sub.store(missing_value)
        sub.store(missing_operator)
        self.assertRaises(Exception, ns.find, "id", missing_value.name)
        self.assertRaises(Exception, ns.find, "op", missing_operator.symbol)

    def test_type(self):
        """Test the Type class."""
        self.assertTrue(lib.Integer.kind_of(lib.Number))
        self.assertTrue(lib.Float.kind_of(lib.Number))
        self.assertTrue(lib.Integer.kind_of(env.Any))

    def test_signature(self):
        """Test the signature class."""
        expected_values = [
            env.Value(lib.Number, None, "x"),
            env.Value(lib.Number, None, "delta"),
            env.Value(lib.Float, -1.0, "phi"),
        ]
        sign = env.Signature(expected_values, "works!")
        # Case 1: Too many arguments
        first_case = [
            env.Value(lib.Integer, 3),
            env.Value(lib.Float, 3.0),
            env.Value(lib.Float, -3.0),
            env.Value(lib.Integer, 3.0),
        ]
        self.assertRaises(env.ArgumentError, sign.match, first_case)

        # Case 2: Too less arguments
        second_case = [
            env.Value(lib.Integer, 3),
        ]
        self.assertRaises(env.ArgumentError, sign.match, second_case)

        # Case 3: Fitting arguments
        third_case = [
            env.Value(lib.Integer, 3),
            env.Value(lib.Integer, 0),
            env.Value(lib.Float, 0.0),
        ]
        third_case_result = [
            env.Value(lib.Integer, 3, "x"),
            env.Value(lib.Integer, 0, "delta"),
            env.Value(lib.Float, 0.0, "phi"),
        ]
        self.assertEqual(sign.match(third_case), (third_case_result, "works!"))

        # Case 4: default values
        fourth_case = [
            env.Value(lib.Integer, 3),
            env.Value(lib.Integer, 0),
        ]
        fourth_case_result = [
            env.Value(lib.Integer, 3, "x"),
            env.Value(lib.Integer, 0, "delta"),
            env.Value(lib.Float, -1.0, "phi"),
        ]
        self.assertEqual(sign.match(fourth_case),
                         (fourth_case_result, "works!"))

    def test_function(self):
        """Test the function class."""
        context = env.empty_context()

        # Function without signatures
        func = env.Function([])
        self.assertRaises(env.FunctionError, func.eval, [], context)

        # Function with one signature, perfect match
        identifier_literal = ast.Identifier("str")
        func = env.Function([
            env.Signature([env.Value(lib.String, None, "str")],
                          identifier_literal),
        ])
        args = [
            string_value,
        ]
        self.assertEqual(func.eval(args, context), string_value)

        # Function with one signature, optional argument
        func = env.Function([
            env.Signature(
                [env.Value(lib.String, string_value.data, "str")], identifier_literal),
        ])
        self.assertEqual(func.eval(args, context), string_value)

        # Function with two signatures, second perfect match
        func = env.Function([
            env.Signature([env.Value(lib.Integer, None, "i")], None),
            env.Signature([env.Value(lib.String, None, "str")],
                          identifier_literal),
        ])
        self.assertEqual(func.eval(args, context), string_value)

        # Check function sandboxing
        class CustomNode(ast.Node):
            name = "custom"

            def __init__(self):
                super().__init__()

            def eval(self, context):
                context.store(env.Value(lib.Integer, 1, "x"))
                return env.Value(env.Null)
        func = env.Function([
            env.Signature([], CustomNode()),
        ])
        self.assertRaises(Exception, context.find, "id", "x")

    def test_operator(self):
        """Test the operator class."""
        context = env.empty_context()
        int_literal = ast.Literal(int_value)
        # Test forwarding
        func = env.Function([
            env.Signature([], int_literal)
        ])
        operator = env.Operator(func, "+")
        self.assertEqual(str(operator), "<Operator (+)>")
        self.assertEqual(operator.eval([], context), int_value)
