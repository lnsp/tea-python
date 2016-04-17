"""Eval an abstract syntax tree."""
from runtime import utils

BEHAVIOUR_DEFAULT = "default"  # do nothing special
BEHAVIOUR_BREAK = "break"
BEHAVIOUR_CONTINUE = "continue"
BEHAVIOUR_RETURN = "return"  # return, but reset to nothing

_SEQUENCE = "sequence"
_CONDITIONAL = "conditional"
_BRANCH = "branch"
_LOOP = "loop"
_RETURN = "return"
_BREAK = "break"
_CONTINUE = "continue"
_FUNCTION = "function"
_OPERATOR = "operator"
_IDENTIFIER = "identifier"
_LITERAL = "literal"

class Value:
    """A variable storing a value with a specific type."""
    def __init__(self, datatype, data):
        self.datatype = datatype
        self.data = data
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.datatype == other.datatype
            and self.data == other.data)
    def __ne__(self, other):
        return not self.__eq__(other) 

class Signature:
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

class Type:
    """A type representing a basic type."""
    
    def __init__(self, name, cast=None):
        self.name = name
        self.cast = cast

TYPES = {
    "int": Type("int"),
    "float": Type("float"),
    "bool": Type("bool"),
    "string": Type("string"),
    "func": Type("function"),
    "null": Type("null"),
    "list": Type("list"),
    "map": Type("map"),
    "set": Type("set"),
}

def store_null():
    return Value(TYPES["null"], None)

class Function:
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

class Operator:
    """A operator with a collection of signatures and functions."""
    
    def __init__(self, function, symbol):
        self.function = function
        self.symbol = symbol
        
    def eval(self, args, context):
        return self.function.eval(args, context)

class Identifier:
    """A identifier with a name and a value."""
    
    def __init__(self, value, name=None):
        self.datatype = value.datatype
        self.data = value.data
        self.name = name
    def __eq__(self, other):
        return ((isinstance(other, Identifier) or isinstance(other, Value))
            and self.datatype == other.datatype
            and self.data == other.data)
    def __ne__(self, other):
        return not self.__eq__(other) 

class Node:
    """A node in the abstract syntax tree."""

    def __init__(self, node_type, node_data):
        """Initialize a new node with a type and data."""
        self.children = []
        self.type = node_type
        self.data = node_data

    def eval(self, context):
        """Eval the node."""
        return self.type["execution"](self, context)

    def add(self, node):
        """Add a child to the node."""
        self.children.append(node)


class Namespace:
    """A variable and operator namespace."""

    def __init__(self, parent):
        """Initialize a new namespace."""
        # parent namespace
        self.parent = parent
        # item map
        self.identifiers = {}
        # operator map
        self.operators = {}
        # type map
        self.types = {}
        # search spaces
        self.spaces = {
            "type": self.types,
            "operator": self.operators,
            "identifier": self.identifiers,
        }
        
    def find(self, space, key):
        """Search for an element in this and higher order namespaces."""
        # search in local namespace
        try:
            return self.spaces[space][key]
        except: pass
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find(space, key)
        # return if nothing available
        return None

    def find_identifier(self, ident):
        """Search for an identifier in this and higher order namespaces."""
        return self.find("identifier", ident)

    def find_operator(self, op):
        """Search for an operator in this and higher order namespaces."""
        return self.find("operator", op)
    
    def find_type(self, t):
        """Search for a type in this and higher order namespaces."""
        return self.find("type", t)
        
    def store(self, space, name, item):
        """Stores a item in the specified search space."""
        self.spaces[space][name] = item;

    def put_identifier(self, item):
        """Store identifier in namespace."""
        self.store("identifier", item.name, item)

    def put_operator(self, operator):
        """Store operator in namespace."""
        self.store("operator", operator.symbol, operator)
        
    def put_type(self, t):
        """Store type in namespace."""
        self.store("type", t.name, t)

class Context:
    """A context for temporary storage."""
    
    def __init__(self, namespace):
        self.ns = namespace
        self.globalns = namespace
        self.behaviour = BEHAVIOUR_DEFAULT
        self.flags = []
    
    def find_identifier(self, name):
        return self.ns.find_identifier(name)
        
    def find_operator(self, symbol):
        return self.ns.find_operator(symbol)

def run_in_substitution(node, context):
    """Run the node in a subtituted namespace."""
    sub = Namespace(context.ns)
    context.ns = sub
    result = node.eval(context)
    context.ns = sub.parent
    return result


