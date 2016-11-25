"""Parse an tokenized expression into an AST."""
from runtime import ast, lexer, env, lib

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
    def __init__(self, msg="Invalid declaration"):
        super().__init__(msg)

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

def is_assignment(token):
    return token != None and token.kind is lexer.OPERATOR and token.value == "="

def find_statement(stream, start):
    end_index = start
    for j in range(start+1, len(stream)):
        if stream[j].kind == lexer.STATEMENT:
            end_index = j
            break
    return end_index

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
        #print("scanned", str(stream[i]), ":", level)
        if stream[i].kind == lexer.LPRT:
            level += 1
        elif stream[i].kind == lexer.RPRT:
            level -= 1
            if level == 0:
                return i
    return -1

def get_arg_count(operator, last_token):
    if operator in ["+", "-"] and (last_token == None or last_token.kind not in [lexer.NUMBER, lexer.IDENTIFIER, lexer.NUMBER]):
        print("unary operator because of", last_token)
        return 1
    elif operator in ["!"]:
        return 1
    print("binary because of", last_token)
    return 2

def is_left_associative(operator, last_token):
    if operator in ["+", "-"] and (last_token == None or last_token.kind not in [lexer.NUMBER, lexer.IDENTIFIER, lexer.NUMBER]):
        print("right associative because of", last_token)
        return False
    elif operator in ["!", "^"]:
        return False
    print("left associative because of", last_token)
    return True

def get_precedence(operator, last_token):
    if operator in ["+", "-"] and (last_token == None or last_token.kind not in [lexer.NUMBER, lexer.IDENTIFIER, lexer.NUMBER]):
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
        print("======== NEXT TOKEN")
        print("Operands: ", ', '.join(str(e) for e in operand_stack))
        print("Operators:", ', '.join(str(e) for e in operator_stack))
        last_token = token
        token = stream[i]
        if token.kind == lexer.NUMBER:
            value = env.Value(lib.FLOAT, data=float(token.value))
            operand_stack.append(ast.Literal(value))
        elif token.kind == lexer.STRING:
            value = env.Value(lib.STRING, data=token.value)
            operand_stack.append(ast.Literal(value))
        elif token.kind == lexer.SEPERATOR:
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

            print("adding operator", new_operator.symbol, "to", len(operator_stack))

            while len(operator_stack) > 0 and (type(operator_stack[-1]) is ast.Operation):
                other = operator_stack[-1]
                other_prec = operator_stack[-1].tag("precedence")

                print("comparing precedence of ", new_operator.symbol, prec, "to", other.symbol, other_prec)

                if left_associative:
                    if prec > other_prec:
                        break
                else:
                    if prec >= other_prec:
                        break
                pop_off_operator()

            operator_stack.append(new_operator)
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
            return operand_stack[0], i

    last_token = token

    while len(operator_stack) > 0:
        pop_off_operator()

    print("Operands: ", ', '.join(str(e) for e in operand_stack))
    print("Operators:", ', '.join(str(e) for e in operator_stack))
    if len(operand_stack) > 1:
        raise InvalidExpression()

    return operand_stack[0], max

def generate_declaration(stream):
    end = find_statement(stream, 0)

    if end < 3 or stream[0].kind != lexer.IDENTIFIER:
        raise InvalidDeclaration()

    name_token, decl_token, type_token = stream[0], stream[1], stream[2]

    if decl_token.kind != lexer.OPERATOR or decl_token.value != ":" or type_token.kind != lexer.IDENTIFIER:
        raise InvalidDeclaration()
    decl = ast.Declaration(name_token.value, type_token.value)

    if end < 5:
        return decl, end

    if not is_assignment(stream[3]):
        raise InvalidAssignment()

    sequ = ast.Sequence()
    sequ.add(decl)

    expr, _ = generate_expression(stream[4:])
    assgn = ast.Assignment(name_token.value)
    assgn.add(expr)
    sequ.add(assgn)

    return sequ, end

def generate_assignment(stream):
    if len(stream) < 3:
        raise InvalidAssignment()

    name_token, equ_token = stream[0], stream[1]
    if name_token.kind != lexer.IDENTIFIER or not is_assignment(equ_token):
        raise InvalidAssignment()

    expr, offset = generate_expression(stream[2:])
    assgn = ast.Assignment(name_token.value)
    assgn.add(expr)

    return assgn, 2 + offset

def generate_while(stream):
    cond_start = stream[0]
    if cond_start.kind != lexer.LPRT:
        raise InvalidCondition()

    #print(str(cond_start))
    cond_end_index = find_matching_prt(stream, 1)
    #print(str(cond_end_index))
    if cond_end_index == -1:
        raise InvalidCondition()


    body_start_index = cond_end_index+1
    body_start = stream[cond_end_index+1]

    #print(body_start_index, str(body_start))
    if body_start.kind != lexer.LBLOCK:
        raise InvalidBlock()
    body_end_index = find_matching_block(stream, body_start_index+1)

    condition, cond_len = generate_expression(stream[1:cond_end_index])
    body, offset = generate_sequence(stream[body_start_index+1:])
    loop = ast.Loop()
    loop.add(condition)
    loop.add(body)

    return loop, 4 + cond_len + offset

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
                expr, offset = generate_expression(stream[i+1:])
                return_node = ast.Return()
                return_node.add(expr)
                sequence.add(return_node)
                i += offset + 1
            elif token.value == "continue":
                sequence.add(ast.Continue())
            elif token.value == "break":
                sequence.add(ast.Break())
            elif token.value == "while":
                while_node, offset = generate_while(stream[i+1:])
                sequence.add(while_node)
                i += offset + 1
            elif token.value == "for":
                raise NotImplemented()
            elif token.value == "import":
                raise NotImplemented()
            elif token.value == "var":
                #print(stream)
                decl, offset = generate_declaration(stream[i+1:])
                sequence.add(decl)
                i += offset + 1
            else:
                if i < max and is_assignment(stream[i+1]):
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
        i += 1
    return sequence, i


def generate(tokens):
    """Parse the tokens to AST notation."""
    # clean off whitespaces
    clean = [t for t in tokens if t.kind != lexer.WHITESPACE]
    sequ, _ = generate_sequence(clean)
    return sequ

def demo_syntax_tree():
    """Initialize a demo syntax tree."""
    tree = ast.syntax_tree()
    return tree
