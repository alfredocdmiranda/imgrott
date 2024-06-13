import argparse
import logging

from imgrott.conf import Settings
from imgrott.constants import (
    DEFAULT_ADDR,
    DEFAULT_PORT,
    GROWATT_SERVER_ADDR,
    GROWATT_SERVER_PORT,
)
from imgrott.server import ImGrottOnlyForwardTCPServer

LOGGING_FORMAT = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"


def arguments():
    parser = argparse.ArgumentParser(
        description="Improved Grott - Proxy Growatt Monitor Server"
    )
    parser.add_argument(
        "--addr",
        default=DEFAULT_ADDR,
        help="ImGrott server address will listen for Datalogger connections",
    )
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        type=int,
        help="ImGrott server port will listen for Datalogger connections",
    )
    parser.add_argument(
        "--growatt_addr",
        default=GROWATT_SERVER_ADDR,
        help="Growatt server address",
    )
    parser.add_argument(
        "--growatt_port",
        default=GROWATT_SERVER_PORT,
        type=int,
        help="Growatt server port",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Debug mode. More verbose.",
    )

    return parser.parse_known_args()


def main():
    args, unknown_args = arguments()
    settings = Settings.from_argparser(args)
    logging.basicConfig(
        level="DEBUG" if settings.debug else "INFO", format=LOGGING_FORMAT
    )

    logging.info("Starting ImGrott Server")
    server = ImGrottOnlyForwardTCPServer(settings)
    server.run()


if __name__ == "__main__":
    main()