def eval_sequence(node, context):
    """Evaluate a sequence of statements."""
    context.behaviour = BEHAVIOUR_DEFAULT
    last_value = store_null()

    for item in node.children:
        last_value = item.eval(context)
        if (context.behaviour != BEHAVIOUR_DEFAULT):
            break

    return last_value


def eval_branch(node, context):
    """Evaluate a n-component branch (if, else-if ..., else)."""
    for conditional in node.children[:-1]:  # all if / else if branches
        result = conditional.eval(context)
        if result != False:
            return result
    return run_in_substitution(node.children[-1], context)

def eval_conditional(node, context):
    """Evaluate a conditional (if [0] then [1])."""
    correct = node.children[0].eval(context)
    if correct.datatype is not TYPES["bool"]:
        raise Exception("Bad conditional")
    else:
        if correct.data:
            return run_in_substitution(node.children[1], context)
        else:
            return False
    
def eval_loop(node, context):
    """Evaluate a 2-component loop. for [0] { ... }"""
    cond = eval_conditional(node, context)
    while cond != False:
        bhv = context.behaviour
        if bhv == BEHAVIOUR_RETURN: return cond
        else:
            context.behaviour = BEHAVIOUR_DEFAULT
            if bhv == BEHAVIOUR_BREAK: return store_null()
        cond = eval_conditional(node, context)
    return store_null()

def eval_operator(node, context):
    """Evaluate an operator and return the result.

    node.data = symbol is required for execution.
    """
    operator = context.find_operator(node.data)
    if operator is not None:
        args = [child.eval(context) for child in node.children]
        return operator.eval(args, context)
    raise Exception("Operator not found")


def eval_function(node, context):
    """Evaluate a function and return the result.

    node.data is required for execution.
    """
    function = context.find_identifier(node.data)
    if function is not None:
        args = [child.eval(context) for child in node.children]
        return function.eval(args, context)
    raise Exception("Function not found")


def eval_identifier(node, context):
    """Evaluate an identifier and return the result.

    node.data = name is required for execution.
    """
    identifier = context.find_identifier(node.data)
    if identifier is not None:
        return identifier
    raise Exception("Identifier not found")


def eval_literal(node, context):
    """Evaluate a literal and return the result.

    node.data (Value) is required for execution.
    """
    return node.data


def eval_return(node, context):
    """Evaluate a return statement and return the result.

    Changes the behaviour context to 'RETURN'.
    """
    value = eval_sequence(node, context)
    context.behaviour = BEHAVIOUR_RETURN
    return value


def eval_break(node, context):
    """Evaluate a break statement."""
    context.behaviour = BEHAVIOUR_BREAK
    return store_null()


def eval_continue(node, context):
    """Evaluate a continue statement."""
    context.behaviour = BEHAVIOUR_CONTINUE
    return store_null()

NODES = {
    _SEQUENCE: {
        "name": _SEQUENCE,
        "execution": eval_sequence,
    },
    _BRANCH: {
        "name": _BRANCH,
        "execution": eval_branch,
    },
    _CONDITIONAL: {
        "name": _CONDITIONAL,
        "execution": eval_conditional,
    },
    _LOOP: {
        "name": _LOOP,
        "execution": eval_loop,
    },
    _OPERATOR: {
        "name": _OPERATOR,
        "execution": eval_operator,
    },
    _IDENTIFIER: {
        "name": _IDENTIFIER,
        "execution": eval_identifier,
    },
    _LITERAL: {
        "name": _LITERAL,
        "execution": eval_literal,
    },
    _RETURN: {
        "name": _RETURN,
        "execution": eval_return,
    },
    _BREAK: {
        "name": _BREAK,
        "execution": eval_break,
    },
    _CONTINUE: {
        "name": _CONTINUE,
        "execution": eval_continue,
    },
    _FUNCTION: {
        "name": _FUNCTION,
        "execution": eval_function,
    },
}


def default_namespace():
    """Initialize a default namespace."""
    namespace = Namespace(None)
    return namespace


def default_context():
    """Initialize a default context."""
    return Context(default_namespace())


def syntax_tree():
    """Initialize a default syntax tree."""
    root = Node(NODES[_SEQUENCE], None)
    return root


def apply(syntax_tree, context):
    """Evaluate the syntax tree."""
    return syntax_tree.eval(context)
