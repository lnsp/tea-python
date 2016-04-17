import unittest
from runtime import std

int_value = std.Value(std.Integer, 1)
float_value = std.Value(std.Float, 1.0)
string_value = std.Value(std.String, "Hello", "identifier")
list_value = std.Value(std.List, ["H", "e", "l", "l", "o"])
set_value = std.Value(std.List, set([list_value]))
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