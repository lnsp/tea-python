"""Parse an tokenized expression into an AST."""
from runtime import ast, std

def apply(tokens):
    """Parse the tokens to AST notation."""
    # TODO: Implement parser
    return ast.syntax_tree()


def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = ast.syntax_tree()

    literal_node = ast.Literal(std.Value(std.String, "Hallo Welt!"))
    tree.add(literal_node)
    
    return tree
