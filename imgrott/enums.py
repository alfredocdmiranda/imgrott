from enum import Enum


class ConnectionType(Enum):
    DATALOGGER = "datalogger"
    GROWATT = "growatt"


class ProtocolMessage(Enum):
    A = b"\x00\x05"
    B = b"\x00\x06"
    C = b"\x00\x02"


class MessageType(bytes, Enum):
    Announcement = b"\x01\x03"
    Buffered = b"\x01\x50"
    InverterData = b"\x01\x04"
    Ping = b"\x01\x16"
    ReadRegister = b"\x01\x19"
    SetRegister = b"\x01\x18"
    SmartMeterData = b"\x01\x20"
