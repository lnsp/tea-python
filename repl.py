#!/usr/bin/python3
"""Command line runtime for Tea."""

import runtime.lib
from runtime import lexer, parser, env, flags

TEA_VERSION = "0.0.5-dev"
TEA_TITLE = "Tea @" + TEA_VERSION
CLI_SYMBOL = ">> "
CLI_SPACE = " " * 3
CLI_RESULT = "<- "
CLI_ERROR = "!! "

def interpret(expression, context):
    """Interpret an expression by tokenizing, parsing and evaluating."""
    if expression == "!exit":
        context.flags.append("exit")
        return
    if expression == "!debug":
        flags.debug = not flags.debug
        return "Debug mode %s" % ("on" if flags.debug else "off")
    if expression.startswith("!exec"):
        # load file
        filename = expression.split(' ')[1]
        print("Executing %s" % filename)
        with open(filename, "r") as f:
            expression = ' '.join(line for line in f)

    try:
        tokens = lexer.run(expression)
        tree = parser.generate(tokens)
        return CLI_RESULT + tree.eval(context).format()
    except (env.FunctionException, env.OperatorException, env.RuntimeException, parser.ParseException) as e:
        return CLI_ERROR + str(e)


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
