import argparse
import glob
import json
import logging
import os
from pathlib import Path

from imgrott.conf import Settings
from imgrott.constants import (
    DEFAULT_ADDR,
    DEFAULT_PORT,
    GROWATT_SERVER_ADDR,
    GROWATT_SERVER_PORT,
)
from imgrott.server import ImGrottBaseTCPServer
from imgrott.services import ExtensionsService

LOGGING_FORMAT = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
SCHEMAS_DIR = f"{Path(__file__).parent}/data"


def load_layouts(folder: str) -> dict[str, dict]:
    """
    Loads layouts from folder
    """
    files = glob.glob(os.path.join(folder, "*.json"))
    layouts = {}
    for file in files:
        logging.debug(f"Loading layout file: {file}")
        layout = json.load(open(file))
        layouts[layout["name"]] = layout

    return layouts


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
    parser.add_argument(
        "--extension-help",
        help="The extension you want to print hepl function.",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[],
        help="The extension you want to enable.",
    )

    return parser.parse_known_args()


def main():
    args, unknown_args = arguments()
    ext_service = ExtensionsService()
    if args.extension_help:
        ext_service.print_help(args.extension_help)
        exit(0)

    settings = Settings.from_argparser(args)
    logging.basicConfig(
        level="DEBUG" if settings.debug else "INFO", format=LOGGING_FORMAT
    )

    logging.info("Starting ImGrott Server")
    layouts = load_layouts(SCHEMAS_DIR)
    ext_service.load_extensions(settings.extensions, unknown_args)
    server = ImGrottBaseTCPServer(settings, layouts)
    server.run()


if __name__ == "__main__":
    main()
