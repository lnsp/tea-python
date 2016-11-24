"""Parse an tokenized expression into an AST."""
from runtime import ast, lexer, env

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

def is_left_associative(operator):
    return True

def get_precedence(operator):
    prec = {"+": 4, "-": 4, "*": 5, "/": 5}
    return prec[operator]

def generate_expression(stream):
    return ast.Literal(env.Value(env.NULL))
    if tok.kind == lexer.NUMBER:
        queue.append(tok)
    elif tok.kind == lexer.STRING:
        queue.append(tok)
    elif tok.kind == lexer.IDENTIFIER:
        if i < max and clean_tokens[i+1].kind == lexer.RPRT:
            tok.kind = lexer.FUNCTION
            stack.append(tok)
        else:
            queue.append(tok)
    elif tok.kind == lexer.OPERATOR:
        prec = get_precedence(tok.value)
        while len(stack) > 0 and stack[-1].kind == lexer.OPERATOR:
            if is_left_associative(stack[-1].value):
                if get_precedence(stack[-1].value) < prec:
                    break
            else:
                if get_precedence(stack[-1].value) <= prec:
                    break
            queue.append(stack.pop())
        stack.append(tok)
    elif tok.kind == lexer.LPRT:
        stack.append(tok)
    elif tok.kind == lexer.RPRT:
        while len(stack) > 0 and stack[-1].kind != lexer.LPRT:
            queue.append(stack.pop())
        stack.pop()

        if stack[-1].kind == lexer.FUNCTION:
            queue.append(stack.pop())
    while len(stack) > 0:
        queue.append(stack.pop())

def generate_declaration(stream):
    if len(stream) < 3 or stream[0].kind != lexer.IDENTIFIER:
        raise InvalidDeclaration()
    name_token, decl_token, type_token = stream[0], stream[1], stream[2]
    if decl_token.kind != lexer.OPERATOR or decl_token.value != ":" or type_token.kind != lexer.IDENTIFIER:
            raise InvalidDeclaration()
    decl = ast.Declaration(name_token.value, type_token.value)
    return decl

def generate_assignment(stream):
    if len(stream) < 3:
        raise InvalidAssignment()
    name = stream
    pass

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
                if i < max and token[i+1].kind == lexer.ASSIGNMENT:
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
