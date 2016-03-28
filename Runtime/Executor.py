"""Eval an abstract syntax tree."""
from Runtime import Utils

BEHAVIOUR_DEFAULT = "default"  # do nothing special
BEHAVIOUR_BREAK = "break"
BEHAVIOUR_CONTINUE = "continue"
BEHAVIOUR_RETURN = "return"  # return, but reset to nothing
BEHAVIOUR_EXIT = "exit"  # exit from program

DATA_INTEGER = "Integer"  # Any integer number
DATA_FLOAT = "Float"  # Any floating point number
DATA_BOOLEAN = "Boolean"  # true / false
DATA_STRING = "String"  # Any string value
DATA_FUNCTION = "Function"
DATA_NONE = "None"  # None / null value
DATA_LIST = "List"
DATA_MAPS = "Map"
DATA_SET = "Set"

_SEQUENCE = "sequence"
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


def operator_add_exec(context, params):
    """Add operator function."""
    return store_value(DATA_INTEGER, 0)


def operator_subtract_exec(context, params):
    """Subtract operator function."""
    return store_value(DATA_INTEGER, 0)

OPERATOR_ADD = {
    "name": "add",
    "precedence": 4,
    "binding": "left",
    "symbol": "+",
    "execution": operator_add_exec,
}
OPERATOR_SUBTRACT = {
    "name": "subtract",
    "precedence": 4,
    "binding": "left",
    "symbol": "-",
    "execution": operator_subtract_exec,
}


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


def run_in_substitution(node, context):
    """Run the node in a subtituted namespace."""
    sub = Namespace(context["local"])
    context["local"] = sub
    result = node.eval(context)
    context["local"] = sub.parent
    return result


def eval_sequence(node, context):
    """Evaluate a sequence of statements."""
    context["behaviour"] = BEHAVIOUR_DEFAULT
    last_value = store_none()

    for item in node.children:
        last_value = item.eval(context)
        if (context["behaviour"] != BEHAVIOUR_DEFAULT):
            break

    return last_value


def eval_branch(node, context):
    """Evaluate a n-component branch (if, else-if ..., else)."""
    for branch in node.children[:-1]:  # all if / else if branches
        if branch.children[0].eval(context)["value"]:  # condition ->
            return run_in_substitution(branch.children[1])
    return run_in_substitution(branch.children[-1])


def eval_loop(node, context):
    """Evaluate either a 2-component or 4-component loop."""
    n = len(node.children)
    # substitute for loop context
    loop_ns = Namespace(context["local"])
    context["local"] = loop_ns
    if n == 2:  # while-loop
        behaviour = context["behaviour"]
        while node.children[0].eval(context)["value"]:
            context["behaviour"] = BEHAVIOUR_DEFAULT
            result = node.children[1].eval(context)
            behaviour = context["behaviour"]
            if behaviour == BEHAVIOUR_RETURN:
                return result
            if behaviour == BEHAVIOUR_BREAK:
                break
        return store_none()
    elif n == 4:
        # execute start statement
        node.children[0].eval(context)
        # execute loop
        while node.children[1].eval(context)["value"]:
            context["behaviour"] = BEHAVIOUR_DEFAULT
            # execute statements
            result = node.children[2].eval(context)
            behaviour = context["behaviour"]
            if behaviour == BEHAVIOUR_RETURN:
                return result
            if behaviour == BEHAVIOUR_BREAK:
                break
            # execute iterator
            node.children[3].eval(context)
        return store_none()


def eval_operator(node, context):
    """Evaluate an operator and return the result.

    node.data['symbol'] is required for execution.
    """
    operator = context.find_operator(node.data["symbol"])
    if operator is not None:
        values = [child.eval(context) for child in node.children]
        return operator["execution"](context, values)
    raise "Operator not found"


def eval_function(node, context):
    """Evaluate a function and return the result.

    node.data['name'] is required for execution.
    """
    function = context.find_identifier(node.data["name"])
    if function is not None:
        values = [child.eval(context) for child in node.children]
        # substitute namespace
        parent_ns = context["local"]
        child_ns = Namespace(context["global"])
        context["local"] = child_ns
        # execute function
        result = function["execution"](context, values)
        context["local"] = parent_ns
        return result
    raise "Function not found"


def eval_identifier(node, context):
    """Evaluate an identifier and return the result.

    node.data['name'] is required for execution.
    """
    identifier = context.find_identifier(node.data["name"])
    if identifier is not None:
        identifier["name"] = node.data["name"]
        return identifier
    return "Identifier not found"


def eval_literal(node, context):
    """Evaluate a literal and return the result.

    node.data['type'] and node.data['value'] is required for execution.
    """
    return node.data


def eval_return(node, context):
    """Evaluate a return statement and return the result.

    Changes the behaviour context to 'RETURN'.
    """
    value = store_none()
    if len(node.children) == 1:
        value = node.children[0].eval(context)

    if context["behaviour"] != BEHAVIOUR_EXIT:
        context["behaviour"] = BEHAVIOUR_RETURN
    return value


def eval_break(node, context):
    """Evaluate a break statement."""
    context["behaviour"] = BEHAVIOUR_BREAK
    return store_none()


def eval_continue(node, context):
    """Evaluate a continue statement."""
    context["continue"] = BEHAVIOUR_CONTINUE
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
    context = Utils.tree()
    context["local"] = context["global"] = default_namespace()
    return context


def syntax_tree():
    """Initialize a default syntax tree."""
    root = Node(TYPES[_SEQUENCE], None)
    return root


def apply(syntax_tree, context):
    """Evaluate the syntax tree."""
    result = syntax_tree.eval(context)
    if context["behaviour"] == BEHAVIOUR_EXIT:
        context["status"] = Utils.CMD_EXIT
    return result
