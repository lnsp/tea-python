"""A collection of classes that are part of the standard runtime environment."""

class Namespace:
    """A variable and operator namespace."""

    def __init__(self, parent):
        """Initialize a new namespace."""
        # parent namespace
        self.parent = parent
        self.search_spaces = {
            "id": {}, # identifier search space
            "op": {}, # operator search space
            "ty": {}, # type search space
        }
        
    def find(self, space, key):
        """Search for an element in this and higher order namespaces."""
        # search in local namespace
        try:
            return self.search_spaces[space][key]
        except: pass
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find(space, key)
        # return if nothing available
        raise Exception("The item does not exist in this and upper namespaces")
        
    def store(self, item):
        """Stores a item in the specified search space."""
        t = type(item)
        if t is Value or t is Function:
            self.search_spaces["id"][item.name] = item
        elif t is Operator:
            self.search_spaces["op"][item.symbol] = item
        elif t is Type:
            self.search_spaces["ty"][item.name] = item
        else:
            raise Exception("Item cannot be stored in namespace")
            
    def store_all(self, items):
        """Stores a list or tuple of items."""
        for e in items:
            self.store(e)
            
    def child(self):
        return Namespace(self)
        
    def __str__(self):
        return "<Namespace>"

class Context:
    """A context for temporary storage."""
    
    def __init__(self, namespace):
        self.ns = namespace
        self.globalns = namespace
        self.behaviour = "default"
        self.flags = []
        
    def store(self, item):
        """Forwards to Namespace.store"""
        return self.ns.store(item)
        
    def find(self, space, key):
        """Forwards to Namespace.find"""
        return self.ns.find(space, key)
        
    def substitute(self):
        """Substitutes the current namespace by a child."""
        org = self.ns
        self.ns = self.ns.child()
        return org
        
    def __str__(self):
        return "<Context>"

def default_namespace():
    """Initialize a default namespace."""
    ns = Namespace(None)
    ns.store_all(default_types)
    return ns


def default_context():
    """Initialize a default context."""
    return Context(default_namespace())

class Value(object):
    """A variable storing a value with a specific type."""
    
    def __init__(self, datatype, data=None, name=None):
        self.datatype = datatype
        self.data = data
        self.name = name
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.datatype == other.datatype
            and self.data == other.data)
    def __ne__(self, other):
        return not self.__eq__(other) 
    def __str__(self):
        return "<Value ? %s *(%s)>" % (self.datatype, self.name)

class ArgumentError(Exception):
    def __init__(self, expected, got):
        message = "Too " + ("many" if expected < got else "less") + "arguments"
        super().__init__("%s: expected %d, got %d" % (message, expected, got))
        
class ArgumentCastError(Exception):
    def __init__(self, expected, got):
        super().__init__("No match found for %s to %s" % (expected, got))

class Signature(object):
    """A signature matching a function call."""
    def __init__(self, expected, function):
        self.expected = expected
        self.function = function
        
    def match(self, called):
        """Checks if the arguments match the function signature.
        If yes, it returns (Arguments, Function)
        If no, it raises an error.
        """
        expected_n, called_n = len(self.expected), len(called)
        
        # Too many arguments
        if expected_n < called_n:
            raise ArgumentError(expected_n, called_n)
        
        # Fill the argument list with trash
        args = []
        
        # Iterate until max arguments reached
        for n in range(expected_n):
            expected_var = self.expected[n]
            expected_type = expected_var.datatype
            # Still arguments to go
            if called_n > n:
                got_var = called[n]
                got_type = got_var.datatype
                if not got_type.kind_of(expected_type):
                    raise ArgumentCastError(expected_var.datatype, got_var.datatype)
                var = got_type.cast(got_var)
            # Not enough arguments given, looking for default values
            elif expected_var.data != None:
                var = expected_type.cast(expected_var)
            # Not enough arguments given, no default values
            else:
                raise ArgumentError(expected_n, called_n)
            var.name = expected_var.name
            args.append(var)
        return args, self.function
    def __str__(self):
        return "<Signature (%s)>" % ",".join(self.expected.name)

class FunctionError(Exception):
    def __init__(self, function, message="No signature found"):
        super().__init__("%s in %s" % (message, function))

class Function(object):
    """A function with a collection of signatures."""
    def __init__(self, signatures, name=None, source_ns=None):
        self.signatures = signatures
        self.name = name
        self.source_ns = source_ns
        
    def eval(self, args, context):
        for sgn in self.signatures:
            try:
                values, fnc = sgn.match(args)
                orig, context.ns = context.ns, Namespace(self.source_ns)
                # place args in namespace
                context.ns.store_all(values)
                result = fnc.eval(context)
                context.ns = orig
                return result
            except (ArgumentError, ArgumentCastError): pass
        raise FunctionError(self)
        
    def __str__(self):
        return "<Function *(%s)>" % self.name

class Operator(object):
    """A operator with a collection of signatures and functions."""
    
    def __init__(self, function, symbol):
        self.function = function
        self.symbol = symbol
        
    def eval(self, args, context):
        return self.function.eval(args, context)
        
    def __str__(self):
        return "<Operator (%s)>" % self.symbol
        
class Type(object):
    """A type representing a basic type."""
    
    def __init__(self, name, cast=None, parent=None):
        self.name = name
        self.cast = cast
        self.parent = parent
        
    def kind_of(self, t):
        if self is t: return True
        if self.parent is not None:
            return self.parent.kind_of(t)
        return False
        
    def __str__(self):
        return "<T %s>" % self.name

# STDLIB BEGIN HERE

class CastError(Exception):
    def __init__(self, value, datatype):
        super().__init__("%s not parseable to %s" % (value, datatype))

Any = Type("*any", None)
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

def cast_null(value):
    if type(value) is Value:
        return Value(Null)
    raise CastError(value, Null)
    
Null = Type("null", cast_null, Any)

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

default_types = [
    Integer, Float, Boolean, String, List, Set, Map, Object, Null, Func
]

def add_operator():
    def add(context):
        """Add two number values."""
        a = context.find("id", "a")
        t = a.datatype
        b = t.cast(context.find("id", "b"))
        return Value(t, a.data + b.data)
        
    signatures = [
        Signature([
            Value(Number, None, "a"),
            Value(Number, None, "b"),
        ], add),
        Signature([
            Value(String, None, "a"),
            Value(Any, None, "b"),
        ], add),
    ]
    
    return Operator(Function(signatures), "+")
    
AddOperator = add_operator()
    
default_operators = [
    AddOperator,
]