"""Parse an tokenized expression into an AST."""
import codecs
from runtime import ast, lexer, env, lib, flags

class ParseException(Exception):
    def __init__(self, msg):
        super().__init__("ParseException: " + msg)

class MissingOperand(ParseException):
    def __init__(self, op):
        super().__init__("%s is missing operands" % op)

class UnknownOperator(ParseException):
    def __init__(self, op):
        super().__init__("Unknown operator %s" % op)

class BadStatement(ParseException):
    """A statement exception."""
    def __init__(self, msg="Bad statement without semicolon"):
        super().__init__(msg)

class NotImplemented(ParseException):
    """A parse exception."""
    def __init__(self, msg="Functionality not implemented"):
        super().__init__(msg)

class InvalidDeclaration(ParseException):
    def __init__(self, msg):
        super().__init__("Invalid declaration: Unexpected %s" % str(msg))

class InvalidDefinition(ParseException):
    def __init__(self, msg):
        super().__init__("Invalid definition: Unexpected %s" % str(msg))

class InvalidAssignment(ParseException):
    def __init__(self, msg="Invalid assignment"):
        super().__init__(msg)

class InvalidBlock(ParseException):
    def __init__(self, msg="Missing block borders"):
        super().__init__(msg)

class InvalidExpression(ParseException):
    def __init__(self, msg="Invalid expression"):
        super().__init__(msg)

class InvalidCondition(ParseException):
    def __init__(self, msg="Invalid condition"):
        super().__init__(msg)

class InvalidLoop(ParseException):
    def __init__(self, msg):
        super().__init__("Invalid loop: Unexpected %s" % str(msg))

def is_assignment(token):
    return token != None and (token.kind is lexer.OPERATOR) and (token.value in ["=", "+=", "-=", "*=", "/=", "%=", "^="])

def find_matching_block(stream, start):
    level = 1
    max = len(stream)
    for i in range(start, max):
        if stream[i].kind == lexer.LBLOCK:
            level += 1
        elif stream[i].kind == lexer.RBLOCK:
            level -= 1
            if level == 0:
                return i
    return -1

def find_matching_prt(stream, start):
    level = 1
    max = len(stream)
    for i in range(start, max):
        if flags.debug:
            print("scanned", str(stream[i]), ":", level)
        if stream[i].kind == lexer.LPRT:
            level += 1
        elif stream[i].kind == lexer.RPRT:
            level -= 1
            if level == 0:
                return i
    return -1

def get_arg_count(operator, last_token):
    if operator in ["+", "-"] and (last_token == None or last_token.kind not in [lexer.NUMBER, lexer.IDENTIFIER, lexer.STRING, lexer.RPRT]):
        if flags.debug:
            print("unary operator because of", last_token)
        return 1
    elif operator in ["!"]:
        return 1
    if flags.debug:
        print("binary because of", last_token)
    return 2

def is_left_associative(operator, last_token):
    if operator in ["+", "-"] and (last_token == None or last_token.kind not in [lexer.NUMBER, lexer.IDENTIFIER, lexer.STRING, lexer.RPRT]):
        if flags.debug:
            print("right associative because of", last_token)
        return False
    elif operator in ["!", "^"]:
        return False
    if flags.debug:
        print("left associative because of", last_token)
    return True

def get_precedence(operator, last_token):
    if operator in ["+", "-"] and (last_token == None or last_token.kind not in [lexer.NUMBER, lexer.IDENTIFIER, lexer.STRING, lexer.RPRT]):
        return 7
    elif operator in ["!"]:
        return 7
    elif operator in ["^"]:
        return 6
    elif operator in ["*", "/"]:
        return 5
    elif operator in ["+", "-", ":"]:
        return 4
    elif operator in ["%"]:
        return 3
    elif operator in ["<", ">", "<=", ">=", "!=", "=="]:
        return 2
    elif operator in ["&&", "||", "^|"]:
        return 1
    return 0

