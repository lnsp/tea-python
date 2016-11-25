"""A collection of classes that are part of the standard runtime environment."""

class RuntimeException(Exception):
    """A runtime exception."""

    def __init__(self, message):
        super().__init__("RuntimeException: " + message)


class NamespaceException(RuntimeException):
    """A namespace exception."""
    def __init__(self, msg="The item does not exist in the search space."):
        super().__init__(msg)

class Namespace:
    """A variable and operator namespace."""

    def __init__(self, parent):
        """Initialize a new namespace."""
        # parent namespace
        self.parent = parent
        self.search_spaces = {
            "id": {},  # identifier search space
            "op": {},  # operator search space
            "ty": {},  # type search space
        }

    def find(self, space, key):
        """Search for an element in this and higher order namespaces."""
        # search in local namespace
        if key in self.search_spaces[space]:
            return self.search_spaces[space][key]
        # find in parent namespaces
        if self.parent is not None:
            return self.parent.find(space, key)
        # return if nothing available
        raise NamespaceException()

    def store(self, item):
        """Stores a item in the specified search space."""
        itemtype = type(item)
        if itemtype in (Value, Function):
            self.search_spaces["id"][item.name] = item
        elif itemtype is Operator:
            self.search_spaces["op"][item.symbol] = item
        elif itemtype is Datatype:
            self.search_spaces["ty"][item.name] = item
        else:
            raise NamespaceException("The item cannot be stored in namespace")

    def store_all(self, items):
        """Stores a list or tuple of items."""
        for element in items:
            self.store(element)

    def child(self):
        """Returns a new namespace with this namespace as its parent."""
        return Namespace(self)

    def __str__(self):
        return "<Namespace>"


class Context:
    """A context for temporary storage."""

    def __init__(self, namespace):
        self.namespace = namespace
        self.global_namespace = namespace
        self.behaviour = "default"
        self.flags = []

    def store(self, item):
        """Forwards to Namespace.store"""
        return self.namespace.store(item)

    def load(self, library):
        """Loads a library into the current namespace."""
        self.namespace.store_all(library.EXPORTS)

    def find(self, space, key):
        """Forwards to Namespace.find"""
        return self.namespace.find(space, key)

    def substitute(self):
        """Substitutes the current namespace by a child."""
        org = self.namespace
        self.namespace = self.namespace.child()
        return org

    def __str__(self):
        return "<Context>"


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


class ArgumentException(Exception):
    """ArgumentException is raised when the number of arguments do not match the signature."""

    def __init__(self, expected, got):
        message = "Too " + ("many" if expected < got else "less") + "arguments"
        super().__init__("%s: expected %d, got %d" % (message, expected, got))


class ArgumentCastException(Exception):
    """ArgumentCastError is raised when the type of arguments do not match the signature."""

    def __init__(self, expected, got):
        super().__init__("No match found for %s to %s" % (expected, got))


class Signature(object):
    """A signature matching a function call."""

    def __init__(self, expected, function):
        self.expected = expected
        self.function = function

    def match(self, args):
        """Checks if the arguments match the function signature.
        If yes, it returns (Arguments, Function)
        If no, it raises an error."""
        number_of_expected, number_of_args = len(self.expected), len(args)

        # Too many arguments
        if number_of_expected < number_of_args:
            raise ArgumentException(number_of_expected, number_of_args)

        # Fill the argument list with trash
        matched_args = []

        # Iterate until max arguments reached
        for index in range(number_of_expected):
            expected = self.expected[index]
            expected_type = expected.datatype
            # Still arguments to go
            if number_of_args > index:
                arg = args[index]
                arg_type = arg.datatype
                if not arg_type.kind_of(expected_type):
                    raise ArgumentCastException(
                        expected_type, arg_type)
                var = arg_type.cast(arg)
            # Not enough arguments given, looking for default values
            elif expected.data != None:
                var = expected_type.cast(expected)
            # Not enough arguments given, no default values
            else:
                raise ArgumentException(number_of_expected, number_of_args)
            var.name = expected.name
            matched_args.append(var)
        return matched_args, self.function

    def __str__(self):
        return "<Signature (%s)>" % ",".join(self.expected.name)


class FunctionException(Exception):
    """Raised when no matching signature was found or a similar error occured."""

    def __init__(self, function, message="No signature found"):
        super().__init__("%s in %s" % (message, function))


class Function(object):
    """A function with a collection of signatures."""

    def __init__(self, signatures, name=None, source_ns=None):
        self.signatures = signatures
        self.name = name
        self.source_ns = source_ns

    def eval(self, args, context):
        """Searches for a matching signature and evaluates the function node."""
        for sgn in self.signatures:
            try:
                values, fnc = sgn.match(args)
                original, context.namespace = context.namespace, Namespace(self.source_ns)
                # place args in namespace
                context.namespace.store_all(values)
                result = fnc.eval(context)
                context.namespace = original
                return result
            except (ArgumentException, ArgumentCastException):
                pass
        raise FunctionException(self)

    def __str__(self):
        return "<Function *(%s)>" % self.name


class FunctionBinding(object):
    """A binding object for Python functions."""

    def __init__(self, fnc):
        self.fnc = fnc

    def eval(self, context):
        """Evaluates the binding node."""
        return self.fnc(context)

class OperatorException(RuntimeException):
    """A operator exception."""

    def __init__(self, op):
        super().__init__("Operator %s is not applicable." % op)

class Operator(object):
    """A operator with a collection of signatures and functions."""

    def __init__(self, base_function, symbol):
        self.functions = [base_function]
        self.symbol = symbol

    def add_function(self, fnc):
        self.functions.append(fnc)

    def eval(self, args, context):
        """Evaluates the operator."""
        for fnc in self.functions:
            try:
                return fnc.eval(args, context)
            except FunctionException:
                pass
        raise OperatorException(self.symbol)

    def __str__(self):
        return "<Operator (%s)>" % self.symbol


class Datatype(object):
    """A type representing a basic type."""

    def __init__(self, name, cast=None, parent=None):
        self.name = name
        self.cast = cast
        self.parent = parent

    def kind_of(self, itemtype):
        """Checks if the type is related to the specified type."""
        if self is itemtype:
            return True
        if self.parent is not None:
            return self.parent.kind_of(itemtype)
        return False

    def __str__(self):
        return "<T %s>" % self.name


class CastException(RuntimeException):
    """A CastError is raised when a value can not be casted to another type."""

    def __init__(self, value, datatype):
        super().__init__("%s not parseable to %s" % (value, datatype))


def empty_context():
    """empty_context generates an empty context with a clean namespace."""
    return Context(Namespace(None))

# Types that belong to the REnv, not to the RLib
ANY = Datatype("*any", None)
NULL = Datatype("null", lambda x: Value(NULL), ANY)
