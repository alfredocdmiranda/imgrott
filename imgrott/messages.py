import codecs
import logging
from datetime import datetime
from itertools import cycle

import libscrc

from imgrott.constants import HEADER_BYTES_SLICE, MSG_TYPE_SLICE, PROTOCOL_MSG_SLICE, GROWATT_MASK_LEN, \
    GROWATT_MASK_HEX, HEADER_MSG_SIZE_SLICE, HEADER_PROTOCOL_SLICE, PAYLOAD_W_CRC_SLICE, HEADER_MSG_TYPE_SLICE, \
    ACK_DATA, PAYLOAD_NO_CRC_SLICE, JSON_UNSIGNED_INT_TYPE_DATA_KEY, JSON_TEXT_TYPE_DATA_KEY, \
    JSON_SIGNED_INT_TYPE_DATA_KEY
from imgrott.enums import ProtocolMessage, MessageType
from imgrott.exceptions import (
    InvalidCRCException,
    InvalidPayloadSizeException,
    ShortMessageSizeException,
    NoValidRecordException,
)

SMART_METER_MESSAGE_TYPE = (MessageType.SmartMeterData,)
GENERIC_MESSAGE_TYPE = (MessageType.InverterData, MessageType.Buffered)
CRC_SUPPORTED_PROTOCOLS = (ProtocolMessage.A, ProtocolMessage.B)
BUFFERED_MSG_TYPE = ProtocolMessage.A
IGNORED_MSG_TYPES = (
    MessageType.Announcement, MessageType.Ping, MessageType.ReadRegister, MessageType.SetRegister
)
NORMAL_PACKET_SIZE = 375


