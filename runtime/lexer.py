"""Split the expression into tokens."""
import re
import collections

REGEX_OPERATOR = r"^([+\-*/=:()]?|([+\-*/%]=)|)$"
REGEX_WHITESPACE = r"^\s+$"
REGEX_NUMBER = r"^\-?[0-9]+(\.[0-9]*)?$"
REGEX_IDENTIFIER = r"^[a-zA-Z_]+([0-9a-zA-Z_]+)?$"
REGEX_STRING = r'^"[^\n\r"]*"?$'

class TokenType(collections.namedtuple("TokenType", ["name", "match"])):
    """A type of a token."""
    __slots__ = ()
    def __str__(self):
        return self.name

class TokenTuple(collections.namedtuple("Token", ["value", "kind"])):
    """A lexed token."""
    __slots__ = ()
    def __str__(self):
        return "%s '%s'" % (str(self.kind), self.value)
    def __eq__(self, other):
        if isinstance(other, TokenTuple):
            return self.kind is other.kind and other.value == self.value

WHITESPACE = TokenType("whitespace", lambda item: re.match(REGEX_WHITESPACE, item))
OPERATOR = TokenType("operator", lambda item: re.match(REGEX_OPERATOR, item))
IDENTIFIER = TokenType("identifier", lambda item: re.match(REGEX_IDENTIFIER, item))
NUMBER = TokenType("number", lambda item: re.match(REGEX_NUMBER, item))
STRING = TokenType("string", lambda item: re.match(REGEX_STRING, item))

TOKEN_TYPES = [
    WHITESPACE, OPERATOR, IDENTIFIER, NUMBER, STRING
]

def run(expression):
    """Tokenize and classify the expression components."""
    active_token = TokenTuple(value="", kind=None)
    token_list = []

    # scan each character
    for character in expression:
        value = active_token.value + character
        kind = active_token.kind
        if kind is not None and kind.match(value):
            active_token = TokenTuple(value=value, kind=kind)
        else:
            if kind is not None:
                token_list.append(active_token)
            active_token = TokenTuple(value=character, kind=match_type(character))

    token_list.append(active_token)
    return token_list


def match_type(char):
    """Search for a matching type, return None when no match is found."""
    for candidate in TOKEN_TYPES:
        if candidate.match(char):
            return candidate
    return None
