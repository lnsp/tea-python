"""Eval an abstract syntax tree."""
from runtime import std

class Behaviour:
    Default = "default"
    Return = "return"
    Break = "break"
    Continue = "continue"

def run_in_substitution(node, context):
    """Run the node in a subtituted namespace."""
    parent = context.substitute()
    result = node.eval(context)
    context.ns = parent
    return result
    
class Node:
    """A generic node in the abstract syntax tree."""
    def __init__(self):
        self.children = []
        
    def add(self, node):
        self.children.append(node)
        
    def __str__(self):
        return "<Node (%s)>" % (type(self).name)

class Sequence(Node):
    """A sequence node."""
    name = "sequence"
    
    def __init__(self):
        super().__init__()
        
    def eval(self, context):
        """Evaluate a sequence of statements."""
        context.behaviour = Behaviour.Default
        value = std.Value(std.Null)

        for item in self.children:
            value = item.eval(context)
            if (context.behaviour != Behaviour.Default):
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
    name = "conditional"
    
    def __init__(self):
        super().__init__()
    
    def eval(self, context):
        """Evaluate a conditional (if [0] then [1])."""
        correct = self.children[0].eval(context)
        if correct.datatype is not std.Boolean:
            raise Exception("Bad conditional")
        else:
            if correct.data:
                return run_in_substitution(self.children[1], context)
            else: return False

class Loop(Node):
    name = "loop"
    
    def __init__(self):
        super().__init__()
    
    def eval(self, context):
        """Evaluate a 2-component loop. for [0] { ... }"""
        cond = Conditional.eval(self, context)
        while cond != False:
            bhv = context.behaviour
            if bhv == Behaviour.Return: return cond
            else:
                context.behaviour = Behaviour.Default
                if bhv == Behaviour.Break: return std.Value(std.Null)
            cond = Conditional.eval(self, context)
        return store_null()

class Operator(Node):
    name = "operator"
    
    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def eval(self, context):
        """Evaluate an operator and return the result."""
        operator = context.find("op", symbol)
        if operator is not None:
            args = [child.eval(context) for child in self.children]
            return operator.eval(args, context)
        raise Exception("Operator not found")

class Call(Node):
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
    name = "literal"
    
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def eval(self, context):
        """Evaluate a literal and return the result."""
        return self.value
        
class Cast(Node):
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
    name = "return"
    
    def __init__(self):
        super().__init__()
    
    def eval(self, context):
        """Evaluate a return statement and return the result.

        Changes the behaviour context to 'RETURN'.
        """
        value = Sequence.eval(self, context)
        context.behaviour = Behaviour.Return
        return value

class Break(Node):
    name = "break"
    
    def __init__(self):
        super().__init__()

    def eval(self, context):
        """Evaluate a break statement."""
        context.behaviour = Behaviour.Break
        return std.Value(std.Null)

class Continue(Node):
    name = "continue"
    
    def __init__(self):
        super().__init__()
        
    def eval(self, context):
        """Evaluate a continue statement."""
        context.behaviour = Behaviour.Continue
        return std.Value(std.Null)

def syntax_tree():
    """Initialize a default syntax tree."""
    return Sequence()
