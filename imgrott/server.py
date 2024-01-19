import argparse

from conf import Settings
from constants import GROWATT_SERVER_ADDR, GROWATT_SERVER_PORT, DEFAULT_ADDR, DEFAULT_PORT


def arguments():
    parser = argparse.ArgumentParser(
        description='Alternative Growatt Monitor Server'
    )
    parser.add_argument(
        "--addr", default=DEFAULT_ADDR, help="ImGrott server address will listen for Datalogger connections",
    )
    parser.add_argument(
        "--port", default=DEFAULT_PORT, type=int, help="ImGrott server port will listen for Datalogger connections",
    )
    parser.add_argument(
        "--growatt_addr", default=GROWATT_SERVER_ADDR, help="Growatt server address",
    )
    parser.add_argument(
        "--growatt_port", default=GROWATT_SERVER_PORT, type=int, help="Growatt server port",
    )
    parser.add_argument(
        "--no-forward", dest="forward", action="store_false", help="Do not forward data to Growatt's servers",
    )
    parser.add_argument(
        "--extensions", nargs="+", default=[], help="Do not forward data to Growatt's servers",
    )

    return parser.parse_args()


def main():
    args = arguments()
    settings = Settings.from_argparser(args)
    print(settings)


if __name__ == "__main__":
    main()
