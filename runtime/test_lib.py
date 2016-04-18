import unittest

from runtime import env, lib

int_value = env.Value(lib.Integer, 1)
int2_value = env.Value(lib.Integer, 2)
float_value = env.Value(lib.Float, 1.0)
float2_value = env.Value(lib.Float, 2.0)
string_value = env.Value(lib.String, "Hello", "identifier")
string1_value = env.Value(lib.String, "Hello1")
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

class TestLib(unittest.TestCase):
    def test_integer(self):
        """Test the Integer type."""
        self.assertEqual(lib.Integer.cast(int_value), int_value)
        self.assertEqual(lib.Integer.cast(float_value), int_value)
        self.assertRaises(env.CastError, lib.Integer.cast, string_value)
        
    def test_float(self):
        """Test the Float type."""
        self.assertEqual(lib.Float.cast(float_value), float_value)
        self.assertEqual(lib.Float.cast(int_value), float_value)
        self.assertRaises(env.CastError, lib.Float.cast, string_value)
   
    def test_string(self):
        """Test the String type."""
        self.assertEqual(lib.String.cast(int_value), env.Value(lib.String, str(int_value.data)))
        self.assertEqual(lib.String.cast(bool_value), env.Value(lib.String, "true"))
        self.assertEqual(lib.String.cast(null_value), env.Value(lib.String, "null"))
        self.assertEqual(lib.String.cast(string_value), string_value)
        self.assertRaises(env.CastError, lib.String.cast, env.Value(env.Function))
        
    def test_boolean(self):
        """Test the Boolean type."""
        self.assertEqual(lib.Boolean.cast(bool_value), bool_value)
        self.assertEqual(lib.Boolean.cast(int_value), bool_value)
        self.assertRaises(env.CastError, lib.Boolean.cast, float_value)
        
    def test_func(self):
        """Test the Func type."""
        self.assertEqual(lib.Func.cast(empty_function), empty_function)
        self.assertRaises(env.CastError, lib.Func.cast, int_value)
        
    def test_list(self):
        """Test the List type."""
        self.assertEqual(lib.List.cast(list_value), list_value)
        self.assertEqual(lib.List.cast(string_value), list_value)
        self.assertRaises(env.CastError, lib.List.cast, bool_value)
        
    def test_set(self):
        """Test the Set type."""
        self.assertEqual(lib.Set.cast(set_value), set_value)
        self.assertEqual(lib.Set.cast(list_value), set_value)
        self.assertRaises(env.CastError, lib.Set.cast, bool_value)
    
    def test_object(self):
        """Test the Object type."""
        self.assertEqual(lib.Object.cast(object_value), object_value)
        self.assertRaises(env.CastError, lib.Object.cast, missing_operator)
        
    def test_add_operation(self):
        """Test the add operator / function."""
        add_op = lib.AddOperator
        context = env.empty_context()
        
        # Case 1: Two int values -> int value
        args = [
            int_value,
            int_value,
        ]
        self.assertEqual(add_op.eval(args, context), int2_value)
        
        # Case 2: Two float values -> float value
        args = [
            float_value,
            float_value,
        ]
        self.assertEqual(add_op.eval(args, context), float2_value)
        
        # Case 3: First int, second float -> int
        args = [
            int_value,
            float_value,
        ]
        self.assertEqual(add_op.eval(args, context), int2_value)
        
        # Case 4: string + int -> string
        args = [
            string_value,
            int_value,
        ]
        self.assertEqual(add_op.eval(args, context), string1_value)