CONN_BUFFER_SIZE = 4096
DEFAULT_ADDR = "0.0.0.0"
DEFAULT_PORT = 5279
GROWATT_SERVER_ADDR = "server.growatt.com"
GROWATT_SERVER_PORT = 5279
SERVER_MAX_CONN = 200

JSON_TEXT_TYPE_DATA_KEY = "text"
JSON_SIGNED_INT_TYPE_DATA_KEY = "int"
JSON_UNSIGNED_INT_TYPE_DATA_KEY = "uint"

GROWATT_MASK = "Growatt"
GROWATT_MASK_HEX = ["{:02x}".format(ord(x)) for x in GROWATT_MASK]
GROWATT_MASK_LEN = len(GROWATT_MASK_HEX)

ACK_DATA = b"\x47"

HEADER_BYTES_SLICE = slice(0, 8)
HEADER_MSG_ID_SLICE = slice(0, 2)
HEADER_PROTOCOL_SLICE = slice(2, 4)
HEADER_MSG_SIZE_SLICE = slice(4, 6)
HEADER_MSG_TYPE_SLICE = slice(6, 8)
PAYLOAD_NO_CRC_SLICE = slice(8, -2)
PAYLOAD_W_CRC_SLICE = slice(8, None)
