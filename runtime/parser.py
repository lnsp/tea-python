"""Parse an tokenized expression into an AST."""
from runtime import ast, lexer, env, lib

class UnknownOperator(Exception):
    def __init__(self, op):
        super().__init__("Unknown operator %s" % op)

class BadStatement(Exception):
    """A statement exception."""
    def __init__(self, msg="Bad statement without semicolon"):
        super().__init__(msg)

class NotImplemented(Exception):
    """A parse exception."""
    def __init__(self, msg="Functionality not implemented"):
        super().__init__(msg)

class InvalidDeclaration(Exception):
    def __init__(self, msg="Invalid declaration"):
        super().__init__(msg)

class InvalidAssignment(Exception):
    def __init__(self, msg="Invalid assignment"):
        super().__init__(msg)

def get_arg_count(operator):
    count = {"+": 2, "-": 2, "*": 2, "/": 2}
    if operator not in count:
        raise UnknownOperator(operator)
    return count[operator]

def is_left_associative(operator):
    assoc = {"+": True, "-": True, "*": True, "/": True}
    if operator not in assoc:
        raise UnknownOperator(operator)
    return assoc[operator]

def get_precedence(operator):
    prec = {"+": 4, "-": 4, "*": 5, "/": 5}
    if operator not in prec:
        raise UnknownOperator(operator)
    return prec[operator]

def generate_expression(stream):
    operand_stack = []
    operator_stack = []
    max = len(stream) - 1
    for i in range(max + 1):
        token = stream[i]
        print("Parsing", token)
        if token.kind == lexer.NUMBER:
            value = env.Value(lib.FLOAT, data=float(token.value))
            operand_stack.append(ast.Literal(value))
        elif token.kind == lexer.STRING:
            value = env.Value(lib.STRING, data=token.value)
            operand_stack.append(ast.Literal(value))
        elif token.kind == lexer.IDENTIFIER:
            if i < max and stream[i+1].kind == lexer.LPRT:
                operator_stack.append(ast.Call(token.value))
            else:
                if token.value == "false":
                    operand_stack.append(ast.Literal(env.Value(lib.BOOLEAN, data=False)))
                elif token.value == "true":
                    operand_stack.append(ast.Literal(env.Value(lib.BOOLEAN, data=True)))
                else:
                    operand_stack.append(ast.Identifier(token.value))
        elif token.kind == lexer.OPERATOR:
            prec = get_precedence(token.value)
            while len(operator_stack) > 0 and operator_stack[-1] is ast.Operation:
                symbol = operator_stack[-1].symbol
                other_prec = get_precedence(symbol)
                if is_left_associative(symbol):
                    if other_prec < prec:
                        break
                else:
                    if other_prec <= prec:
                        break
                operator = operator_stack.pop()
                arg_count = get_arg_count(symbol)
                for j in range(arg_count):
                    operator.add_front(operand_stack.pop())
                operand_stack.append(operator)
            operator_stack.append(ast.Operation(token.value))
        elif token.kind == lexer.LPRT:
            operand_stack.append(token.value)
            operator_stack.append(token.value)
        elif token.kind == lexer.RPRT:
            while len(operator_stack) > 0 and operator_stack[-1] != "(":
                operator = operator_stack.pop()
                arg_count = get_arg_count(operator.symbol)
                for j in range(arg_count):
                    operator.add_front(operand_stack.pop())
                operand_stack.append(operator)
            operator_stack.pop()

            if len(operator_stack) > 0 and type(operator_stack[-1]) is ast.Call:
                function = operator_stack.pop()
                while len(operand_stack) > 0 and operand_stack[-1] != "(":
                    function.add(operand_stack.pop())
                operand_stack.pop()
                operand_stack.append(function)
            else:
                i = len(operand_stack) - 1
                while i >= 0 and operand_stack[i] != "(":
                    i -= 1
                del operand_stack[i]

        print("Operands: ", ', '.join(str(e) for e in operand_stack))
        print("Operators:", ', '.join(str(e) for e in operator_stack))

    while len(operator_stack) > 0:
        operator = operator_stack.pop()
        arg_count = get_arg_count(operator.symbol)
        for j in range(arg_count):
            operator.add_front(operand_stack.pop())
        operand_stack.append(operator)

    return operand_stack[0]

