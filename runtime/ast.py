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
    name = "base_node"

    def __init__(self):
        self.children = []
        self.tags = {}

    def add(self, node):
        """Adds a leaf to this node."""
        self.children.append(node)

    def tag(self, tag, value=None):
        if value is None:
            return self.tags[tag]
        self.tags[tag] = value

    def add_front(self, node):
        self.children = [node] + self.children

    def describe(self):
        return type(self).name

    def get_str_rep(self, depth):
        rep = "%s (%d)" % (self.describe(), len(self.children))
        for i in self.children:
            rep += "\n" + (" " * depth)
            rep += i.get_str_rep(depth+2)
        return rep + ">"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.children == other.children

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

    def __init__(self, substitute=False):
        super().__init__()
        self.substitute = substitute

    def __eq__(self, other):
        return super().__eq__(other)

    def eval(self, context):
        """Evaluate a sequence of statements."""
        parent = None
        try:
            if self.substitute:
                parent = context.substitute()
        except:
            pass

        context.behaviour = DEFAULT_BEHAVIOUR
        value = env.Value(env.NULL)

        for item in self.children:
            value = item.eval(context)
            if context.behaviour is not DEFAULT_BEHAVIOUR:
                break

        if parent is not None:
            context.namespace = parent

        return value


class Branch(Node):
    """A branch node."""
    name = "branch"

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        return super().__eq__(other)

    def eval(self, context):
        """Evaluate a n-component branch (if, else-if ..., else)."""
        if len(self.children) > 1:
            for conditional in self.children[:-1]:  # all if / else if branches
                result = conditional.eval(context)
                if result != False:
                    return result
            return run_in_substitution(self.children[-1], context)
        else:
            result = self.children[0].eval(context)
            if result != False:
                return result



class Conditional(Node):
    """A conditional node."""
    name = "conditional"

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        return super().__eq__(other)

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

    def __eq__(self, other):
        return super().__eq__(other)

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

    def describe(self):
        return "operation %s" % self.symbol

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def __eq__(self, other):
        return super().__eq__(other) and self.symbol == other.symbol

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

    def describe(self):
        return "call %s" % self.identity

    def __init__(self, identity):
        super().__init__()
        self.identity = identity

    def __eq__(self, other):
        return super().__eq__(other) and self.identity == other.identity

    def eval(self, context):
        """Evaluate a function call and return the result."""
        function = context.find("id", self.identity)
        if function is not None:
            args = [child.eval(context) for child in self.children]
            result = function.eval(args, context)
            context.behaviour = DEFAULT_BEHAVIOUR
            return result
        raise Exception("Function not found")


class Identifier(Node):
    """A node representing an identifier."""
    name = "identifier"

    def describe(self):
        return "identifier %s" % self.identity

    def __init__(self, identity):
        super().__init__()
        self.identity = identity

    def __eq__(self, other):
        return super().__eq__(other) and self.identity == other.identity

    def eval(self, context):
        """Evaluate an identifier and return the result."""
        identifier = context.find("id", self.identity)
        if identifier is not None:
            return identifier
        raise Exception("Identifier not found")


class Literal(Node):
    """A node with a explicit value."""
    name = "literal"

    def describe(self):
        return "literal %s" % str(self.value.data)

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __eq__(self, other):
        return super().__eq__(other) and self.value == other.value

    def eval(self, context):
        """Evaluate a literal and return the result."""
        return self.value


class Cast(Node):
    """A type cast node."""
    name = "cast"

    def describe(self):
        return "cast %s" % self.target

    def __init__(self, target):
        super().__init__()
        self.target = target

    def __eq__(self, other):
        return super().__eq__(other) and self.target == other.target

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

    def __eq__(self, other):
        return super().__eq__(other)

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

    def __eq__(self, other):
        return super().__eq__(other)

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

    def __eq__(self, other):
        return super().__eq__(other)

    @classmethod
    def eval(cls, context):
        """Evaluate a continue statement."""
        context.behaviour = CONTINUE_BEHAVIOUR
        return env.Value(env.NULL)

class Definition(Node):
    """A definition node."""
    name = "definition"

    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name and self.args == other.args

    def describe(self):
        return "definition %s: (%s)" % (self.name, ', '.join(str(arg) for arg in self.args))

    def eval(self, context):
        # check if function with the same name already exists
        try:
            context.find("id", self.name)
            raise env.RuntimeException("%s already defined in the same context." % self.name)
        except env.NamespaceException:
            # convert types from text to type
            for arg in self.args:
                arg.datatype = context.find("ty", arg.datatype)
            signature = env.Signature(self.args, self.children[0])

            fnc = env.Function([signature], self.name, context.namespace)
            context.store(fnc)

            return fnc

class Declaration(Node):
    """A declaration node."""
    name = "declaration"

    def describe(self):
        return "declaration %s: %s" % (self.name, self.datatype)

    def __init__(self, name, datatype):
        super().__init__()
        self.name = name
        self.datatype = datatype

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name and self.datatype == other.datatype

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

    def describe(self):
        return "assignment %s" % self.name

    def __init__(self, name, ignore_type=False):
        super().__init__()
        self.name = name
        self.ignore_type = ignore_type

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name and self.ignore_type == other.ignore_type

    def eval(self, context):
        """Looks for a variable in the namespace and assigns a value to it."""
        # Search for variable in namespace
        variable = context.find("id", self.name)
        value = self.children[0].eval(context)

        if self.ignore_type:
            variable.datatype = value.datatype
            variable.data = value.data
        else:
            if variable.datatype != value.datatype:
                raise env.AssignmentException(value.datatype, variable.datatype)
            variable.data = value.data

        return value

def syntax_tree():
    """Initialize a default syntax tree."""
    return Sequence()
