import logging
from itertools import cycle

import libscrc

from imgrott.constants import HEADER_BYTES_SLICE, MSG_TYPE_SLICE, PROTOCOL_MSG_SLICE, GROWATT_MASK_LEN, GROWATT_MASK_HEX
from imgrott.enums import ProtocolMessage, MessageType
from imgrott.exceptions import (
    InvalidCRCException,
    InvalidPayloadSizeException,
    ShortMessageSizeException,
    NoValidRecordException,
)

SMART_METER_MESSAGE_TYPE = (MessageType.C, MessageType.D)
GENERIC_MESSAGE_TYPE = (MessageType.A, MessageType.B)
CRC_SUPPORTED_PROTOCOLS = (ProtocolMessage.A, ProtocolMessage.B)
BUFFERED_MSG_TYPE = ProtocolMessage.A


class Message:
    @classmethod
    def read(cls, data: bytes, layouts: list[dict], inverter_type: str = "default"):
        raise NotImplementedError

    @staticmethod
    def _get_header(data: bytes) -> str:
        return "".join("{:02x}".format(n) for n in data[HEADER_BYTES_SLICE])

    @staticmethod
    def _validate_record(data: bytes) -> bool:
        len_data = len(data)
        payload_size = int.from_bytes(data[4:6], "big")
        header = Message._get_header(data)
        protocol = ProtocolMessage(header[6:8])

        len_crc = 0
        crc = None
        crc_calc = None
        if protocol in CRC_SUPPORTED_PROTOCOLS:
            len_crc = 4  # TODO bytes?
            crc = int.from_bytes(data[-2:], "big")
            crc_calc = libscrc.modbus(data[0 : len_data - 2])

        real_payload_size = (
            len_data * 2 - 12 - len_crc
        ) / 2  # TODO What does this calculation do?

        if real_payload_size == payload_size:
            if crc is not None and crc_calc is not None and crc != crc_calc:
                raise InvalidCRCException("Invalid CRC value")
            return True
        else:
            raise InvalidPayloadSizeException("Invalid payload size")


