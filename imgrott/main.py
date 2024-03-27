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
from imgrott.server import ImGrottOnlyForwardTCPServer


def load_layouts(folder: str) -> dict[str, dict]:
    """"""
    files = glob.glob(os.path.join(folder, "*.json"))
    layouts = {}
    for file in files:
        logging.debug(f"Loading layout file: {file}")
        layout = json.load(open(file))
        layouts[layout["name"]] = layout

    return layouts


def arguments():
    parser = argparse.ArgumentParser(
        description="Improved Grott - Alternative Growatt Monitor Server"
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
        "--no-forward",
        dest="forward",
        action="store_false",
        help="Do not forward data to Growatt's servers",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[],
        help="Do not forward data to Growatt's servers",
    )

    return parser.parse_args()


def main():
    logging.info("Starting ImGrott Server")
    args = arguments()
    settings = Settings.from_argparser(args)
    layouts = load_layouts(f"{Path(__file__).parent}/data")
    server = ImGrottOnlyForwardTCPServer(settings)
    server.run()


if __name__ == "__main__":
    main()
