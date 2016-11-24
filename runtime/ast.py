"""Eval an abstract syntax tree."""
from runtime import env

DEFAULT_BEHAVIOUR = "default"
RETURN_BEHAVIOUR = "return"
BREAK_BEHAVIOUR = "break"
CONTINUE_BEHAVIOUR = "continue"

def run_in_substitution(node, context):
    """Run the node in a subtituted namespace."""
    parent = context.substitute()
    result = node.eval(context)
    context.namespace = parent
    return result


class Node:
    """A generic node in the abstract syntax tree."""

    def __init__(self):
        self.children = []

    def add(self, node):
        """Adds a leaf to this node."""
        self.children.append(node)

    def add_front(self, node):
        self.children = [node] + self.children

    def get_str_rep(self, depth):
        rep = "<Node (%s)" % type(self).name
        for i in self.children:
            rep += "\n" + (" " * depth)
            rep += i.get_str_rep(depth+2)
        return rep + ">"

    def __str__(self):
        return self.get_str_rep(2)

    def tree_to_string(self, root=0):
        """Generates a tree-string from this node."""
        path_ws = " " * root
        my_path = path_ws + "|\n" + path_ws + "+-" + \
            ("+" if len(self.children) > 0 else "-") + "-"
        my_node = my_path + str(self) + "\n"
        return my_node + ''.join([n.tree_to_string(root + 2) for n in self.children])


class Sequence(Node):
    """A sequence node."""
    name = "sequence"

    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Evaluate a sequence of statements."""
        context.behaviour = DEFAULT_BEHAVIOUR
        value = env.Value(env.NULL)

        for item in self.children:
            value = item.eval(context)
            if context.behaviour is not DEFAULT_BEHAVIOUR:
                break

        return value


class Branch(Node):
    """A branch node."""
    name = "branch"

    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Evaluate a n-component branch (if, else-if ..., else)."""
        for conditional in self.children[:-1]:  # all if / else if branches
            result = conditional.eval(context)
            if result != False:
                return result
        return run_in_substitution(self.children[-1], context)


class Conditional(Node):
    """A conditional node."""
    name = "conditional"

    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Evaluate a conditional (if [0] then [1])."""
        correct = self.children[0].eval(context)
        if correct.data not in (True, False):
            raise Exception("Bad conditional")
        else:
            if correct.data:
                return run_in_substitution(self.children[1], context)
            else:
                return False


class Loop(Node):
    """A loop node."""
    name = "loop"

    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Evaluate a 2-component loop. for [0] { ... }"""
        cond = Conditional.eval(self, context)
        while cond != False:
            bhv = context.behaviour
            if bhv is RETURN_BEHAVIOUR:
                return cond
            else:
                context.behaviour = DEFAULT_BEHAVIOUR
                if bhv is BREAK_BEHAVIOUR:
                    return env.Value(env.NULL)
            cond = Conditional.eval(self, context)
        return env.Value(env.NULL)


class Operation(Node):
    """A operation node calling an operator."""
    name = "operation"

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def eval(self, context):
        """Evaluate an operator and return the result."""
        operator = context.find("op", self.symbol)
        if operator is not None:
            args = [child.eval(context) for child in self.children]
            return operator.eval(args, context)
        raise Exception("Operator not found")


class Call(Node):
    """A function call node."""
    name = "call"

    def __init__(self, identity):
        super().__init__()
        self.identity = identity

    def eval(self, context):
        """Evaluate a function call and return the result."""
        function = context.find("id", self.identity)
        if function is not None:
            args = [child.eval(context) for child in self.children]
            return function.eval(args, context)
        raise Exception("Function not found")


class Identifier(Node):
    """A node representing an identifier."""
    name = "identifier"

    def __init__(self, identity):
        super().__init__()
        self.identity = identity

    def eval(self, context):
        """Evaluate an identifier and return the result."""
        identifier = context.find("id", self.identity)
        if identifier is not None:
            return identifier
        raise Exception("Identifier not found")


class Literal(Node):
    """A node with a explicit value."""
    name = "literal"

    def __init__(self, value):
        super().__init__()
        self.value = value

    def eval(self, context):
        """Evaluate a literal and return the result."""
        return self.value


class Cast(Node):
    """A type cast node."""
    name = "cast"

    def __init__(self, target):
        super().__init__()
        self.target = target

    def eval(self, context):
        """Evaluate a type cast and return the result."""
        target_type = context.find("ty", self.target)
        if target_type is not None:
            value = self.children[0].eval(context)
            return target_type.cast(value)
        raise Exception("Type not found")


class Return(Node):
    """A return node."""
    name = "return"

    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Evaluate a return statement and return the result.

        Changes the behaviour context to 'RETURN'.
        """
        value = Sequence.eval(self, context)
        context.behaviour = RETURN_BEHAVIOUR
        return value

class Break(Node):
    """A break node."""
    name = "break"

    def __init__(self):
        super().__init__()

    @classmethod
    def eval(cls, context):
        """Evaluate a break statement."""
        context.behaviour = BREAK_BEHAVIOUR
        return env.Value(env.NULL)

class Continue(Node):
    """A continue node."""
    name = "continue"

    def __init__(self):
        super().__init__()

    @classmethod
    def eval(cls, context):
        """Evaluate a continue statement."""
        context.behaviour = CONTINUE_BEHAVIOUR
        return env.Value(env.NULL)

class Declaration(Node):
    """A declaration node."""
    name = "declaration"

    def __init__(self, name, datatype):
        super().__init__()
        self.name = name
        self.datatype = datatype

    def eval(self, context):
        """Creates an entry in the local namespace."""
        # Search in local namespace
        if self.name in context.namespace.search_spaces["id"]:
            raise env.RuntimeException("The name %s is already in use" % self.name)
        # Search for type
        datatype = context.find("ty", self.datatype)
        casted_value = datatype.cast(env.Value(env.NULL))
        casted_value.name = self.name
        context.store(casted_value)
        return casted_value

class Assignment(Node):
    """A assignment node."""
    name = "assignment"

    def __init__(self, name):
        super().__init__()
        self.name = name

    def eval(self, context):
        """Looks for a variable in the namespace and assigns a value to it."""
        # Search for variable in namespace
        variable = context.find("id", self.name)
        value = self.children[0].eval(context)
        variable.data = variable.datatype.cast(value).data
        return value

def syntax_tree():
    """Initialize a default syntax tree."""
    return Sequence()
