import pytest

from imgrott.messages import Message
from imgrott.exceptions import InvalidCRCException, InvalidPayloadSizeException

scrambled_message = b"\x00\xbf\x00\x06\x01\x0e\x01\x20\x1f\x35\x2b\x41\x22\x38\x37\x7f\x44\x2c\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x2e\x31\x2a\x44\x36\x0f\x3c\x5f\x46\x2b\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x79\x72\x7e\x4f\x4a\x7c\x77\xa9\x74\x74\x47\xf6\x6f\x77\x68\x4f\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x7b\x61\x74\x74\x47\x72\x6f\x77\x61\x8b\x8b\xbf\xb9\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x7d\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x8d\x90\x8e\xb1\x74\x74\x47\x72\x6f\x77\x61\x74\x8b\xb8\x8f\x63\x77\x61\x74\x74\x47\x72\x6f\x77\x9e\x8b\x8c\x8c\x72\x6f\x7e\x61\x8b\x8b\xbe\xa2\x90\x88\x9c\x78\x74\x47\x73\x9b\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x18\xc3\x74\x74\x49\x01\x6f\x77\x70\x1c\x74\x47\x7d\x24\x77\x61\x74\x74\x47\x72\x11\x61\x61\x74\x54\xf3\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x66\xc4"
unscrambled_message = b"\x00\xbf\x00\x06\x01\x0e\x01\x20\x58\x47\x44\x36\x43\x4c\x43\x38\x36\x43\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x41\x46\x4b\x30\x42\x48\x4e\x30\x31\x4a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x06\x0a\x08\x38\x13\x00\xc8\x00\x00\x00\x84\x00\x00\x09\x3b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xf8\xcb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xf9\xd0\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xfd\x0c\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xf8\xcb\x00\x00\x09\x00\xff\xff\xf9\xd0\xff\xff\xfd\x0c\x00\x00\x01\xf4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x6f\xa2\x00\x00\x0e\x73\x00\x00\x11\x68\x00\x00\x0f\x4b\x00\x00\x00\x00\x00\x00\x7e\x16\x00\x00\x20\xb4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09\xb3"
scrambled_message_invalid_crc = b"\x00\xbf\x00\x06\x01\x0e\x01\x20\x1f\x35\x2b\x41\x22\x38\x37\x7f\x44\x2c\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x2e\x31\x2a\x44\x36\x0f\x3c\x5f\x46\x2b\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x79\x72\x7e\x4f\x4a\x7c\x77\xa9\x74\x74\x47\xf6\x6f\x77\x68\x4f\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x7b\x61\x74\x74\x47\x72\x6f\x77\x61\x8b\x8b\xbf\xb9\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x7d\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x8d\x90\x8e\xb1\x74\x74\x47\x72\x6f\x77\x61\x74\x8b\xb8\x8f\x63\x77\x61\x74\x74\x47\x72\x6f\x77\x9e\x8b\x8c\x8c\x72\x6f\x7e\x61\x8b\x8b\xbe\xa2\x90\x88\x9c\x78\x74\x47\x73\x9b\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x18\xc3\x74\x74\x49\x01\x6f\x77\x70\x1c\x74\x47\x7d\x24\x77\x61\x74\x74\x47\x72\x11\x61\x61\x74\x54\xf3\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x71\x66\xc4"
scrambled_message_invalid_size = b"\x00\xbf\x00\x06\x01\x0e\x01\x20\x1f\x35\x2b\x41\x22\x38\x37\x7f\x44\x2c\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x2e\x31\x2a\x44\x36\x0f\x3c\x5f\x46\x2b\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x79\x72\x7e\x4f\x4a\x7c\x77\xa9\x74\x74\x47\xf6\x6f\x77\x68\x4f\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x7b\x61\x74\x74\x47\x72\x6f\x77\x61\x8b\x8b\xbf\xb9\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x7d\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x8d\x90\x8e\xb1\x74\x74\x47\x72\x6f\x77\x61\x74\x8b\xb8\x8f\x63\x77\x61\x74\x74\x47\x72\x6f\x77\x9e\x8b\x8c\x8c\x72\x6f\x7e\x61\x8b\x8b\xbe\xa2\x90\x88\x9c\x78\x74\x47\x73\x9b\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x18\xc3\x74\x74\x49\x01\x6f\x77\x70\x1c\x74\x47\x7d\x24\x77\x61\x74\x74\x47\x72\x11\x61\x61\x74\x54\xf3\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x74\x74\x47\x72\x6f\x77\x61\x66\xc4"


def test_scramble():
    assert Message._scramble(scrambled_message) == unscrambled_message


def test_unscramble():
    assert Message._scramble(unscrambled_message) == scrambled_message


def test_validate_record_valid():
    assert Message._validate_packet(scrambled_message)


def test_validate_record_invalid_crc():
    with pytest.raises(InvalidCRCException):
        Message._validate_packet(scrambled_message_invalid_crc)


def test_validate_record_invalid_size():
    with pytest.raises(InvalidPayloadSizeException):
        Message._validate_packet(scrambled_message_invalid_size)