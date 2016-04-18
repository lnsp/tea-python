from runtime.env import *

Number = Type("*number", None, Any)


def cast_integer(value):
    if type(value) is Value:
        if value.datatype in (Float, Integer):
            return Value(Integer, int(value.data))
        if value.datatype is Boolean:
            return Value(Integer, 1 if value.data else 0)
        if value.datatype is Null:
            return Value(Integer, 0)
    raise CastError(value, Integer)

Integer = Type("int", cast_integer, Number)


def cast_float(value):
    if type(value) is Value:
        if value.datatype in (Float, Integer):
            return Value(Float, float(value.data))
        if value.datatype is Null:
            return Value(Float, 0.0)
    raise CastError(value, Float)

Float = Type("float", cast_float, Number)


def cast_string(value):
    if type(value) is Value:
        if value.datatype in (Integer, Float, String):
            return Value(String, str(value.data))
        if value.datatype is Boolean:
            return Value(String, "true" if value.data else "false")
        if value.datatype is Null:
            return Value(String, "null")
    raise CastError(value, String)

String = Type("string", cast_string, Any)


def cast_boolean(value):
    if type(value) is Value:
        if value.datatype is Integer:
            return Value(Boolean, True if value.data > 0 else False)
        if value.datatype is Boolean:
            return Value(Boolean, bool(value.data))
        if value.datatype is Null:
            return Value(Null, False)
    raise CastError(value, Boolean)

Boolean = Type("bool", cast_boolean, Any)


def cast_func(value):
    if type(value) is Value:
        if value.datatype is Func:
            return Value(Func, value.data)
    raise CastError(value, Func)

Func = Type("func", cast_func, Any)


def cast_list(value):
    if type(value) is Value:
        if value.datatype in (List, String):
            return Value(List, list(value.data))
    raise CastError(value, List)

List = Type("list", cast_list, Any)


def cast_map(value):
    if type(value) is Value:
        if value.datatype in Map:
            return Value(Map, map(value.data))
    raise CastError(value, Map)

Map = Type("map", cast_map, Any)


def cast_set(value):
    if type(value) is Value:
        if value.datatype in (Set, List):
            return Value(Set, set(value.data))
    raise CastError(value, Set)

Set = Type("set", cast_set, Any)


def cast_object(value):
    if type(value) is Value:
        return Value(Object, value.data)
    raise CastError(value, Object)

Object = Type("object", cast_object, Any)


def add_function():
    def add(context):
        """Add two number values."""
        a = context.find("id", "a")
        t = a.datatype
        b = t.cast(context.find("id", "b"))
        return Value(t, a.data + b.data)

    add_node = FunctionBinding(add)

    signatures = [
        Signature([
            Value(Number, None, "a"),
            Value(Number, None, "b"),
        ], add_node),
        Signature([
            Value(String, None, "a"),
            Value(Any, None, "b"),
        ], add_node),
    ]
    return Function(signatures, "#add")

AddFunction = add_function()
AddOperator = Operator(AddFunction, "+")


def sub_function():
    def sub(context):
        """Subtract two number values."""
        a = context.find("id", "a")
        t = a.datatype
        b = t.cast(context.find("id", "b"))
        return Value(t, a.data - b.data)

    sub_node = FunctionBinding(sub)
    signatures = [
        Signature([
            Value(Number, None, "a"),
            Value(Number, None, "b"),
        ], sub_node),
    ]
    return Function(signatures, "#sub")

SubFunction = sub_function()
SubOperator = Operator(SubFunction, "-")


def mul_function():
    def mul(context):
        """Multiply two numbers."""
        a = context.find("id", "a")
        t = a.datatype
        b = t.cast(context.find("id", "b"))
        return Value(t, a.data * b.data)

    mul_node = FunctionBinding(mul)
    signatures = [
        Signature([
            Value(Number, None, "a"),
            Value(Number, None, "b"),
        ], mul_node),
    ]
    return Function(signatures, "#mul")

MulFunction = mul_function()
MulOperator = Operator(MulFunction, "*")

default_types = [
    Integer, Float, Boolean, String, List, Set, Map, Object, Func
]
default_operators = [
    AddOperator, SubOperator, MulOperator,
]
default_functions = [
    AddFunction, SubFunction, MulFunction,
]
