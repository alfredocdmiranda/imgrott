import argparse
import codecs
import glob
import json
import os
from datetime import datetime
from enum import Enum
import logging
import select
import socket
import time
from itertools import cycle
from pathlib import Path

import libscrc

from imgrott.conf import Settings
from imgrott.constants import (
    GROWATT_SERVER_ADDR,
    GROWATT_SERVER_PORT,
    DEFAULT_ADDR,
    DEFAULT_PORT,
    SERVER_MAX_CONN,
    CONN_BUFFER_SIZE,
)
from imgrott.enums import ConnectionType
from imgrott.messages import DataloggerMessage, GrowattMessage

logging.basicConfig(level=logging.DEBUG)


class ImGrottBaseTCPServer:
    def __init__(self, config: Settings):
        self.config = config
        self.forward_to = (self.config.growatt_addr, self.config.growatt_port)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.config.addr, self.config.port))
        self.server.listen(SERVER_MAX_CONN)
        self.input_list = [self.server]
        self.connections = {}

    def run(self):
        while True:
            time.sleep(0.0002)  # TODO Verify if this is really necessary.
            input_ready, *_ = select.select(self.input_list, [], [])
            for sock in input_ready:
                if sock == self.server:
                    self.on_connect(sock)
                    continue

                data, addr = sock.recvfrom(CONN_BUFFER_SIZE)
                logging.debug(data)
                if len(data) == 0:
                    self.on_close(sock)
                    continue

                self.on_receive(sock, data)

                # try:
                #     self.data, self.addr = sock.recvfrom(CONN_BUFFER_SIZE)
                # except:
                #     if conf.verbose : print("\t - Grott connection error")
                #     self.on_close(conf)
                #     break
                # if len(self.data) == 0:
                #     self.on_close(conf)
                #     break
                # else:
                #     self.on_recv(conf)

    def on_close(self, sock: socket.socket) -> None:
        addr, port = sock.getpeername()
        forward_conn = self.connections[sock]["forward"]
        if forward_conn:
            self.connections.pop(forward_conn)
            self.input_list.remove(forward_conn)
            forward_conn.close()
        self.connections.pop(sock, None)
        self.input_list.remove(sock)
        sock.close()
        logging.info(f'Closed connection for "{addr}" on port "{port}"')

    def on_connect(self, sock: socket.socket) -> None:
        datalogger_sock, datalogger_addr = sock.accept()
        self.input_list.append(datalogger_sock)
        self.connections[datalogger_sock] = {
            "type": ConnectionType.DATALOGGER,
            "devices": [],
            "forward": None,
        }
        logging.info(
            f'New Connection from "{datalogger_addr[0]}" on port "{datalogger_addr[1]}"'
        )

        if self.config.forward:
            forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_sock.connect(self.forward_to)
            self.input_list.append(forward_sock)
            self.connections[forward_sock] = {
                "type": ConnectionType.GROWATT,
                "devices": [],
                "forward": datalogger_sock,
            }
            self.connections[datalogger_sock]["forward"] = forward_sock
            logging.info(
                f'It will forward to "{self.forward_to[0]}" on port "{self.forward_to[1]}"'
            )

    def on_receive(self, sock: socket.socket, data: bytes) -> None:
        # if len(data) == 0:
        #     return None
        #
        # match self.connections[sock]["type"]:
        #     case ConnectionType.DATALOGGER:
        #         message = DataloggerMessage.read(data)
        #     case ConnectionType.GROWATT:
        #         message = GrowattMessage.read(data)
        #     case _:
        #         message = None
        #
        # return message
        raise NotImplementedError("Need to implement on_receive()")


class ImGrottOnlyForwardTCPServer(ImGrottBaseTCPServer):
    def on_receive(self, sock: socket.socket, data: bytes) -> None:
        if len(data) == 0:
            return None

        sock_forward = self.connections[sock].get("forward", None)
        if sock_forward:
            src_addr = sock.getpeername()[0]
            dest_addr = sock_forward.getpeername()[0]
            logging.info(
                f"Forwarding data from {src_addr}[{self.connections[sock]["type"]}] "
                f"to {dest_addr}[{self.connections[sock]["type"]}]"
            )
            try:
                sock_forward.sendall(data)
            except BaseException:
                logging.error("Failed to forward message.")
