"""Eval an abstract syntax tree."""
import runtime

BEHAVIOUR_DEFAULT = "default"  # do nothing special
BEHAVIOUR_RETURN = "return"  # return, but reset to nothing
BEHAVIOUR_EXIT = "exit"  # exit from program

DATA_INTEGER = "Integer"  # Any integer number
DATA_FLOAT = "Float"  # Any floating point number
DATA_BOOLEAN = "Boolean"  # true / false
DATA_STRING = "String"  # Any string value
DATA_REFERENCE = "Reference"  # Name reference
DATA_FUNCTION = "Function"
DATA_NONE = "None"  # None / null value
# TODO: Add lists, maps and sets

SEQUENCE = "sequence"
BRANCH = "branch"
RETURN = "return"
FUNCTION = "function"
OPERATOR = "operator"
IDENTIFIER = "identifier"
LITERAL = "literal"


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
        self.items = {}
        # operator map
        self.operators = {}

    def find_identifier(self, identifier):
        """Search for an identifier in this and higher order namespaces."""
        # search in local namespace
        for key in self.items:
            if key == identifier:
                return self.items[key]
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find_identifier(identifier)
        # return if nothing available
        return None

    def find_operator(self, operator):
        """Search for an operator in this and higher order namespaces."""
        # search in local namespace
        for key in self.operators:
            if key == operator:
                return self.operators[key]
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find_operator(operator)
        # return if nothing available
        return None

    def put_item(self, item):
        """Store identifier in namespace."""
        # add item to namespace
        self.items[item["name"]] = item

    def put_operator(self, operator):
        """Store operator in namespace."""
        # add operator to namespace
        self.operator[operator["name"]] = operator


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
            return branch.children[1].eval(context)  # execution
    return branch.children[-1].eval(context)  # else branch


def eval_operator(node, context):
    """Evaluate an operator and return the result.

    node.data['symbol'] is required for execution.
    """
    operator = context.find_operator(node.data["symbol"])
    if operator is not None:
        values = [child.eval(context) for child in node.children]
        return operator["execution"](values)
    raise "Operator not found"


def eval_function(node, context):
    """Evaluate a function and return the result.

    node.data['name'] is required for execution.
    """
    function = context.find_identifier(node.data["name"])
    if function is not None:
        values = [child.eval(context) for child in node.children]
        return function["execution"](values)
    raise "Function not found"


def eval_identifier(node, context):
    """Evaluate an identifier and return the result.

    node.data['name'] is required for execution.
    """
    identifier = context.find_identifier(node.data["name"])
    if identifier is not None:
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
    context["behaviour"] = BEHAVIOUR_RETURN
    return value

TYPES = {
    SEQUENCE: {
        "name": SEQUENCE,
        "execution": eval_sequence,
    },
    BRANCH: {
        "name": BRANCH,
        "execution": eval_branch,
    },
    OPERATOR: {
        "name": OPERATOR,
        "execution": eval_operator,
    },
    IDENTIFIER: {
        "name": IDENTIFIER,
        "execution": eval_identifier,
    },
    LITERAL: {
        "name": LITERAL,
        "execution": eval_literal,
    },
    RETURN: {
        "name": RETURN,
        "execution": None,
    },
    FUNCTION: {
        "name": FUNCTION,
        "execution": eval_function,
    },
}


def default_namespace():
    """Initialize a default namespace."""
    namespace = Namespace(None)
    # add items and operators
    return namespace


def syntax_tree():
    """Initialize a default syntax tree."""
    root = Node(TYPES[SEQUENCE], None)
    return root


def apply(syntax_tree, context):
    """Evaluate the syntax tree."""
    syntax_tree.eval(context)
    if context["behaviour"] == BEHAVIOUR_EXIT:
        context["status"] = runtime.CLI_EXIT
