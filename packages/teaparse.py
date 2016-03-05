"""Parse an tokenized expression into an AST."""
import teaeval


def apply(tokens):
    """Parse the tokens to AST notation."""
    # TODO: Implement parser
    return teaeval.syntax_tree()


def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = teaeval.syntax_tree()

    literal = teaeval.store_value(teaeval.DATA_STRING, "Hallo Welt!")
    literal_node = teaeval.Node(teaeval.TYPES[teaeval._LITERAL], literal)

    tree.add(literal_node)
    return tree
