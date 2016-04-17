"""A collection of classes that are part of the standard runtime environment."""

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
        if expected_n > called_n:
            raise Exception("Too less arguments")
        elif expected_n < called_n:
            raise Exception("Too many arguments")
        args = [self.expected[n].cast(called[n]) for n in range(expected_n)]
        return args, self.function

class Function(object):
    """A function with a collection of signatures."""
    def __init__(self, signatures, name=None):
        self.signatures = signatures
        self.name = name
        
    def eval(self, args, context):
        for sgn in self.signatures:
            try:
                values, fnc = match(args)
                return fnc(context, values)
            except: pass
        raise Exception("No matching signature found")

class Operator(object):
    """A operator with a collection of signatures and functions."""
    
    def __init__(self, function, symbol):
        self.function = function
        self.symbol = symbol
        
    def eval(self, args, context):
        return self.function.eval(args, context)
        
class Type(object):
    """A type representing a basic type."""
    
    def __init__(self, name, cast=None):
        self.name = name
        self.cast = cast

def cast_integer(value):
    pass
    
Integer = Type("int", cast_integer)

def cast_float(value):
    pass
    
Float = Type("float", cast_float)

def cast_string(value):
    pass
    
String = Type("string", cast_string)

def cast_boolean(value):
    pass
    
Boolean = Type("bool", cast_boolean)

def cast_null(value):
    pass
    
Null = Type("null", cast_null)

def cast_function(value):
    pass
    
Function = Type("function", cast_function)

def cast_list(value):
    pass
    
List = Type("list", cast_list)

def cast_map(value):
    pass
    
Map = Type("map", cast_map)

def cast_set(value):
    pass
    
Set = Type("set", cast_set)

def cast_object(value):
    pass

Object = Type("object", cast_object)

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
            
    def child(self):
        return Namespace(self)

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

def default_namespace():
    """Initialize a default namespace."""
    return Namespace(None)


def default_context():
    """Initialize a default context."""
    return Context(default_namespace())