def generate_expression(stream):
    if flags.debug:
        print("Starting generate expression")
    operand_stack = []
    operator_stack = []
    max = len(stream) - 1

    last_token = None
    token = None

    def pop_off_operator():
        operator = operator_stack.pop()
        arg_count = operator.tag("arg_count")
        if len(operand_stack) < arg_count:
            raise MissingOperand(operator.symbol)
        for j in range(arg_count):
            operator.add_front(operand_stack.pop())
        operand_stack.append(operator)

    for i in range(max + 1):
        last_token = token
        token = stream[i]

        if flags.debug:
            print(">>> Parsing next token:", token)
            print("Operands: ", ', '.join(str(e) for e in operand_stack))
            print("Operators:", ', '.join(str(e) for e in operator_stack))

        if token.kind == lexer.NUMBER:
            value = None
            if '.' in token.value:
                value = env.Value(lib.FLOAT, data=float(token.value))
            else:
                value = env.Value(lib.INTEGER, data=float(token.value))
            operand_stack.append(ast.Literal(value))
        elif token.kind == lexer.STRING:
            stripped = token.value.strip("\"")
            decoded = codecs.decode(stripped, "unicode_escape")
            value = env.Value(lib.STRING, data=decoded)
            operand_stack.append(ast.Literal(value))
        elif token.kind == lexer.SEPARATOR:
            while len(operator_stack) > 0 and operator_stack[-1] != "(":
                pop_off_operator()
        elif token.kind == lexer.IDENTIFIER:
            if i < max and stream[i+1].kind == lexer.LPRT:
                operator_stack.append(ast.Call(token.value))
            else:
                if token.value == "false":
                    operand_stack.append(ast.Literal(env.Value(lib.BOOLEAN, data=False)))
                elif token.value == "true":
                    operand_stack.append(ast.Literal(env.Value(lib.BOOLEAN, data=True)))
                elif token.value == "null":
                    operand_stack.append(ast.Literal(env.Value(lib.NULL)))
                else:
                    operand_stack.append(ast.Identifier(token.value))
        elif token.kind == lexer.OPERATOR:
            new_operator = ast.Operation(token.value)

            prec = get_precedence(token.value, last_token)
            arg_count = get_arg_count(token.value, last_token)
            left_associative = is_left_associative(token.value, last_token)

            new_operator.tag("precedence", prec)
            new_operator.tag("arg_count", arg_count)
            new_operator.tag("left_associative", left_associative)

            if flags.debug:
                print("adding operator", new_operator.symbol, "to", len(operator_stack))

            while len(operator_stack) > 0 and (type(operator_stack[-1]) is ast.Operation):
                other = operator_stack[-1]
                other_prec = operator_stack[-1].tag("precedence")

                if flags.debug:
                    print("comparing precedence of ", new_operator.symbol, prec, "to", other.symbol, other_prec)

                if left_associative:
                    if prec > other_prec:
                        break
                else:
                    if prec >= other_prec:
                        break
                pop_off_operator()

            operator_stack.append(new_operator)
            if flags.debug:
                print("pushed operator on stack")
        elif token.kind == lexer.LPRT:
            operand_stack.append(token.value)
            operator_stack.append(token.value)
        elif token.kind == lexer.RPRT:
            while len(operator_stack) > 0 and operator_stack[-1] != "(":
                pop_off_operator()
            operator_stack.pop()

            if len(operator_stack) > 0 and type(operator_stack[-1]) is ast.Call:
                function = operator_stack.pop()
                while len(operand_stack) > 0 and operand_stack[-1] != "(":
                    function.add_front(operand_stack.pop())
                operand_stack.pop()
                operand_stack.append(function)
            else:
                i = len(operand_stack) - 1
                while i >= 0 and operand_stack[i] != "(":
                    i -= 1
                del operand_stack[i]
        elif token.kind == lexer.STATEMENT:
            while len(operator_stack) > 0:
                pop_off_operator()
            if len(operand_stack) > 1:
                raise InvalidExpression()
            return operand_stack[0], i + 1

    last_token = token

    while len(operator_stack) > 0:
        pop_off_operator()

    if flags.debug:
        print("Operands: ", ', '.join(str(e) for e in operand_stack))
        print("Operators:", ', '.join(str(e) for e in operator_stack))
    if len(operand_stack) > 1:
        raise InvalidExpression()

    if flags.debug:
        print("Parsed expression with length %d" % (max + 1))

    return operand_stack[0], max + 1