class DataloggerMessage(Message):
    def __init__(self):
        pass

    @classmethod
    def read(
        cls, data: bytes, layouts: dict[str, dict], inverter_type: str = "default"
    ):
        cls._validate_record(data)
        header = cls._get_header(data)
        len_data = len(data)
        is_buffered = True if header[MSG_TYPE_SLICE] == BUFFERED_MSG_TYPE else False

        if len_data < 12:
            raise ShortMessageSizeException("Data size too small")

        # TODO Need to add layout to the configurations
        layout = None
        try:
            layout = cls._auto_layout_detection(
                len_data, header, layouts, inverter_type
            )
        except NoValidRecordException:
            logging.warning(
                "Data ACK Record or Data Record not defined. No processing done."
            )

        need_decrypt = layouts[layout].get("decrypt", True)
        if need_decrypt:
            result_str = cls._decrypt(data)
        else:
            result_str = data.hex()

        logging.debug(f"Growatt Datalogger Plain Data: {result_str}")

        is_data_processed = False
        layout = cls._auto_layout_detection_by_inv_serial(
            result_str, layout, len_data, header, inverter_type
        )

    @staticmethod
    def _auto_layout_detection(
        len_data: int,
        header: str,
        layouts: dict[str, dict],
        inverter_type: str = "default",
    ) -> str:
        """
        Detects automatically which layout is being used in the message.
        """
        logging.debug("Automatic Protocol Detection")
        logging.debug(f"Data Record Length: {len_data}")

        is_smart_meter = header[MSG_TYPE_SLICE] in SMART_METER_MESSAGE_TYPE
        layout = f"T{header[PROTOCOL_MSG_SLICE]}{header[12:14]}{header[MSG_TYPE_SLICE]}"

        if len_data > 375 and not is_smart_meter:
            # v270 add X for extended except for smart monitor records
            layout = f"{layout}X"

        # v270 no invtype added to layout for smart monitor records
        if inverter_type != "default" and not is_smart_meter:
            layout = f"{layout}{inverter_type.upper()}"

        if layout not in layouts:
            logging.debug(f"No matching record layout found, trying generic")
            if header[MSG_TYPE_SLICE] in GENERIC_MESSAGE_TYPE:
                layout = layout.replace(header[12:16], "NNNN")
                if layout not in layouts:
                    raise NoValidRecordException("No matching record layout found")
            else:
                raise NoValidRecordException("No matching record layout found")

        logging.debug(f"Record layout used : {layout}")
        return layout

    @staticmethod
    def _auto_layout_detection_by_inv_serial(
        data: str,
        layout: str,
        len_data: int,
        header: str,
        inverter_type: str = "default",
    ) -> str:
        """
        Detects automatically which layout is being used in the message using the Serial Inverter.
        """
        is_smart_meter = header[MESSAGE_TYPE_SLICE] in SMART_METER_MESSAGE_TYPE
        if inverter_type == "default":
            # Handle systems with mixed invtype
            if len_data > 50 and not is_smart_meter:
                # There is enough data for an inverter serial number
                inverter_serial = None
                try:
                    inverter_serial = codecs.decode(data[76:96], "hex").decode("ASCII")
                except UnicodeDecodeError:
                    # In case of problem (eg: new record type with different serial placement)
                    logging.warning(
                        "It happened some error while trying to decode Inverter's Serial Number. "
                        "This may be a new record type with a serial number in a different place."
                    )

                inverter_type = {}.get(inverter_serial, "default")
                if inverter_type != "default":
                    layout = layout + inverter_type.upper()
        return layout

    @staticmethod
    def _decrypt(data: bytes) -> str:
        len_data = len(data)
        unscrambled = list(data[HEADER_BYTES_SLICE])

        for i, j in zip(range(0, len_data - 8), cycle(range(0, GROWATT_MASK_LEN))):
            unscrambled = unscrambled + [data[i + 8] ^ int(GROWATT_MASK_HEX[j], 16)]

        result_string = "".join("{:02x}".format(n) for n in unscrambled)
        logging.debug("Growatt Datalogger data decrypted")

        return result_string

    @staticmethod
    def _process_data(data: str, layout: dict[str, ...], buffered: bool):
        processed_data = {}
        for keyword in layout["data"].keys():
            if keyword not in ("date", "logstart", "device"):
                # try if keyword should be included
                include = layout["data"][keyword].get("incl", True)
                # process only keyword needs to be included (default):
                try:
                    if include:
                        key_type = layout["data"][keyword].get("type", "num")
                        if key_type == "text":
                            DataloggerMessage._decode_text(
                                data, layout["data"][keyword]
                            )
                        if key_type == "num":
                            DataloggerMessage._decode_num(data, layout["data"][keyword])
                        if key_type == "numx":
                            DataloggerMessage._decode_numx(
                                data, layout["data"][keyword]
                            )
                except BaseException:
                    logging.exception(
                        "It happened some error while processing the data"
                    )
                    raise

                    # test if pvserial was defined, if not take inverterid from config.
        # device_defined = False
        # try:
        #     device = layout.get("device")
        #     device_defined = True
        # except:
        #     # test if pvserial was defined, if not take inverterid from config.
        #     try:
        #         test = definedkey["pvserial"]
        #     except:
        #         definedkey["pvserial"] = conf.inverterid
        #         conf.recorddict[layout]["pvserial"] = {"value": 0, "type": "text"}
        #         if conf.verbose: print(
        #             "\t - pvserial not found and device not specified used configuration defined invertid:",
        #             definedkey["pvserial"])

        date = DataloggerMessage._get_datetime(data, layout["data"]["date"], buffered)
        date_from_server = False
        if not date:
            date = datetime.now().replace(microsecond=0).isoformat()
            date_from_server = True

        # filter invalid 0120 record (0 < voltage_l1 > 500 )
        if header[MESSAGE_TYPE_SLICE] == "20":
            if (definedkey["voltage_l1"] / 10 > 500) or (
                definedkey["voltage_l1"] / 10 < 0
            ):
                print("\t - " + "Grott invalid 0120 record processing stopped")
                return

                # v270
        # compatibility with prev releases for "20" smart monitor record!
        # if device is not specified in layout record datalogserial is used as device (to distinguish record from inverter record)

        if device_defined == True:
            deviceid = definedkey["device"]

        else:
            if not is_smart_meter:
                deviceid = definedkey["pvserial"]
            else:
                deviceid = definedkey["datalogserial"]

        jsonobj = {
            "device": deviceid,
            "time": jsondate,
            "buffered": buffered,
            "values": {},
        }

        for key in definedkey:
            # if key != "pvserial" :
            # if conf.recorddict[layout][key]["type"] == "num" :
            # only add int values to the json object
            # print(definedkey[key])
            # print(type(definedkey[key]))
            # if type(definedkey[key]) == type(1) :
            #    jsonobj["values"][key] = definedkey[key]
            jsonobj["values"][key] = definedkey[key]

        jsonmsg = json.dumps(jsonobj)

        # if buffered and date_from_server:
        #         if conf.verbose: print(
        #             "\t - " + 'Buffered record not sent: sendbuf = False or invalid date/time format')
        #         return

    @staticmethod
    def _get_datetime(data: str, layout: dict[str, ...], buffered) -> str:
        offset = int(layout.get("value", 0))

        date_str = None
        if offset > 0 and buffered:
            logging.debug("Processing date")
            pvyearI = int(data[offset : offset + 2], 16)
            pvyear = f"20{pvyearI:02d}"

            pvmonthI = int(data[offset + 2 : offset + 4], 16)
            pvmonth = f"{pvmonthI:02d}"

            pvdayI = int(data[offset + 4 : offset + 6], 16)
            pvday = f"{pvdayI:02d}"

            # Time
            pvhourI = int(data[offset + 6 : offset + 8], 16)
            pvhour = f"{pvhourI:02d}"

            pvminuteI = int(data[offset + 8 : offset + 10], 16)
            pvminute = f"{pvminuteI:02d}"

            pvsecondI = int(data[offset + 10 : offset + 12], 16)
            pvsecond = f"{pvsecondI:02d}"

            # create date/time is format
            pvdate = f"{pvyear}-{pvmonth}-{pvday}T{pvhour}:{pvminute}:{pvsecond}"
            # test if valid date/time in data record
            try:
                datetime.strptime(pvdate, "%Y-%m-%dT%H:%M:%S")
                date_str = pvdate
            except ValueError:
                logging.error(
                    f"Date could not be parsed: {pvdate}. It is either an invalid record or a new layout."
                )

        return date_str

    @staticmethod
    def _decode_text(data: str, layout: dict) -> str:
        start = layout["value"]
        end = start + (layout["length"] * 2)
        return codecs.decode(data[start:end], "hex").decode("utf-8")

    @staticmethod
    def _decode_num(data: str, layout: dict) -> int:
        start = layout["value"]
        end = start + (layout["length"] * 2)
        return int(data[start:end], 16)

    @staticmethod
    def _decode_numx(data: str, layout: dict) -> int:
        start = layout["value"]
        end = start + (layout["length"] * 2)

        data_bytes = bytes.fromhex(data[start:end])
        return int.from_bytes(data_bytes, byteorder="big", signed=True)


class GrowattMessage(Message):
    @classmethod
    def read(
        cls,
        data: bytes,
        layouts: list[dict],
        compatible_mode: bool = False,
        inverter_type: str = "default",
    ):
        pass
