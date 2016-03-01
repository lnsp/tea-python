import teaeval, helper

# parse the tokens to an infix notation
def apply(tokens):
    # TODO: Implement parser
    return teaeval.syntax_tree()

def default_context():
    # create default context with namespace
    context = helper.tree()
    context["namespace"] = default_namespace()
    return context
