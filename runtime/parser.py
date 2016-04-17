"""Parse an tokenized expression into an AST."""
from runtime import ast, std

def generate(tokens):
    """Parse the tokens to AST notation."""
    # TODO: Implement parser
    return demo_syntax_tree()


def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = ast.syntax_tree()

    literal_node = ast.Literal(std.Value(std.Boolean, True))
    cast_node = ast.Cast(std.Integer.name)
    cast_node.add(literal_node)
    tree.add(cast_node)
    
    return tree
