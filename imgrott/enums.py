from enum import Enum


class ConnectionType(Enum):
    DATALOGGER = "datalogger"
    GROWATT = "growatt"


class ProtocolMessage(str, Enum):
    A = "05"
    B = "06"
    C = "02"


class MessageType(str, Enum):
    A = "50"
    B = "04"
    C = "20"
    D = "1b"
