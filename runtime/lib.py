"""The standard runtime library."""
from runtime.env import (Datatype, Value, Function, Operator,
                         Signature, FunctionBinding, CastException, ANY, NULL,
                         RuntimeException)

NUMBER = Datatype("*number", None, ANY)


def cast_integer(value):
    """Casts a value to an INTEGER."""
    if isinstance(value, Value):
        if value.datatype in (FLOAT, INTEGER):
            return Value(INTEGER, int(value.data))
        if value.datatype is BOOLEAN:
            return Value(INTEGER, 1 if value.data else 0)
        if value.datatype is NULL:
            return Value(INTEGER, 0)
    raise CastException(value, INTEGER)

INTEGER = Datatype("int", cast_integer, NUMBER)


def cast_float(value):
    """Casts a value to a FLOAT."""
    if isinstance(value, Value):
        if value.datatype in (FLOAT, INTEGER):
            return Value(FLOAT, float(value.data))
        if value.datatype is NULL:
            return Value(FLOAT, 0.0)
    raise CastException(value, FLOAT)

FLOAT = Datatype("float", cast_float, NUMBER)


def cast_string(value):
    """Casts a value to a STRING."""
    if isinstance(value, Value):
        if value.datatype in (INTEGER, FLOAT, STRING):
            return Value(STRING, str(value.data))
        if value.datatype is BOOLEAN:
            return Value(STRING, "true" if value.data else "false")
        if value.datatype is NULL:
            return Value(STRING, "")
    raise CastException(value, STRING)

STRING = Datatype("string", cast_string, ANY)


def cast_boolean(value):
    """Casts a value to a BOOLEAN."""
    if isinstance(value, Value):
        if value.datatype is INTEGER:
            return Value(BOOLEAN, True if value.data > 0 else False)
        if value.datatype is BOOLEAN:
            return Value(BOOLEAN, bool(value.data))
        if value.datatype is NULL:
            return Value(NULL, False)
    raise CastException(value, BOOLEAN)

BOOLEAN = Datatype("bool", cast_boolean, ANY)


def cast_function(value):
    """Casts a value to a FUNCTION."""
    if isinstance(value, Value):
        if value.datatype is FUNCTION:
            return Value(FUNCTION, value.data)
        if value.datatype is NULL:
            return Value(FUNCTION, None)
    raise CastException(value, FUNCTION)

FUNCTION = Datatype("func", cast_function, ANY)


def cast_list(value):
    """Casts a value to a LIST."""
    if isinstance(value, Value):
        if value.datatype in (LIST, STRING):
            return Value(LIST, list(value.data))
        if value.datatype is NULL:
            return Value(LIST, [])
    raise CastException(value, LIST)

LIST = Datatype("LIST", cast_list, ANY)


def cast_map(value):
    """Casts a value to a MAP."""
    if isinstance(value, Value):
        if value.datatype is MAP:
            return Value(MAP, dict(value.data))
        if value.datatype is NULL:
            return Value(MAP, dict())
    raise CastException(value, MAP)

MAP = Datatype("map", cast_map, ANY)


def cast_set(value):
    """Casts a value to a SET."""
    if isinstance(value, Value):
        if value.datatype in (SET, LIST):
            return Value(SET, set(value.data))
        if value.datatype is NULL:
            return Value(SET, set())
    raise CastException(value, SET)

SET = Datatype("set", cast_set, ANY)


def cast_object(value):
    """Casts a value to an OBJECT."""
    if isinstance(value, Value):
        return Value(OBJECT, value.data)
    raise CastException(value, OBJECT)

OBJECT = Datatype("object", cast_object, ANY)


def _add_operation():
    """The add operation."""
    def add(context):
        """Add two number values."""
        var_a = context.find("id", "a")
        var_b = var_a.datatype.cast(context.find("id", "b"))
        return Value(var_a.datatype, var_a.data + var_b.data)

    add_node = FunctionBinding(add)

    signatures = [
        Signature([
            Value(NUMBER, None, "a"),
            Value(NUMBER, None, "b"),
        ], add_node),
        Signature([
            Value(STRING, None, "a"),
            Value(ANY, None, "b"),
        ], add_node),
    ]
    return Function(signatures, "#add")

ADD_FUNCTION = _add_operation()
ADD_OPERATOR = Operator(ADD_FUNCTION, "+")


def _sub_function():
    """The sub operation."""
    def sub(context):
        """Subtract two number values."""
        var_a = context.find("id", "a")
        var_b = var_a.datatype.cast(context.find("id", "b"))
        return Value(var_a.datatype, var_a.data - var_b.data)

    sub_node = FunctionBinding(sub)
    signatures = [
        Signature([
            Value(NUMBER, None, "a"),
            Value(NUMBER, None, "b"),
        ], sub_node),
    ]
    return Function(signatures, "#sub")

SUB_FUNCTION = _sub_function()
SUB_OPERATOR = Operator(SUB_FUNCTION, "-")


def _mul_operation():
    def mul(context):
        """Multiply two numbers."""
        var_a = context.find("id", "a")
        var_b = var_a.datatype.cast(context.find("id", "b"))
        return Value(var_a.datatype, var_a.data * var_b.data)

    mul_node = FunctionBinding(mul)
    signatures = [
        Signature([
            Value(NUMBER, None, "a"),
            Value(NUMBER, None, "b"),
        ], mul_node),
    ]
    return Function(signatures, "#mul")

MUL_FUNCTION = _mul_operation()
MUL_OPERATOR = Operator(MUL_FUNCTION, "*")

