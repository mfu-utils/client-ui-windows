from socket import socket, AF_INET, SOCK_STREAM, error
from threading import Thread
from typing import Optional

from App.Core.Logger import Log
from App.Core.Network.Client import ClientConfig
from App.Core.Network.Client.ResponseDataPromise import ResponseDataPromise
from App.Core.Network.Protocol import RCL, RCLProtocol


class TcpClient(Thread):
    def __init__(self, config: ClientConfig, rcl: RCL, log: Log):
        super().__init__()
        self.__log = log

        self.__config = config

        self.__rcl = rcl
        self.__config = config
        self.__host = (self.__config.address, self.__config.port)
        self.__recv_size = self.__config.max_bytes_receive

        self.__running = True
        self.__received_data = b""
        self.__receive_len = 0
        self.__error_message = ""
        self.__promise: Optional[ResponseDataPromise] = None

        self.__socket: Optional[socket] = None

        self.__request = b""
        self.__ready_to_send = False

        self.__accepted = False

    def __try_connection(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.settimeout(self.__config.timeout)
        self.__socket.connect(self.__host)

    def terminate(self):
        self.__socket.close()
        self.__running = False

    def __recv_segment(self) -> bytes:
        return self.__socket.recv(self.__recv_size)

    def __determinate_len(self):
        start_index = RCLProtocol.RCL_HEADER_INDEX_DATA_LENGTH
        end_index = start_index + RCLProtocol.RCL_HEADER_LEN_DATA_LENGTH

        _len = int.from_bytes(self.__received_data[start_index:end_index], 'big')

        self.__receive_len = RCLProtocol.RCL_HEADERS_LENGTH + _len + 4

    def __try_accept(self):
        try:
            if segment := self.__recv_segment():
                self.__received_data += segment

                self.__determinate_len()

                while len(self.__received_data) < self.__receive_len:
                    self.__received_data += self.__recv_segment()

                self.__accepted = True
                self.__promise.set_result(self.__received_data)

        except error as e:
            self.__error_message = str(e)

    def get_error(self) -> Optional[str]:
        if self.__error_message:
            return self.__error_message

        return None

    def send(self, data: bytes) -> ResponseDataPromise:
        self.__request = data
        self.__ready_to_send = True

        self.__promise = ResponseDataPromise(self.__rcl)

        return self.__promise

    def run(self):
        try:
            self.__try_connection()
        except error as e:
            message = f"Cannot connect to server: {str(e)}"

            self.__log.error(message, {'object': self})

            self.terminate()

            if self.__promise:
                self.__promise.set_error(message)

        while self.__running:
            if not self.__ready_to_send:
                continue

            self.__ready_to_send = False

            self.__socket.sendall(self.__request)

            while not self.__accepted:
                self.__try_accept()
                continue

            self.terminate()
