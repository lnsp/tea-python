"""The standard runtime library."""
from runtime.env import (Datatype, Value, Function, Operator,
                         Signature, FunctionBinding, CastError, ANY, NULL,
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
    raise CastError(value, INTEGER)

INTEGER = Datatype("int", cast_integer, NUMBER)


def cast_float(value):
    """Casts a value to a FLOAT."""
    if isinstance(value, Value):
        if value.datatype in (FLOAT, INTEGER):
            return Value(FLOAT, float(value.data))
        if value.datatype is NULL:
            return Value(FLOAT, 0.0)
    raise CastError(value, FLOAT)

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
    raise CastError(value, STRING)

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
    raise CastError(value, BOOLEAN)

BOOLEAN = Datatype("bool", cast_boolean, ANY)


def cast_function(value):
    """Casts a value to a FUNCTION."""
    if isinstance(value, Value):
        if value.datatype is FUNCTION:
            return Value(FUNCTION, value.data)
        if value.datatype is NULL:
            return Value(FUNCTION, None)
    raise CastError(value, FUNCTION)

FUNCTION = Datatype("func", cast_function, ANY)


def cast_list(value):
    """Casts a value to a LIST."""
    if isinstance(value, Value):
        if value.datatype in (LIST, STRING):
            return Value(LIST, list(value.data))
        if value.datatype is NULL:
            return Value(LIST, [])
    raise CastError(value, LIST)

LIST = Datatype("LIST", cast_list, ANY)


def cast_map(value):
    """Casts a value to a MAP."""
    if isinstance(value, Value):
        if value.datatype is MAP:
            return Value(MAP, dict(value.data))
        if value.datatype is NULL:
            return Value(MAP, dict())
    raise CastError(value, MAP)

MAP = Datatype("map", cast_map, ANY)


def cast_set(value):
    """Casts a value to a SET."""
    if isinstance(value, Value):
        if value.datatype in (SET, LIST):
            return Value(SET, set(value.data))
        if value.datatype is NULL:
            return Value(SET, set())
    raise CastError(value, SET)

SET = Datatype("set", cast_set, ANY)


def cast_object(value):
    """Casts a value to an OBJECT."""
    if isinstance(value, Value):
        return Value(OBJECT, value.data)
    raise CastError(value, OBJECT)

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

EXPORTS = [
    # Datatypes
    INTEGER, FLOAT, BOOLEAN, STRING, LIST, SET, MAP, OBJECT, FUNCTION,
    # Operators
    ADD_OPERATOR, SUB_OPERATOR, MUL_OPERATOR, DIV_OPERATOR,
    # Functions
    ADD_FUNCTION, SUB_FUNCTION, MUL_FUNCTION, DIV_FUNCTION,
]