def _div_operation():
    def div(context):
        """Divide two numbers."""
        var_a = context.find("id", "a")
        var_b = var_a.datatype.cast(context.find("id", "b"))
        if var_b.data == 0:
            raise RuntimeException("Can not divide by 0")
        result = var_a.data / var_b.data
        if var_a.datatype is INTEGER:
            result = int(result)
        return Value(var_a.datatype, result)

    div_node = FunctionBinding(div)
    signatures = [
        Signature([
            Value(NUMBER, None, "a"),
            Value(NUMBER, None, "b"),
        ], div_node)
    ]
    return Function(signatures, "#div")

DIV_FUNCTION = _div_operation()
DIV_OPERATOR = Operator(DIV_FUNCTION, "/")

def _equ_operation():
    def equ(context):
        """Checks if two values are equal."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        if var_a.datatype is not var_b.datatype:
            raise RuntimeException("Two values of different types may not be compared.")
        return Value(BOOLEAN, var_a == var_b)

    equ_node = FunctionBinding(equ)
    signatures = [
        Signature([
            Value(ANY, None, "a"),
            Value(ANY, None, "b"),
        ], equ_node)
    ]
    return Function(signatures, "#equ")

EQU_FUNCTION = _equ_operation()
EQU_OPERATOR = Operator(EQU_FUNCTION, "==")

def _and_operation():
    def and_o(context):
        """Returns true if both values are true."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        return Value(BOOLEAN, var_a.data and var_b.data)

    and_node = FunctionBinding(and_o)
    signatures = [
        Signature([
            Value(BOOLEAN, None, "a"),
            Value(BOOLEAN, None, "b"),
        ], and_node),
    ]
    return Function(signatures, "#and")

AND_FUNCTION = _and_operation()
AND_OPERATOR = Operator(AND_FUNCTION, "&&")

def _or_operation():
    def or_o(context):
        """Returns true if one value is true."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        return Value(BOOLEAN, var_a.data or var_b.data)

    or_node = FunctionBinding(or_o)
    signatures = [
        Signature([
            Value(BOOLEAN, None, "a"),
            Value(BOOLEAN, None, "b"),
        ], or_node),
    ]
    return Function(signatures, "#or")

OR_FUNCTION = _or_operation()
OR_OPERATOR = Operator(OR_FUNCTION, "||")

def _xor_operation():
    def xor(context):
        """Returns true if one of the two values is true."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        return Value(BOOLEAN, (var_a.data or var_b.data) and var_a.data != var_b.data)

    xor_node = FunctionBinding(xor)
    signatures = [
        Signature([
            Value(BOOLEAN, None, "a"),
            Value(BOOLEAN, None, "b"),
        ], xor_node),
    ]
    return Function(signatures, "#xor")

XOR_FUNCTION = _xor_operation()
XOR_OPERATOR = Operator(XOR_FUNCTION, "^|")

def _neq_operation():
    def neq(context):
        """Returns true if both values are unequal."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        if var_a.datatype is not var_b.datatype:
            raise RuntimeException("Two values of different types may not be compared.")
        return Value(BOOLEAN, var_a != var_b)
    neq_node = FunctionBinding(neq)
    signatures = [
        Signature([
            Value(ANY, None, "a"),
            Value(ANY, None, "b"),
        ], neq_node),
    ]
    return Function(signatures, "#neq")

NEQ_FUNCTION = _neq_operation()
NEQ_OPERATOR = Operator(NEQ_FUNCTION, "!=")

def _sm_operation():
    def smaller(context):
        """Returns true if one value is smaller than the other."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        return Value(BOOLEAN, var_a.data < var_b.data)
    sm_node = FunctionBinding(smaller)
    signatures = [
        Signature([
            Value(NUMBER, None, "a"),
            Value(NUMBER, None, "b"),
        ], sm_node),
        Signature([
            Value(STRING, None, "a"),
            Value(STRING, None, "b"),
        ], sm_node),
    ]
    return Function(signatures, "#sm")

SM_FUNCTION = _sm_operation()
SM_OPERATOR = Operator(SM_FUNCTION, "<")

def _lg_operation():
    def larger(context):
        """Returns true if a is larger than b."""
        var_a = context.find("id", "a")
        var_b = context.find("id", "b")
        return Value(BOOLEAN, var_a.data < var_b.data)
    lg_node = FunctionBinding(larger)
    signatures = [
        Signature([
            Value(NUMBER, None, "a"),
            Value(NUMBER, None, "b"),
        ], lg_node),
        Signature([
            Value(STRING, None, "a"),
            Value(STRING, None, "b"),
        ], lg_node),
    ]
    return Function(signatures, "#lg")

LG_FUNCTION = _lg_operation()
LG_OPERATOR = Operator(SM_FUNCTION, ">")

EXPORTS = [
    # Datatypes
    INTEGER, FLOAT, BOOLEAN, STRING, LIST, SET, MAP, OBJECT, FUNCTION,
    # Operators
    ADD_OPERATOR, SUB_OPERATOR, MUL_OPERATOR, DIV_OPERATOR, EQU_OPERATOR,
    AND_OPERATOR, OR_OPERATOR, XOR_OPERATOR, NEQ_OPERATOR,
    SM_OPERATOR,
    # Functions
    ADD_FUNCTION, SUB_FUNCTION, MUL_FUNCTION, DIV_FUNCTION, EQU_FUNCTION,
    AND_FUNCTION, OR_FUNCTION, XOR_FUNCTION, NEQ_FUNCTION,
    SM_FUNCTION,
]
