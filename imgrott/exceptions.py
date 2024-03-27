class NoValidRecordException(Exception):
    pass


class InvalidCRCException(Exception):
    pass


class InvalidPayloadSizeException(Exception):
    pass


class ShortMessageSizeException(Exception):
    pass
