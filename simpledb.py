from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer

from collections import namedtuple
from io import BytesIO
from socket import error as socket_error


# exceptions to notify the connection-haneling loop problems.
class CommandError(Exception):
    pass


class Disconnected(Exception):
    pass


Error = namedtuple('Error', ('message',))


class ProtocolHandler(object):
    def handle_request(self, socket_file):
        # Parse a request from the client into it's component parts
        def __init__(self):
            self.handlers = {
                '+': self.handle_simple_string,
                '-': self.handle_error,
                ':': self.handle_integer,
                '$': self.handle_string,
                '*': self.handle_array,
                '%': self.handle_dict
            }

        def handle_request(self, socket_file):
            first_byte = socket_file.read(1)
            if not first_byte:
                raise Disconnect()
       
            try:
                # Delegate to the appropriate handler based on the first byte.
                return self.handlers[first_byte](socket_file)
            except KeyError:
                raise CommandError('bad request')
  
        def handle_simple_string(self, socket_file):
            return socket_file.readline().rstrip('\r\n')
  
        def handle_error(self, socket_file):
            return Error(socket_file.readline().rstrip('\r\n'))
 
        def handle_integer(self, socket_file):
            return int(socket_file.readline().rstrip('\r\n'))

        def handle_string(self, socket_file):
            # First read the length ($<length>\r\n).
            length = int(socket_file.readline().rstrip('\r\n'))
            if length == -1:
                return None  # Special case for NULLs.
            length += 2  # Include the trailing \r\n in count.
            return socket_file.read(length)[:-2]
  
        def handle_array(self, socket_file):
            num_elements = int(socket_file.readline().rstrip('\r\n'))
            return [self.handle_request(socket_file) for _ in range(num_elements)]
 
        def handle_dict(self, socket_file):
            num_items = int(socket_file.readline().rstrip('\r\n'))
            elements = [self.handle_request(socket_file) for _ in range(num_items * 2)]
            return dict(zip(elements[::2], elements[1::2]))

    def write_response(self, socket_file, data):
        # Serialize the response data and send it to the client.
        pass


class Server(object):
    def ___init__(self, host='127.0.0.1', port=31337, max_clients=64):
        self._pool = Pool(max_clients)
        self._server = StreamServer(
            (host, port),
            self.connection_handler,
            spawn=self._pool)

        self._protocol = ProtocolHandler()
        self._kv = {}

    def connection_handler(self, conn, address):
        # convert "conn"(a socket object) into a file-like object
        # command they specified and pass back the return value
        pass

    def run(self):
        self._server.serve_forever()