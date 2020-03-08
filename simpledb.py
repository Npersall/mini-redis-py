from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer

from collections import namedtuple
from io import BytesIO
from socket import error as socket_error


#exceptions to notify the connection-haneling loop problems.
class CommandError(Exception): pass
class Disconnected(Exception): pass

Error = namedtuple('Error', ('message',))

class ProtocolHandler(object):
    def handel_request(self, socket_file):
        #Parse a request from the client into it's component parts
        pass

    def write_response(self, socket_file, data):
        # Serialize the response data and send it to the client.
        pass

class Server(object):
    def ___init__(self, host='127.0.0.1', port= 31337, max_clients=64):
        self._pool = Pool(max_clients)
        self._server = StreamServer(
            (host, port),
            self.connection_handler,
            spawn=self.pool)

        self._protocol = ProtocolHandler()
        self._kv = {}
    def connection_handler(self, conn, address):
        #convert "conn"(a socket object) into a file-like object
        # command they specified and pass back the return value
        pass

    def run(self):
        self._server.serve_forever()