def generate_declaration(stream):
    if len(stream) < 3 or stream[0].kind != lexer.IDENTIFIER:
        raise InvalidDeclaration()

    name_token, decl_token, type_token = stream[0], stream[1], stream[2]

    if decl_token.kind != lexer.OPERATOR or decl_token.value != ":" or type_token.kind != lexer.IDENTIFIER:
            raise InvalidDeclaration()
    decl = ast.Declaration(name_token.value, type_token.value)

    if len(stream) < 5:
        return decl

    if stream[3].kind != lexer.ASSIGNMENT:
        raise InvalidAssignment()

    sequ = ast.Sequence()
    sequ.add(decl)

    expr = generate_expression(stream[4:])
    assgn = ast.Assignment(name_token.value)
    assgn.add(expr)
    sequ.add(assgn)

    return sequ

def generate_assignment(stream):
    if len(stream) < 3:
        raise InvalidAssignment()

    name_token, equ_token = stream[0], stream[1]
    if name_token.kind != lexer.IDENTIFIER or equ_token.kind != lexer.ASSIGNMENT:
        raise InvalidAssignment()

    expr = generate_expression(stream[2:])
    assgn = ast.Assignment(name_token.value)
    assgn.add(expr)

    return assgn

def next_statement_end(stream, start):
    end_index = start
    for j in range(start+1, len(stream)):
        if stream[j].kind == lexer.STATEMENT:
            end_index = j
            break
    return end_index


def generate_sequence(stream):
    sequence = ast.Sequence()
    stack = []
    queue = []

    max = len(stream) - 1

    i = 0
    while i <= max:
        token = stream[i]
        if token.kind == lexer.IDENTIFIER:
            if token.value == "func":
                raise NotImplemented()
            elif token.value == "return":
                end_index = next_statement_end(stream, i)
                if end_index == i:
                    raise BadStatement()
                return_node = ast.Return()
                return_node.add(generate_expression(stream[i+1:end_index]))
                sequence.add(return_node)
                i = end_index
            elif token.value == "continue":
                sequence.add(ast.Continue())
            elif token.value == "break":
                sequence.add(ast.Break())
            elif token.value == "while":
                raise NotImplemented()
            elif token.value == "for":
                raise NotImplemented()
            elif token.value == "import":
                raise NotImplemented()
            elif token.value == "var":
                end_index = next_statement_end(stream, i)
                if end_index == i:
                    raise BadStatement()
                sequence.add(generate_declaration(stream[i+1:end_index]))
                i = end_index
            else:
                if i < max and stream[i+1].kind == lexer.ASSIGNMENT:
                    end_index = next_statement_end(stream, i)
                    if end_index == i:
                        raise BadStatement()
                    sequence.add(generate_assignment(stream[i:end_index]))
                    i = end_index
                else:
                    end_index = next_statement_end(stream, i)
                    if end_index == i:
                        raise BadStatement()
                    sequence.add(generate_expression(stream[i:end_index]))
                    i = end_index
        elif token.kind == lexer.NUMBER or token.kind == lexer.STRING:
            end_index = next_statement_end(stream, i)
            if end_index == i:
                raise BadStatement()
            sequence.add(generate_expression(stream[i:end_index]))
            i = end_index
        elif token.kind == lexer.LBLOCK:
            raise NotImplemented()
        elif token.kind == lexer.RBLOCK:
            return sequence
        i += 1
    return sequence


def generate(tokens):
    """Parse the tokens to AST notation."""
    # clean off whitespaces
    clean = [t for t in tokens if t.kind != lexer.WHITESPACE]
    return generate_sequence(clean)

def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = ast.syntax_tree()
    return tree
