#!/usr/bin/python3
"""Command line runtime for Tea."""

from runtime import tokenizer, parser, ast, std

TEA_VERSION = "0.0.3-dev"
TEA_TITLE = "Tea @" + TEA_VERSION
CLI_SYMBOL = "#> "
CLI_SPACE = " " * 3
CLI_RESULT = "<- "


def interpret(expression, context):
    """Interpret an expression by tokenizing, parsing and evaluating."""
    if expression == "exit":
        context.flags.append("exit")
        return
    
    tokens = tokenizer.apply(expression)
    tree = parser.generate(tokens)
    return tree.tree_to_string()


def main():
    """Run the CLI."""
    # print application title
    print(TEA_TITLE)

    # run REPL
    context = std.default_context()
    while "done" not in context.flags:
        output = interpret(input(CLI_SYMBOL), context)
        while "continue" in context.flags:
            output = interpret(input(CLI_SPACE), context)
        if "exit" in context.flags: return
        print(output)

if __name__ == "__main__":
    main()
