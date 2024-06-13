import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Decoder:
    @staticmethod
    def datetime(data: bytes):
        values = []
        for index, _ in enumerate(
            ("year", "month", "day", "hours", "minutes", "seconds")
        ):
            values.append(int.from_bytes(data[index : index + 1]))

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
