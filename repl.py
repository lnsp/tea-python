#!/usr/bin/python3
"""Command line runtime for Tea."""

import runtime.lib
from runtime import lexer, parser, env

TEA_VERSION = "0.0.5-dev"
TEA_TITLE = "Tea @" + TEA_VERSION
CLI_SYMBOL = "#> "
CLI_SPACE = " " * 3
CLI_RESULT = "<- "


def interpret(expression, context):
    """Interpret an expression by tokenizing, parsing and evaluating."""
    if expression == "exit":
        context.flags.append("exit")
        return

    tokens = lexer.run(expression)
    print('Generated tokens:', ', '.join((str(e) for e in tokens)))
    tree = parser.generate(tokens)
    print(tree)
    return tree.eval(context).data


def main():
    """Run the CLI."""
    # print application title
    print(TEA_TITLE)

    # run REPL
    context = env.empty_context()
    context.load(runtime.lib)
    while "done" not in context.flags:
        output = interpret(input(CLI_SYMBOL), context)
        while "continue" in context.flags:
            output = interpret(input(CLI_SPACE), context)
        if "exit" in context.flags:
            return
        print(output)

if __name__ == "__main__":
    main()
