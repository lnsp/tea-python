"""Eval an abstract syntax tree."""
from Runtime import Utils

BEHAVIOUR_DEFAULT = "default"  # do nothing special
BEHAVIOUR_BREAK = "break"
BEHAVIOUR_CONTINUE = "continue"
BEHAVIOUR_RETURN = "return"  # return, but reset to nothing

DATA_INTEGER = "Integer"  # Any integer number
DATA_FLOAT = "Float"  # Any floating point number
DATA_BOOLEAN = "Boolean"  # true / false
DATA_STRING = "String"  # Any string value
DATA_FUNCTION = "Function"
DATA_NONE = "None"  # None / null value
DATA_LIST = "List"
DATA_MAP = "Map"
DATA_SET = "Set"

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


def store_value(t, v):
    """Create a storage with a stored type and value."""
    return {"type": t, "value": v}


def store_none():
    """Create a storage with no value."""
    return store_value(DATA_NONE, None)



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

    def find_identifier(self, ident):
        """Search for an identifier in this and higher order namespaces."""
        # search in local namespace
        for key in self.identifiers:
            if key == ident:
                return self.identifiers[key]
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find_identifier(ident)
        # return if nothing available
        return None

    def find_operator(self, op):
        """Search for an operator in this and higher order namespaces."""
        # search in local namespace
        for key in self.operators:
            if key == op:
                return self.operators[key]
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find_operator(op)
        # return if nothing available
        return None

    def put_identifier(self, name, item):
        """Store identifier in namespace."""
        # add item to namespace
        self.identifiers[name] = item

    def put_operator(self, symbol, operator):
        """Store operator in namespace."""
        # add operator to namespace
        self.operators[symbol] = operator

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
    last_value = store_none()

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
    if correct["type"] is not DATA_BOOLEAN:
        raise Exception("Bad conditional")
    else:
        if correct["value"]:
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
            if bhv == BEHAVIOUR_BREAK: return store_none()
        cond = eval_conditional(node, context)
    return store_none()

def eval_operator(node, context):
    """Evaluate an operator and return the result.

    node.data['symbol'] is required for execution.
    """
    operator = context.find_operator(node.data)
    if operator is not None:
        args = [child.eval(context) for child in node.children]
        return operator["execution"](context, args)
    raise Exception("Operator not found")


def eval_function(node, context):
    """Evaluate a function and return the result.

    node.data['name'] is required for execution.
    """
    function = context.find_identifier(node.data)
    if function is not None:
        args = [child.eval(context) for child in node.children]
        result = function["execution"](context, args)
        return result
    raise Exception("Function not found")


def eval_identifier(node, context):
    """Evaluate an identifier and return the result.

    node.data['name'] is required for execution.
    """
    identifier = context.find_identifier(node.data)
    if identifier is not None:
        identifier["name"] = node.data
        return identifier
    raise Exception("Identifier not found")


def eval_literal(node, context):
    """Evaluate a literal and return the result.

    node.data['type'] and node.data['value'] is required for execution.
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
    return store_none()


def eval_continue(node, context):
    """Evaluate a continue statement."""
    context.behaviour = BEHAVIOUR_CONTINUE
    return store_none()

TYPES = {
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
    root = Node(TYPES[_SEQUENCE], None)
    return root


def apply(syntax_tree, context):
    """Evaluate the syntax tree."""
    return syntax_tree.eval(context)
