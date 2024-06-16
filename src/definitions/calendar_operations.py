from enum import Enum

class Operation(Enum):
    INFO = "i"
    CREATE = "c"
    GET = "g"
    UPDATE = "u"
    DELETE = "d"
    EXIT = "e"