def generate_declaration(stream):
    if flags.debug:
        print("Starting generating declaration")

    end = len(stream)
    for j in range(len(stream)):
        if stream[j].kind is lexer.STATEMENT:
            end = j
            break

    if end < 3:
        raise ParseException("Declaration too short")

    if not (stream[0].kind is lexer.IDENTIFIER and stream[0].value == "var"):
        raise InvalidDeclaration(stream[0])

    if stream[1].kind != lexer.IDENTIFIER:
        raise InvalidDeclaration(stream[1])

    declared_names = []
    sequ = ast.Sequence()
    expr_begin = 2

    ignore_type = True

    while expr_begin < end and ((stream[expr_begin].kind is lexer.SEPARATOR) or
                                ((stream[expr_begin].kind is lexer.OPERATOR) and
                                 (stream[expr_begin].value == ":" or
                                  (stream[expr_begin].value == "=" and ignore_type)))):
        if (stream[expr_begin].kind is lexer.OPERATOR) and stream[expr_begin].value == ":":
            ignore_type = False
        if expr_begin > 2 and stream[expr_begin - 2].kind != lexer.SEPARATOR:
            raise InvalidDeclaration(stream[expr_begin - 2])
        if stream[expr_begin - 1].kind is not lexer.IDENTIFIER:
            raise InvalidDeclaration(stream[expr_begin - 1])
        declared_names.append(stream[expr_begin - 1].value)
        expr_begin += 2

    if not ignore_type and stream[expr_begin - 1].kind is not lexer.IDENTIFIER:
        raise InvalidDeclaration(stream[expr_begin - 1])

    datatype = "null"
    if not ignore_type:
        datatype = stream[expr_begin - 1].value
    else:
        expr_begin -= 2

    expr = None
    if expr_begin < end and is_assignment(stream[expr_begin]):
        expr, _ = generate_expression(stream[expr_begin + 1:])

    for name in declared_names:
        decl = ast.Declaration(name, datatype)
        sequ.add(decl)

        if expr is not None:
            assgn = ast.Assignment(name, ignore_type)
            assgn.add(expr)
            expr = assgn

    if expr is not None:
        sequ.add(expr)

    return sequ, end - 1

def generate_assignment(stream):
    if flags.debug:
        print("Starting generating assigment")

    if len(stream) < 3:
        raise InvalidAssignment()

    name_token, equ_token = stream[0], stream[1]
    if name_token.kind != lexer.IDENTIFIER or not is_assignment(equ_token):
        raise InvalidAssignment()

    expr, offset = generate_expression(stream[2:])

    if flags.debug:
        print("Expression has offset %d" % offset)

    if len(equ_token.value) != 1:
        operation = ast.Operation(equ_token.value[0])
        operation.add(ast.Identifier(name_token.value))
        operation.add(expr)
        expr = operation

    assgn = ast.Assignment(name_token.value)
    assgn.add(expr)

    if flags.debug:
        print("Assignment has offset %d" % (1 + offset))

    return assgn, 1 + offset

def generate_function(stream):
    if flags.debug:
        print("Starting generating function definition")

    head_name = stream[0]
    if head_name.kind is not lexer.IDENTIFIER:
        raise InvalidDefinition(head_name)
    fnc_name = head_name.value

    head_start = stream[1]
    if head_start.kind != lexer.LPRT:
        raise InvalidDefinition(head_start)
    head_end_index = find_matching_prt(stream, 2)

    arguments = []
    arg_index = 2
    while arg_index < head_end_index:
        if stream[arg_index].kind is not lexer.IDENTIFIER:
            raise InvalidDefinition(stream[arg_index])
        arg_name = stream[arg_index].value
        if arg_index + 3 >= len(stream):
            raise InvalidDefinition(stream[arg_index+1])
        if (stream[arg_index+1].kind is not lexer.OPERATOR) or stream[arg_index+1].value != ":":
            raise InvalidDefinitiom(stream[arg_index+1])
        if stream[arg_index+2].kind is not lexer.IDENTIFIER:
            raise InvalidDefinitiom(stream[arg_index+2])
        arg_type = stream[arg_index+2].value
        arguments.append(env.Value(arg_type, None, arg_name))
        arg_index += 4

    if flags.debug:
        print("Adding arguments:", ', '.join(str(e) for e in arguments))

    body_start_index = head_end_index + 1
    body_start = stream[body_start_index]
    if body_start.kind is not lexer.LBLOCK:
        raise InvalidDefinition(body_start)

    body, body_len = generate_sequence(stream[body_start_index+1:])
    defi_node = ast.Definition(fnc_name, arguments)
    defi_node.add(body)

    return defi_node, 3 + head_end_index + body_len

