from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    FUNC = auto()
    LET = auto()
    MUT = auto()
    WHILE = auto()
    IF = auto()
    ELSE = auto()
    RECORD = auto()
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQEQ = auto()
    EQUAL = auto()
    LT = auto()
    GT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str
    line: int
    column: int
