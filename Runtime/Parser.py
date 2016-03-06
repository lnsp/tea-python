"""Parse an tokenized expression into an AST."""
import Executor


def apply(tokens):
    """Parse the tokens to AST notation."""
    # TODO: Implement parser
    return Executor.syntax_tree()


def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = Executor.syntax_tree()

    literal = Executor.store_value(Executor.DATA_STRING, "Hallo Welt!")
    literal_node = Executor.Node(Executor.TYPES[Executor._LITERAL], literal)

    tree.add(literal_node)
    return tree
