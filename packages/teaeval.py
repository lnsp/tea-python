import runtime

BEHAVIOUR_DEFAULT = "default" # do nothing special
BEHAVIOUR_RETURN = "return" # return, but reset to nothing
BEHAVIOUR_EXIT = "exit" # exit from program

DATA_INTEGER = "Integer" # Any integer number
DATA_FLOAT = "Float" # Any floating point number
DATA_BOOLEAN = "Boolean" # true / false
DATA_STRING = "String" # Any string value
DATA_REFERENCE = "Reference"  # Name reference
DATA_NONE = "None" # None / null value
# TODO: Add lists, maps and sets

SEQUENCE = "sequence"
BRANCH = "branch"
RETURN = "return"
FUNCTION = "function"
OPERATOR = "operator"
IDENTIFIER = "identifier"
LITERAL = "literal"

# creates a storage structure
def store_value(data_type, data):
    return { "type": data_type, "data": data }

# creates a None structure
def store_none():
    return store_value(DATA_NONE, None)

# operator operations
def operator_add_exec(params):
    return store_value(DATA_INTEGER, 0)

def operator_subtract_exec(params):
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
    def __init__(self, node_type, node_data):
        self.children = []
        self.type = node_type
        self.data = node_data

    def eval(self, context):
        return self.type["execution"](self, context)

    def add(self, node):
        self.children.append(node)

class Namespace:
    def __init__(self, parent):
        # parent namespace
        self.parent = parent
        # item map
        self.items = {}
        # operator map
        self.operators = {}

    def find_identifier(self, identifier):
        # search in local namespace
        for key in self.items:
            if key == identifier:
                return self.items[key]
        # find in parent namespaces
        if self.parent != None:
            return self.parent.find_identifier(identifier)
        # return if nothing available
        return None

    def find_operator(self, operator):
        # search in local namespace
        for key in self.operators:
            if key == operator:
                return self.operators[key]
        # find in parent namespaces
        if self.parent != None:
            return self.parent.find_operator(operator)
        # return if nothing available
        return None

    def put_item(self, item):
        # add item to namespace
        self.items[item["name"]] = item

    def put_operator(self, operator):
        # add operator to namespace
        self.operator[item["name"]] = operator

# evaluates a sequence of expressions, loops or branches
def eval_sequence(node, context):
    context["behaviour"] = BEHAVIOUR_DEFAULT
    last_value = store_none()

    for item in node.children:
        last_value = item.eval(context)
        if (context["behaviour"] != BEHAVIOUR_DEFAULT):
            break

    return last_value

# evaluates a n-component branch (if, else-if, else)
def eval_branch(node, context):
    for branch in node.children[:-1]: # all if / else if branches
        if branch.children[0].eval(context): # condition ->
            return branch.children[1].eval(context) # execution
    return branch.children[-1].eval(context) # else branch

# evaluates an operator and returns the resulting value
def eval_operator(node, context):
    pass

# evaluates an identifier and returns the resulting value
def eval_identifier(node, context):
    pass

# evaluates an literal and returns the resulting value
def eval_literal(node, context):
    pass

# evaluates a return statement
def eval_return(node, context):
    pass

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
    }
}
# create default namespace
def default_namespace():
    namespace = Namespace(None)
    # add items and operators
    return namespace

def syntax_tree():
    root = Node(TYPES[SEQUENCE], None)
    return root

# eval the ast notation
def apply(syntax_tree, context):
    syntax_tree.eval(context)
    if context["behaviour"] == BEHAVIOUR_EXIT:
        context["status"] = runtime.CLI_EXIT