class Message:
    def __init__(
            self,
            datalogger_sn: str,
            inverter_sn: str,
            protocol: ProtocolMessage,
            type_: MessageType,
            date: datetime,
            data: dict[str, str | int],
            is_ack: bool = False
    ):
        """
        Args:
            datalogger_sn: Datalogger Serial Number
            inverter_sn: Solar Inverter Serial Number
            protocol: Message's protocol
            type_: Message's type
            date: Date and time the message was created
            data: All the data that comes in the payload
        """
        self.datalogger_sn = datalogger_sn
        self.inverter_sn = inverter_sn
        self.protocol = protocol
        self.type = type_
        self.date = date
        self.data = data
        self.is_ack = is_ack

    @classmethod
    def read(
            cls, data: bytes, layouts: dict[str, dict], inverter_type: str = "default"
    ):
        cls._validate_record(data)
        protocol = ProtocolMessage(data[HEADER_PROTOCOL_SLICE])
        msg_type = MessageType(data[HEADER_MSG_TYPE_SLICE])

        if cls._is_ack_packet(data[PAYLOAD_NO_CRC_SLICE]):
            logging.debug("ACK Packet received.")
            return

        if msg_type in IGNORED_MSG_TYPES:
            logging.debug("Message won't be processed. It is in list of ignored types.")
            return

        len_data = len(data)
        try:
            layout_name = cls._auto_layout_detection(
                len_data, protocol, msg_type, layouts, inverter_type
            )
            layout = layouts[layout_name]
        except NoValidRecordException:
            logging.warning(
                "Data Record not defined. No processing done."
            )
            return

        decrypted_data = data
        need_decrypt = layout.get("decrypt", True)
        if need_decrypt:
            decrypted_data = cls._decrypt(data)

        logging.debug(f"Growatt Datalogger Plain Data: {decrypted_data.hex()}")

        processed_data = cls._process_data(decrypted_data[PAYLOAD_NO_CRC_SLICE], layout, False)
        logging.debug(f"Gorwatt Datalogger Processed Data: {processed_data}")

        return cls(
            datalogger_sn=processed_data["datalogserial"],
            inverter_sn=processed_data["pvserial"],
            protocol=protocol,
            type_=msg_type,
            date=processed_data["date"],
            data=processed_data["data"]
        )

    @staticmethod
    def _is_ack_packet(data: bytes) -> bool:
        return data == ACK_DATA

    @staticmethod
    def _validate_record(data: bytes) -> bool:
        payload_size = int.from_bytes(data[HEADER_MSG_SIZE_SLICE], "big")
        protocol = ProtocolMessage(data[HEADER_PROTOCOL_SLICE])

        real_payload_size = len(data[PAYLOAD_W_CRC_SLICE])
        if real_payload_size != payload_size:
            raise InvalidPayloadSizeException("Invalid payload size")

        if protocol in CRC_SUPPORTED_PROTOCOLS:
            crc = int.from_bytes(data[-2:], "big")
            crc_calc = libscrc.modbus(data[:-2])

            if crc is not None and crc_calc is not None and crc != crc_calc:
                raise InvalidCRCException("Invalid CRC value")

        return True

    @staticmethod
    def _auto_layout_detection(
            len_data: int,
            protocol: ProtocolMessage,
            msg_type: MessageType,
            layouts: dict[str, dict],
            inverter_type: str = "default",
    ) -> str:
        """
        Detects automatically which layout is being used in the message.
        """
        logging.debug("Automatic Protocol Detection")
        logging.debug(f"Data Record Length: {len_data}")

        is_smart_meter = msg_type in SMART_METER_MESSAGE_TYPE
        layout_num = f"{protocol.value[-1:].hex()}{msg_type.value.hex()}"
        layout = f"T{layout_num}"

        if len_data > NORMAL_PACKET_SIZE and not is_smart_meter:
            # v270 add X for extended except for smart monitor records
            layout = f"{layout}X"

        # v270 no invtype added to layout for smart monitor records
        if inverter_type != "default" and not is_smart_meter:
            # TODO ?
            layout = f"{layout}{inverter_type.upper()}"

        logging.debug(f"Checking if layout [{layout}] exist.")
        if layout not in layouts:
            logging.debug(f"No matching record layout found, trying generic.")
            if msg_type in GENERIC_MESSAGE_TYPE:
                layout = layout.replace(msg_type.value.hex(), "NNNN")
                logging.debug(f"Checking if generic layout [{layout}] exist.")
                if layout not in layouts:
                    logging.error(f"No matching generic record layout found.")
                    raise NoValidRecordException("No matching generic record layout found")
            else:
                raise NoValidRecordException("No matching record layout found")

        logging.debug(f"Record layout used : {layout}")
        return layout

    @staticmethod
    def _decrypt(data: bytes) -> bytes:
        len_data = len(data)
        unscrambled = list(data[HEADER_BYTES_SLICE])

        for i, j in zip(range(0, len_data - 8), cycle(range(0, GROWATT_MASK_LEN))):
            unscrambled_value = data[i + 8] ^ int(GROWATT_MASK_HEX[j], 16)
            unscrambled.append(unscrambled_value)

        logging.debug("Growatt Datalogger data decrypted")

        return bytes(unscrambled)

    @staticmethod
    def _process_data(data: bytes, layout: dict[str, ...], buffered: bool) -> dict[str, ...]:
        processed_data = {
            "datalogserial": Decoder.text(
                data[
                    layout["datalogserial"]["offset"]:
                    layout["datalogserial"]["offset"] + layout["datalogserial"]["length"]
                ]
            ),
            "pvserial": Decoder.text(
                data[layout["pvserial"]["offset"]:layout["pvserial"]["offset"] + layout["pvserial"]["length"]]
            ),
            "date": datetime.now() if "date" not in layout else Decoder.datetime(
                data[layout["date"]["offset"]:layout["date"]["offset"] + layout["date"]["length"]]
            ),
            "data": {}
        }

        for keyword in layout["data"].keys():
            if keyword not in ("logstart",):
                include = layout["data"][keyword].get("incl", True)
                offset = layout["data"][keyword]["offset"]
                length = layout["data"][keyword]["length"]
                try:
                    if include:
                        key_type = layout["data"][keyword].get("type", "num")
                        if key_type == JSON_TEXT_TYPE_DATA_KEY:
                            processed_data["data"][keyword] = Decoder.text(data[offset:offset+length])
                        elif key_type == JSON_UNSIGNED_INT_TYPE_DATA_KEY:
                            processed_data["data"][keyword] = Decoder.unsigned(data[offset:offset+length])
                        elif key_type == JSON_SIGNED_INT_TYPE_DATA_KEY:
                            processed_data["data"][keyword] = Decoder.signed(data[offset:offset+length])
                except BaseException:
                    logging.exception("It happened some error while processing the data")
                    raise

        return processed_data


class Decoder:
    @staticmethod
    def datetime(data: bytes):
        logging.debug("Processing date")
        values = []
        for index, _ in enumerate(("year", "month", "day", "hours", "minutes", "seconds")):
            values.append(int.from_bytes(data[index:index + 1]))

        date_str = "20{}-{}-{}T{}:{}:{}".format(*values)
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def unsigned(data: bytes):
        return int.from_bytes(data, byteorder="big")

    @staticmethod
    def signed(data: bytes):
        return int.from_bytes(data, byteorder="big", signed=True)

    @staticmethod
    def text(data: bytes):
        return data.decode("utf-8").rstrip("\x00")
