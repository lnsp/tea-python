#!/usr/bin/python3
"""Command line runtime for Tea."""

from Runtime import Tokenizer
from Runtime import Parser
from Runtime import Executor
from Runtime import Utils

TEA_VERSION = "0.0.3-dev"
TEA_TITLE = "Tea @" + TEA_VERSION
CLI_SYMBOL = "#> "
CLI_SPACE = " " * 3
CLI_RESULT = "<- "


def interpret(expression, context):
    """Interpret an expression by tokenizing, parsing and evaluating."""
    if expression == "exit":
        context["status"] = Utils.CMD_EXIT
    else:
        expr_tokens = Tokenizer.apply(expression)
        expr_tree = Parser.apply(expr_tokens)
        expr_result = Executor.apply(Parser.demo_syntax_tree(), context)
        context["output"] = CLI_RESULT + str(expr_result["value"])


def main():
    """Run the CLI."""
    # print application title
    print(TEA_TITLE)

    # run REPL
    context = Utils.tree()
    while context["status"] != Utils.CMD_EXIT:
        context["status"] = Utils.CMD_NULL
        context["output"] = None

        interpret(input(CLI_SYMBOL), context)
        while context["status"] == Utils.CMD_CONTINUE:
            interpret(input(CLI_SPACE), context)
        print(context["output"])

if __name__ == "__main__":
    main()
