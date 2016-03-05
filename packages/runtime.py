#!/usr/bin/python3
"""Command line runtime for Tea."""

import teasplit
import teaparse
import teaeval
import helper

TEA_VERSION = "0.0.3-dev"
TEA_TITLE = "Tea @" + TEA_VERSION
CLI_SYMBOL = "#> "
CLI_SPACE = " " * 3
CLI_RESULT = "<- "
CLI_NULL = 0
CLI_CONTINUE = -1
CLI_EXIT = -2


def interpret(expression, context):
    """Interpret an expression by tokenizing, parsing and evaluating."""
    if expression == "exit":
        context["status"] = CLI_EXIT
    else:
        expr_tokens = teasplit.apply(expression)
        expr_tree = teaparse.apply(expr_tokens)
        expr_result = teaeval.apply(teaparse.demo_syntax_tree(), context)
        context["output"] = CLI_RESULT + str(expr_result["value"])


def main():
    """Run the CLI."""
    # print application title
    print(TEA_TITLE)

    # run REPL
    context = helper.tree()
    while context["status"] != CLI_EXIT:
        context["status"] = CLI_NULL
        context["output"] = None

        interpret(input(CLI_SYMBOL), context)
        while context["status"] == CLI_CONTINUE:
            interpret(input(CLI_SPACE), context)
        print(context["output"])

if __name__ == "__main__":
    main()