def generate_if(stream):
    if flags.debug:
        print("Starting generating if statement")
    cond_start = stream[0]
    if cond_start.kind != lexer.LPRT:
        raise InvalidCondition()

    cond_end_index = find_matching_prt(stream, 1)
    if cond_end_index == 1:
        raise InvalidCondition()

    body_start_index = cond_end_index + 1
    body_start = stream[body_start_index]

    if body_start.kind != lexer.LBLOCK:
        raise InvalidBlock()
    body_end_index = find_matching_block(stream, body_start_index)

    if flags.debug:
        print("If-condition: " + ' '.join(str(e) for e in stream[1:cond_end_index]))
    condition, cond_len = generate_expression(stream[1:cond_end_index])
    body, body_len = generate_sequence(stream[body_start_index+1:])
    body.substitute = True

    branch_node = ast.Branch()
    cond_node = ast.Conditional()
    cond_node.add(condition)
    cond_node.add(body)
    branch_node.add(cond_node)

    after_if = 4 + cond_len + body_len
    if len(stream) <= after_if:
        return branch_node, after_if

    if stream[after_if].kind is not lexer.IDENTIFIER or stream[after_if].value != "else":
        return branch_node, after_if

    if flags.debug:
        print("Going for possible else")

    # check for else_if
    if stream[after_if+1].kind is lexer.IDENTIFIER and stream[after_if+1].value == "if":
        if flags.debug:
            print("Found else-if")
        elif_node, elif_len = generate_if(stream[after_if+2:])
        branch_node.add(elif_node)
        return branch_node, 2 + after_if + elif_len
    else:
        if flags.debug:
            print("Found else starting with " + ' '.join(str(e) for e in stream[after_if+2:]))
        else_body, else_body_len = generate_sequence(stream[after_if+2:])
        else_body.substitute = True
        branch_node.add(else_body)
        return branch_node, 3 + after_if + else_body_len

def generate_for(stream):
    if flags.debug:
        print("Starting generating for statement")
    head_start = stream[0]
    if head_start.kind is not lexer.LPRT:
        raise InvalidCondition()

    head_end_index = find_matching_prt(stream, 1)
    if head_end_index == -1:
        raise InvalidCondition()

    # find first ;
    init_end_index = 1
    for j in range(len(stream)):
        if stream[j].kind is lexer.STATEMENT:
            init_end_index = j
            break

    init_stmt, init_len = generate_sequence(stream[1:init_end_index+1])
    cond_expr, cond_len = generate_expression(stream[1 + init_len:head_end_index])
    iter_stmt, iter_len = generate_sequence(stream[1 + init_len + cond_len:head_end_index])

    body_start_index = head_end_index + 1
    body_start = stream[body_start_index]

    if body_start.kind is not lexer.LBLOCK:
        raise InvalidBlock()

    body_end_index = find_matching_block(stream, body_start_index + 1)
    body, body_len = generate_sequence(stream[body_start_index+1:])

    inner_sequ = ast.Sequence()
    inner_sequ.add(body)
    inner_sequ.add(iter_stmt)

    loop = ast.Loop()
    loop.add(cond_expr)
    loop.add(inner_sequ)

    sequ = ast.Sequence(True)
    sequ.add(init_stmt)
    sequ.add(loop)

    return sequ, 3 + init_len + cond_len + iter_len + body_len


