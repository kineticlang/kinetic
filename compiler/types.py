from dataclasses import dataclass
from enum import Enum, auto


class KType(Enum):
    INT = auto()
    STRING = auto()
    BOOL = auto()
    INT_ARRAY = auto()
    VOID = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class RecordType:
    name: str


@dataclass
class FunctionType:
    parameters: list[KType | RecordType]
    result: KType | RecordType
