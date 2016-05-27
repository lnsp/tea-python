"""The unit test for the runtime.lib module."""
import unittest

from runtime import env, lib

INT_VALUE = env.Value(lib.INTEGER, 1)
INT2_VALUE = env.Value(lib.INTEGER, 2)
INT0_VALUE = env.Value(lib.INTEGER, 0)
INTM_VALUE = env.Value(lib.INTEGER, -1)
FLOAT_VALUE = env.Value(lib.FLOAT, 1.0)
FLOAT2_VALUE = env.Value(lib.FLOAT, 2.0)
FLOAT0_VALUE = env.Value(lib.FLOAT, 0.0)
FLOATM_VALUE = env.Value(lib.FLOAT, -1.0)
STRING_VALUE = env.Value(lib.STRING, "Hello", "identifier")
STRING1_VALUE = env.Value(lib.STRING, "Hello1")
LIST_VALUE = env.Value(lib.LIST, ["H", "e", "l", "l", "o"])
SET_VALUE = env.Value(lib.SET, set(LIST_VALUE.data))
TRUE_VALUE = env.Value(lib.BOOLEAN, True, "b")
FALSE_VALUE = env.Value(lib.BOOLEAN, False, None)
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
        self.assertRaises(env.CastException, lib.INTEGER.cast, STRING_VALUE)

    def test_float(self):
        """Test the FLOAT type."""
        self.assertEqual(lib.FLOAT.cast(FLOAT_VALUE), FLOAT_VALUE)
        self.assertEqual(lib.FLOAT.cast(INT_VALUE), FLOAT_VALUE)
        self.assertRaises(env.CastException, lib.FLOAT.cast, STRING_VALUE)

    def test_string(self):
        """Test the STRING type."""
        self.assertEqual(lib.STRING.cast(INT_VALUE),
                         env.Value(lib.STRING, str(INT_VALUE.data)))
        self.assertEqual(lib.STRING.cast(TRUE_VALUE),
                         env.Value(lib.STRING, "true"))
        self.assertEqual(lib.STRING.cast(NULL_VALUE),
                         env.Value(lib.STRING, ""))
        self.assertEqual(lib.STRING.cast(STRING_VALUE), STRING_VALUE)
        self.assertRaises(env.CastException, lib.STRING.cast,
                          env.Value(env.Function))

    def test_boolean(self):
        """Test the BOOLEAN type."""
        self.assertEqual(lib.BOOLEAN.cast(TRUE_VALUE), TRUE_VALUE)
        self.assertEqual(lib.BOOLEAN.cast(INT_VALUE), TRUE_VALUE)
        self.assertRaises(env.CastException, lib.BOOLEAN.cast, FLOAT_VALUE)

    def test_func(self):
        """Test the FUNCTION type."""
        self.assertEqual(lib.FUNCTION.cast(USELESS_FUNCTION), USELESS_FUNCTION)
        self.assertRaises(env.CastException, lib.FUNCTION.cast, INT_VALUE)

    def test_list(self):
        """Test the LIST type."""
        self.assertEqual(lib.LIST.cast(LIST_VALUE), LIST_VALUE)
        self.assertEqual(lib.LIST.cast(STRING_VALUE), LIST_VALUE)
        self.assertRaises(env.CastException, lib.LIST.cast, TRUE_VALUE)

    def test_set(self):
        """Test the SET type."""
        self.assertEqual(lib.SET.cast(SET_VALUE), SET_VALUE)
        self.assertEqual(lib.SET.cast(LIST_VALUE), SET_VALUE)
        self.assertRaises(env.CastException, lib.SET.cast, TRUE_VALUE)

    def test_object(self):
        """Test the OBJECT type."""
        self.assertEqual(lib.OBJECT.cast(OBJECT_VALUE), OBJECT_VALUE)
        self.assertRaises(env.CastException, lib.OBJECT.cast,
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

    def test_div_operation(self):
        """Test the div operator/ function."""
        div_op = lib.DIV_OPERATOR
        context = env.empty_context()

        # Case 1: Two int values -> int
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(div_op.eval(args, context), INT_VALUE)
        # Case 2: Two float values -> float
        args = [FLOAT_VALUE, FLOAT_VALUE]
        self.assertEqual(div_op.eval(args, context), FLOAT_VALUE)
        # Case 3: One int, one float -> int
        args = [INT_VALUE, FLOAT_VALUE]
        self.assertEqual(div_op.eval(args, context), INT_VALUE)
        # Case 4: Division by 0 int
        args = [INT_VALUE, INT0_VALUE]
        self.assertRaises(lib.RuntimeException, div_op.eval, args, context)
        # Case 5: Division by  0 float
        args = [FLOAT_VALUE, FLOAT0_VALUE]
        self.assertRaises(lib.RuntimeException, div_op.eval, args, context)

    def test_equ_operation(self):
        """Test the equ operator / function."""
        equ_op = lib.EQU_OPERATOR
        context = env.empty_context()

        # Case 1: Two int values
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(equ_op.eval(args, context), TRUE_VALUE)
        # Case 2: One float, one int
        args = [FLOAT_VALUE, INT_VALUE]
        self.assertRaises(lib.RuntimeException, equ_op.eval, args, context)
        # Case 3: Two different int values
        args = [INT0_VALUE, INT2_VALUE]
        self.assertEqual(equ_op.eval(args, context), FALSE_VALUE)

    def test_and_operation(self):
        """Test the and operator / function."""
        and_op = lib.AND_OPERATOR
        context = env.empty_context()

        # Case 1: Two true
        args = [TRUE_VALUE, TRUE_VALUE]
        self.assertEqual(and_op.eval(args, context), TRUE_VALUE)
        # Case 2: Two false
        args = [FALSE_VALUE, FALSE_VALUE]
        self.assertEqual(and_op.eval(args, context), FALSE_VALUE)
        # Case 3: One true, one false
        args = [TRUE_VALUE, FALSE_VALUE]
        self.assertEqual(and_op.eval(args, context), FALSE_VALUE)

    def test_or_operation(self):
        """Test the or operator / function."""
        or_op = lib.OR_OPERATOR
        context = env.empty_context()

        # Case 1: Two true
        args = [TRUE_VALUE, TRUE_VALUE]
        self.assertEqual(or_op.eval(args, context), TRUE_VALUE)
        # Case 2: Two false
        args = [FALSE_VALUE, FALSE_VALUE]
        self.assertEqual(or_op.eval(args, context), FALSE_VALUE)
        # Case 3: One false, one true
        args = [TRUE_VALUE, FALSE_VALUE]
        self.assertEqual(or_op.eval(args, context), TRUE_VALUE)

    def test_xor_operation(self):
        """Test the xor operator / function."""
        xor_op = lib.XOR_OPERATOR
        context = env.empty_context()

        # Case 1: Both true
        args = [TRUE_VALUE, TRUE_VALUE]
        self.assertEqual(xor_op.eval(args, context), FALSE_VALUE)
        # Case 2: Two false
        args = [FALSE_VALUE, FALSE_VALUE]
        self.assertEqual(xor_op.eval(args, context), FALSE_VALUE)
        # Case 3: One false, one true
        args = [TRUE_VALUE, FALSE_VALUE]
        self.assertEqual(xor_op.eval(args, context), TRUE_VALUE)

    def test_neq_operation(self):
        """Test the neq operator / function."""
        neq_op = lib.NEQ_OPERATOR
        context = env.empty_context()

        # Case 1: Two int values
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(neq_op.eval(args, context), FALSE_VALUE)

        # Case 2: Two different ints
        args = [INT0_VALUE, INT2_VALUE]
        self.assertEqual(neq_op.eval(args, context), TRUE_VALUE)

        # Case 3: One int, one float
        args = [INT_VALUE, FLOAT_VALUE]
        self.assertRaises(env.RuntimeException, neq_op.eval, args, context)

    def test_sm_operation(self):
        """Test the sm operation."""
        sm_op = lib.SM_OPERATOR
        context = env.empty_context()

        # Case 1.1: Two equal ints
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 1.2: One smaller, one larger int
        args = [INT0_VALUE, INT2_VALUE]
        self.assertEqual(sm_op.eval(args, context), TRUE_VALUE)

        # Case 1.3: One larger, one smaller int
        args = [INT2_VALUE, INT0_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 2.1: Two equal floats
        args = [FLOAT_VALUE, FLOAT_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 2.2: One smaller, one larger float
        args = [FLOAT0_VALUE, FLOAT2_VALUE]
        self.assertEqual(sm_op.eval(args, context), TRUE_VALUE)

        # Case 2.3: One larger, one smaller float
        args = [FLOAT2_VALUE, FLOAT0_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 3.1: Two equal int / float
        args = [FLOAT_VALUE, INT_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 3.2: One larger float, one smaller int
        args = [FLOAT2_VALUE, INT0_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 3.3: One smaller float, one larger int
        args = [FLOAT0_VALUE, INT2_VALUE]
        self.assertEqual(sm_op.eval(args, context), TRUE_VALUE)

        # Case 4.1: Two equal strings
        args = [STRING_VALUE, STRING_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

        # Case 4.2: One smaller, one larger string
        args = [STRING_VALUE, STRING1_VALUE]
        self.assertEqual(sm_op.eval(args, context), TRUE_VALUE)

        # Case 4.3: One larger, one smaller string
        args = [STRING1_VALUE, STRING_VALUE]
        self.assertEqual(sm_op.eval(args, context), FALSE_VALUE)

    def test_lg_operation(self):
        """Test the lg operation."""
        lg_op = lib.LG_OPERATOR
        context = env.empty_context()

        # Case 1.1: Two equal ints
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 1.2: One smaller, one larger int
        args = [INT0_VALUE, INT2_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 1.3: One larger, one smaller int
        args = [INT2_VALUE, INT0_VALUE]
        self.assertEqual(lg_op.eval(args, context), TRUE_VALUE)

        # Case 2.1: Two equal floats
        args = [FLOAT_VALUE, FLOAT_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 2.2: One smaller, one larger float
        args = [FLOAT0_VALUE, FLOAT2_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 2.3: One larger, one smaller float
        args = [FLOAT2_VALUE, FLOAT0_VALUE]
        self.assertEqual(lg_op.eval(args, context), TRUE_VALUE)

        # Case 3.1: Two equal int / float
        args = [FLOAT_VALUE, INT_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 3.2: One larger float, one smaller int
        args = [FLOAT2_VALUE, INT0_VALUE]
        self.assertEqual(lg_op.eval(args, context), TRUE_VALUE)

        # Case 3.3: One smaller float, one larger int
        args = [FLOAT0_VALUE, INT2_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 4.1: Two equal strings
        args = [STRING_VALUE, STRING_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 4.2: One smaller, one larger string
        args = [STRING_VALUE, STRING1_VALUE]
        self.assertEqual(lg_op.eval(args, context), FALSE_VALUE)

        # Case 4.3: One larger, one smaller string
        args = [STRING1_VALUE, STRING_VALUE]
        self.assertEqual(lg_op.eval(args, context), TRUE_VALUE)

    def test_sme_operation(self):
        """Test the sme operation."""
        sme_op = lib.SME_OPERATOR
        context = env.empty_context()

        # Case 1.1: Two equal ints
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 1.2: One smaller, one larger int
        args = [INT0_VALUE, INT2_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 1.3: One larger, one smaller int
        args = [INT2_VALUE, INT0_VALUE]
        self.assertEqual(sme_op.eval(args, context), FALSE_VALUE)

        # Case 2.1: Two equal floats
        args = [FLOAT_VALUE, FLOAT_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 2.2: One smaller, one larger float
        args = [FLOAT0_VALUE, FLOAT2_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 2.3: One larger, one smaller float
        args = [FLOAT2_VALUE, FLOAT0_VALUE]
        self.assertEqual(sme_op.eval(args, context), FALSE_VALUE)

        # Case 3.1: Two equal int / float
        args = [FLOAT_VALUE, INT_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 3.2: One larger float, one smaller int
        args = [FLOAT2_VALUE, INT0_VALUE]
        self.assertEqual(sme_op.eval(args, context), FALSE_VALUE)

        # Case 3.3: One smaller float, one larger int
        args = [FLOAT0_VALUE, INT2_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 4.1: Two equal strings
        args = [STRING_VALUE, STRING_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 4.2: One smaller, one larger string
        args = [STRING_VALUE, STRING1_VALUE]
        self.assertEqual(sme_op.eval(args, context), TRUE_VALUE)

        # Case 4.3: One larger, one smaller string
        args = [STRING1_VALUE, STRING_VALUE]
        self.assertEqual(sme_op.eval(args, context), FALSE_VALUE)

    def test_lge_operation(self):
        """Test the lge operation."""
        lge_op = lib.LGE_OPERATOR
        context = env.empty_context()

        # Case 1.1: Two equal ints
        args = [INT_VALUE, INT_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 1.2: One smaller, one larger int
        args = [INT0_VALUE, INT2_VALUE]
        self.assertEqual(lge_op.eval(args, context), FALSE_VALUE)

        # Case 1.3: One larger, one smaller int
        args = [INT2_VALUE, INT0_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 2.1: Two equal floats
        args = [FLOAT_VALUE, FLOAT_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 2.2: One smaller, one larger float
        args = [FLOAT0_VALUE, FLOAT2_VALUE]
        self.assertEqual(lge_op.eval(args, context), FALSE_VALUE)

        # Case 2.3: One larger, one smaller float
        args = [FLOAT2_VALUE, FLOAT0_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 3.1: Two equal int / float
        args = [FLOAT_VALUE, INT_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 3.3: One smaller float, one larger int
        args = [FLOAT0_VALUE, INT2_VALUE]
        self.assertEqual(lge_op.eval(args, context), FALSE_VALUE)

        # Case 3.2: One larger float, one smaller int
        args = [FLOAT2_VALUE, INT0_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 4.1: Two equal strings
        args = [STRING_VALUE, STRING_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

        # Case 4.2: One smaller, one larger string
        args = [STRING_VALUE, STRING1_VALUE]
        self.assertEqual(lge_op.eval(args, context), FALSE_VALUE)

        # Case 4.3: One larger, one smaller string
        args = [STRING1_VALUE, STRING_VALUE]
        self.assertEqual(lge_op.eval(args, context), TRUE_VALUE)

    def test_unmi_operation(self):
        unmi_op = lib.UNMI_OPERATOR
        context = env.empty_context()

        # Case 1.1: - (1) -> -1
        args = [INT_VALUE]
        self.assertEqual(unmi_op.eval(args, context), INTM_VALUE)
        # Case 1.2: - (-1) -> 1
        args = [INTM_VALUE]
        self.assertEqual(unmi_op.eval(args, context), INT_VALUE)
        # Case 1.3: - (0) -> 0
        args = [INT0_VALUE]
        self.assertEqual(unmi_op.eval(args, context), INT0_VALUE)

        # Case 2.1: - (1.0) -> 1.0
        args = [FLOAT_VALUE]
        self.assertEqual(unmi_op.eval(args, context), FLOATM_VALUE)
        # Case 2.2: - (-1.0) -> 1.0
        args = [FLOATM_VALUE]
        self.assertEqual(unmi_op.eval(args, context), FLOAT_VALUE)
        # Case 2.3: - (0.0) -> 0.0
        args = [FLOAT0_VALUE]
        self.assertEqual(unmi_op.eval(args, context), FLOAT0_VALUE)
