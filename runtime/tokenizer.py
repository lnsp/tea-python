"""Split the expression into tokens."""
import re

REGEX_OPERATOR = "^[+\-;]+$"
REGEX_WHITESPACE = "^\s+$"
REGEX_NUMBER = "^\-?[0-9]+(\.[0-9]+)?$"
REGEX_IDENTIFIER = "^[a-zA-Z_]+([0-9a-zA-Z_]+)?$"
REGEX_STRING = "^\"[^\\n\\r\"]*\"?$"

WHITESPACE = "whitespace"
STR_LITERAL = "str_literal"
IDENTIFIER = "identifier"
NUM_LITERAL = "num_literal"
OPERATOR = "operator"


def is_operator(item):
    """Check if the item is an operator."""
    return re.match(REGEX_OPERATOR, item)


def is_identifier(item):
    """Check if the item is an identifier."""
    return re.match(REGEX_IDENTIFIER, item)


def is_whitespace(item):
    """Check if the item is a whitespace."""
    return re.match(REGEX_WHITESPACE, item)


def is_number_literal(item):
    """Check if the item is a number."""
    return re.match(REGEX_NUMBER, item)


def is_string_literal(item):
    """Check if the item is a string."""
    return re.match(REGEX_STRING, item)


TOKEN_TYPES = {
    WHITESPACE: {
        "name": WHITESPACE,
        "match": is_whitespace,
    },
    OPERATOR: {
        "name": OPERATOR,
        "match": is_operator,
    },
    IDENTIFIER: {
        "name": IDENTIFIER,
        "match": is_identifier,
    },
    NUM_LITERAL: {
        "name": NUM_LITERAL,
        "match": is_number_literal,
    },
    STR_LITERAL: {
        "name": STR_LITERAL,
        "match": is_string_literal,
    }
}


def apply(expression):
    """Tokenize and classify the expression components."""
    token = {"value": "", "type": None}
    token_list = []

    # scan each character
    for char in expression:
        exp = token["value"] + char
        if token["type"] is not None and token["type"]["match"](exp):
            token["value"] = exp
        else:
            if token["type"] is not None:
                token_list.append(token)
            token = {"value": char, "type": match_type(char)}

    token_list.append(token)
    return token_list


def match_type(char):
    """Search for a matching type, return None when no match is found."""
    for _, candidate in TOKEN_TYPES.items():
        if candidate["match"](char):
            return candidate
    return None