def generate_while(stream):
    if flags.debug:
        print("Starting generating while statement")

    if len(stream) < 6:
        raise InvalidLoop("length %d" % len(stream))

    if not (stream[0].kind is lexer.IDENTIFIER and stream[0].value == "while"):
        raise InvalidLoop(stream[0])

    cond_start = stream[1]
    if cond_start.kind != lexer.LPRT:
        raise InvalidCondition()

    cond_end_index = find_matching_prt(stream, 2)
    if cond_end_index == -1:
        raise InvalidCondition()

    body_start_index = cond_end_index+1
    body_start = stream[body_start_index]

    if body_start.kind != lexer.LBLOCK:
        raise InvalidBlock()
    body_end_index = find_matching_block(stream, body_start_index+1)

    condition, cond_len = generate_expression(stream[2:cond_end_index])
    body, offset = generate_sequence(stream[body_start_index+1:])
    body.substitute = True

    loop = ast.Loop()
    loop.add(condition)
    loop.add(body)

    return loop, 4 + cond_len + offset

def generate_sequence(stream):
    if flags.debug:
        print("Starting generating sequence")
    sequence = ast.Sequence()
    stack = []
    queue = []

    max = len(stream) - 1

    i = 0
    def next():
        if i < max:
            return stream[i+1]
        return None

    while i <= max:
        if flags.debug:
            print("Operating on", i, stream[i])
        token = stream[i]
        if token.kind == lexer.IDENTIFIER:
            if token.value == "func":
                func, offset = generate_function(stream[i+1:])
                sequence.add(func)
                i += offset
            elif token.value == "return":
                expr, offset = generate_expression(stream[i+1:])
                return_node = ast.Return()
                return_node.add(expr)
                sequence.add(return_node)
                i += offset
            elif token.value == "continue":
                sequence.add(ast.Continue())
            elif token.value == "break":
                sequence.add(ast.Break())
            elif token.value == "while":
                while_node, offset = generate_while(stream[i:])
                sequence.add(while_node)
                i += offset
            elif token.value == "if":
                if_node, offset = generate_if(stream[i+1:])
                sequence.add(if_node)
                i += offset
            elif token.value == "for":
                for_node, offset = generate_for(stream[i+1:])
                sequence.add(for_node)
                i += offset
            elif token.value == "import":
                raise NotImplemented()
            elif token.value == "var":
                decl, offset = generate_declaration(stream[i:])
                sequence.add(decl)
                i += offset
            else:
                if i < max and is_assignment(next()):
                    assgn, offset = generate_assignment(stream[i:])
                    sequence.add(assgn)
                    i += offset
                else:
                    expr, offset = generate_expression(stream[i:])
                    sequence.add(expr)
                    i += offset
        elif token.kind == lexer.NUMBER or token.kind == lexer.STRING or token.kind == lexer.OPERATOR:
            expr, offset = generate_expression(stream[i:])
            sequence.add(expr)
            i += offset
        elif token.kind == lexer.LBLOCK:
            sequ, offset = generate_sequence(stream[i+1:])
            i += offset + 1
            sequence.add(sequ)
        elif token.kind == lexer.RBLOCK:
            return sequence, i
        if flags.debug:
            print("Tree view:", sequence)
        i += 1
    return sequence, i

def optimize_ast(root):
    for i in range(len(root.children)):
        node = root.children[i]
        if type(node) is ast.Operation and node.symbol == ":":
            values = node.children
            datatype = values.pop().identity
            if flags.debug:
                print("Replacing cast of %s" % datatype)
            node = ast.Cast(datatype)
            node.children = values
            root.children[i] = node
        else:
            optimize_ast(node)

def generate(tokens):
    """Parse the tokens to AST notation."""
    # clean off whitespaces
    clean = [t for t in tokens if t.kind != lexer.WHITESPACE]
    if flags.debug:
        print("Optimized tokens:", '; '.join(str(e) for e in clean))
    sequ, _ = generate_sequence(clean)
    if flags.debug:
        print("Optimizing AST ...")
    optimize_ast(sequ)
    if flags.debug:
        print("Final AST:", str(sequ))
    return sequ

def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = ast.syntax_tree()
    return tree
