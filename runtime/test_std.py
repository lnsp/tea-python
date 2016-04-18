import unittest
from runtime import std, ast

int_value = std.Value(std.Integer, 1)
float_value = std.Value(std.Float, 1.0)
string_value = std.Value(std.String, "Hello", "identifier")
list_value = std.Value(std.List, ["H", "e", "l", "l", "o"])
set_value = std.Value(std.Set, set(list_value.data))
bool_value = std.Value(std.Boolean, True, "b")
true_str_value = std.Value(std.String, "true")
missing_value = std.Value(std.Integer, 0, "missing")
null_value = std.Value(std.Null)
example_operator = std.Operator(None, "+")
missing_operator = std.Operator(None, "?")
empty_function = std.Value(std.Func, None)
object_value = std.Value(std.Object, None)

class TestStd(unittest.TestCase):
    def test_namespace(self):
        """Test the Namespace class."""
        ns = std.Namespace(None)
        self.assertEqual(ns.parent, None)
        self.assertRaises(Exception, ns.find, "id", "identifier")
        self.assertRaises(Exception, ns.find, "op", "operator")
        # store example operator
        ns.store(string_value)
        ns.store(example_operator)
        self.assertEqual(ns.find("id", string_value.name), string_value)
        self.assertEqual(ns.find("op", example_operator.symbol), example_operator)
        # test upper namspace
        sub = ns.child()
        self.assertEqual(ns.find("id", string_value.name), string_value)
        self.assertEqual(ns.find("op", example_operator.symbol), example_operator)
        # check independence
        sub.store(missing_value)
        sub.store(missing_operator)
        self.assertRaises(Exception, ns.find, "id", missing_value.name)
        self.assertRaises(Exception, ns.find, "op", missing_operator.symbol)

    def test_default_namespace(self):
        """Test the default_namespace method."""
        ns = std.default_namespace()
        self.assertEqual(ns.parent, None)
   
    def test_default_context(self):
        """Test the default_context method."""
        context = std.default_context()
        self.assertEqual(context.globalns, context.ns)
    
    def test_integer(self):
        """Test the Integer type."""
        self.assertEqual(std.Integer.cast(int_value), int_value)
        self.assertEqual(std.Integer.cast(float_value), int_value)
        self.assertRaises(std.CastError, std.Integer.cast, string_value)
        
    def test_float(self):
        """Test the Float type."""
        self.assertEqual(std.Float.cast(float_value), float_value)
        self.assertEqual(std.Float.cast(int_value), float_value)
        self.assertRaises(std.CastError, std.Float.cast, string_value)
   
    def test_string(self):
        """Test the String type."""
        self.assertEqual(std.String.cast(int_value), std.Value(std.String, str(int_value.data)))
        self.assertEqual(std.String.cast(bool_value), std.Value(std.String, "true"))
        self.assertEqual(std.String.cast(null_value), std.Value(std.String, "null"))
        self.assertEqual(std.String.cast(string_value), string_value)
        self.assertRaises(std.CastError, std.String.cast, std.Value(std.Function))
        
    def test_boolean(self):
        """Test the Boolean type."""
        self.assertEqual(std.Boolean.cast(bool_value), bool_value)
        self.assertEqual(std.Boolean.cast(int_value), bool_value)
        self.assertRaises(std.CastError, std.Boolean.cast, float_value)
        
    def test_null(self):
        """Test the Null type."""
        self.assertEqual(std.Null.cast(string_value), null_value)
        self.assertEqual(std.Null.cast(int_value), null_value)
        self.assertRaises(std.CastError, std.Null.cast, missing_operator)
        
    def test_func(self):
        """Test the Func type."""
        self.assertEqual(std.Func.cast(empty_function), empty_function)
        self.assertRaises(std.CastError, std.Func.cast, int_value)
        
    def test_list(self):
        """Test the List type."""
        self.assertEqual(std.List.cast(list_value), list_value)
        self.assertEqual(std.List.cast(string_value), list_value)
        self.assertRaises(std.CastError, std.List.cast, bool_value)
        
    def test_set(self):
        """Test the Set type."""
        self.assertEqual(std.Set.cast(set_value), set_value)
        self.assertEqual(std.Set.cast(list_value), set_value)
        self.assertRaises(std.CastError, std.Set.cast, bool_value)
    
    def test_object(self):
        """Test the Object type."""
        self.assertEqual(std.Object.cast(object_value), object_value)
        self.assertRaises(std.CastError, std.Object.cast, missing_operator)
        
    def test_signature(self):
        """Test the signature class."""
        expected_values = [
            std.Value(std.Integer, None, "x"),
            std.Value(std.Float, None, "delta"),
            std.Value(std.Float, -1.0, "phi"),
        ]
        sign = std.Signature(expected_values, "works!")
        # Case 1: Too many arguments
        first_case = [
            std.Value(std.Integer, 3),
            std.Value(std.Float, 3.0),
            std.Value(std.Float, -3.0),
            std.Value(std.Integer, 3.0),
        ]
        self.assertRaises(std.ArgumentError, sign.match, first_case)
        
        # Case 2: Too less arguments
        second_case = [
            std.Value(std.Integer, 3),
        ]
        self.assertRaises(std.ArgumentError, sign.match, second_case)
        
        # Case 3: Fitting arguments
        third_case =  [
            std.Value(std.Integer, 3),
            std.Value(std.Integer, 0),
            std.Value(std.Float, 0.0),
        ]
        third_case_result = [
            std.Value(std.Integer, 3, "x"),
            std.Value(std.Float, 0.0, "delta"),
            std.Value(std.Float, 0.0, "phi"),
        ]
        self.assertEqual(sign.match(third_case), (third_case_result, "works!"))
        
        # Case 4: default values
        fourth_case = [
            std.Value(std.Integer, 3),
            std.Value(std.Integer, 0),
        ]
        fourth_case_result = [
            std.Value(std.Integer, 3, "x"),
            std.Value(std.Float, 0.0, "delta"),
            std.Value(std.Float, -1.0, "phi"),
        ]
        self.assertEqual(sign.match(fourth_case), (fourth_case_result, "works!"))
        
    def test_function(self):
        """Test the function class."""
        context = std.default_context()
        
        # Function without signatures
        func = std.Function([])
        self.assertRaises(std.FunctionError, func.eval, [], context)
        
        # Function with one signature, perfect match
        identifier_literal = ast.Identifier("str")
        func = std.Function([
            std.Signature([std.Value(std.String, None, "str")], identifier_literal),
        ])
        args = [
            string_value,
        ]
        self.assertEqual(func.eval(args, context), string_value)
        
        # Function with one signature, optional argument
        func = std.Function([
            std.Signature([std.Value(std.String, string_value.data, "str")], identifier_literal),
        ])
        self.assertEqual(func.eval(args, context), string_value)
        
        # Function with two signatures, second perfect match
        func = std.Function([
            std.Signature([std.Value(std.Integer, None, "i")], None),
            std.Signature([std.Value(std.String, None, "str")], identifier_literal),
        ])
        self.assertEqual(func.eval(args, context), string_value)
        
        # Check function sandboxing
        class CustomNode(ast.Node):
            name = "custom"
            
            def __init__(self):
                super().__init__()
            
            def eval(self, context):
                context.store(std.Value(std.Integer, 1, "x"))
                return std.Value(std.Null)
        func = std.Function([
            std.Signature([], CustomNode()),
        ])
        self.assertRaises(Exception, context.find, "id", "x")
        
    def test_operator(self):
        """Test the operator class."""
        context = std.default_context()
        int_literal = ast.Literal(int_value)
        # Test forwarding
        func = std.Function([
            std.Signature([], int_literal)
        ])
        operator = std.Operator(func, "+")
        self.assertEqual(str(operator), "<Operator (+)>")
        self.assertEqual(operator.eval([], context), int_value)