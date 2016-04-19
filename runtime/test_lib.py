"""The unit test for the runtime.lib module."""
import unittest

from runtime import env, lib

INT_VALUE = env.Value(lib.INTEGER, 1)
INT2_VALUE = env.Value(lib.INTEGER, 2)
FLOAT_VALUE = env.Value(lib.FLOAT, 1.0)
FLOAT2_VALUE = env.Value(lib.FLOAT, 2.0)
STRING_VALUE = env.Value(lib.STRING, "Hello", "identifier")
STRING1_VALUE = env.Value(lib.STRING, "Hello1")
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


class TestLib(unittest.TestCase):
    """Test cases for runtime library."""

    def test_integer(self):
        """Test the Integer type."""
        self.assertEqual(lib.INTEGER.cast(INT_VALUE), INT_VALUE)
        self.assertEqual(lib.INTEGER.cast(FLOAT_VALUE), INT_VALUE)
        self.assertRaises(env.CastError, lib.INTEGER.cast, STRING_VALUE)

    def test_float(self):
        """Test the FLOAT type."""
        self.assertEqual(lib.FLOAT.cast(FLOAT_VALUE), FLOAT_VALUE)
        self.assertEqual(lib.FLOAT.cast(INT_VALUE), FLOAT_VALUE)
        self.assertRaises(env.CastError, lib.FLOAT.cast, STRING_VALUE)

    def test_string(self):
        """Test the STRING type."""
        self.assertEqual(lib.STRING.cast(INT_VALUE),
                         env.Value(lib.STRING, str(INT_VALUE.data)))
        self.assertEqual(lib.STRING.cast(BOOL_VALUE),
                         env.Value(lib.STRING, "true"))
        self.assertEqual(lib.STRING.cast(NULL_VALUE),
                         env.Value(lib.STRING, ""))
        self.assertEqual(lib.STRING.cast(STRING_VALUE), STRING_VALUE)
        self.assertRaises(env.CastError, lib.STRING.cast,
                          env.Value(env.Function))

    def test_boolean(self):
        """Test the BOOLEAN type."""
        self.assertEqual(lib.BOOLEAN.cast(BOOL_VALUE), BOOL_VALUE)
        self.assertEqual(lib.BOOLEAN.cast(INT_VALUE), BOOL_VALUE)
        self.assertRaises(env.CastError, lib.BOOLEAN.cast, FLOAT_VALUE)

    def test_func(self):
        """Test the FUNCTION type."""
        self.assertEqual(lib.FUNCTION.cast(USELESS_FUNCTION), USELESS_FUNCTION)
        self.assertRaises(env.CastError, lib.FUNCTION.cast, INT_VALUE)

    def test_list(self):
        """Test the LIST type."""
        self.assertEqual(lib.LIST.cast(LIST_VALUE), LIST_VALUE)
        self.assertEqual(lib.LIST.cast(STRING_VALUE), LIST_VALUE)
        self.assertRaises(env.CastError, lib.LIST.cast, BOOL_VALUE)

    def test_set(self):
        """Test the SET type."""
        self.assertEqual(lib.SET.cast(SET_VALUE), SET_VALUE)
        self.assertEqual(lib.SET.cast(LIST_VALUE), SET_VALUE)
        self.assertRaises(env.CastError, lib.SET.cast, BOOL_VALUE)

    def test_object(self):
        """Test the OBJECT type."""
        self.assertEqual(lib.OBJECT.cast(OBJECT_VALUE), OBJECT_VALUE)
        self.assertRaises(env.CastError, lib.OBJECT.cast,
                          ANOTHER_USELESS_OPERATOR)

    def test_add_operation(self):
        """Test the add operator / function."""
        add_op = lib.ADD_OPERATOR
        context = env.empty_context()

        # Case 1: Two int values -> int value
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(add_op.eval(args, context), INT2_VALUE)

        # Case 2: Two float values -> float value
        args = [FLOAT_VALUE, FLOAT_VALUE]
        self.assertEqual(add_op.eval(args, context), FLOAT2_VALUE)

        # Case 3: First int, second float -> int
        args = [INT_VALUE, FLOAT_VALUE]
        self.assertEqual(add_op.eval(args, context), INT2_VALUE)

        # Case 4: string + int -> string
        args = [STRING_VALUE, INT_VALUE]
        self.assertEqual(add_op.eval(args, context), STRING1_VALUE)

    def test_sub_operation(self):
        """Test the sub operator / function."""
        sub_op = lib.SUB_OPERATOR
        context = env.empty_context()

        # Case 1: Two int values -> int value
        args = [INT2_VALUE, INT_VALUE]
        self.assertEqual(sub_op.eval(args, context), INT_VALUE)
        # Case 2: Two float values -> float
        args = [FLOAT2_VALUE, FLOAT_VALUE]
        self.assertEqual(sub_op.eval(args, context), FLOAT_VALUE)
        # Case 3: First float, second int -> float
        args = [FLOAT2_VALUE, INT_VALUE]
        self.assertEqual(sub_op.eval(args, context), FLOAT_VALUE)

    def test_mul_operation(self):
        """Test the mul operator / function."""
        mul_op = lib.MUL_OPERATOR
        context = env.empty_context()

        # Case 1: Two int values -> int
        args = [INT_VALUE, INT2_VALUE]
        self.assertEqual(mul_op.eval(args, context), INT2_VALUE)
        # Case 2: Two float values -> float
        args = [FLOAT2_VALUE, FLOAT_VALUE]
        self.assertEqual(mul_op.eval(args, context), FLOAT2_VALUE)
        # Case 3: First float, second int -> float
        args = [FLOAT2_VALUE, INT_VALUE]
        self.assertEqual(mul_op.eval(args, context), FLOAT2_VALUE)
