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

    def handle_string(self, socket_file):
        # First read the length ($<length>\r\n).
        length = int(socket_file.readline().rstrip('\r\n'))
        if length == -1:
            return None  # Special case for NULLs.
        return socket_file.read(length)[:-2]

        num_elements = int(socket_file.readline().rstrip('\r\n'))
        return [self.handle_request(socket_file) for _ in range(num_elements)]

    def handle_dict(self, socket_file):
        num_items = int(socket_file.readline().rstrip('\r\n'))
        elements = [self.handle_request(socket_file) for _ in range(num_items * 2)]
        return dict(zip(elements[::2], elements[1::2]))

    # Serialize the response data and send it to the client.
    def write_response(self, socket_file, data):
        buf = BytesIO()
        self._write(buf, data)
        buf.seek(0)
        socket_file.write(buf.getvalue())
        socket_file.flush()

    def _write(self, buf, data):
        if isinstance(data, str):
            data = data.encode('utf-8')

        if isinstance(data, bytes):
            buf.write('$%s\r\n%s\r\n' % (len(data), data))
        elif isinstance(data, int):
            buf.write(':%s\r\n' % data)
        elif isinstance(data, Error):
            buf.write('-%s\r\n' % error.message)
        elif isinstance(data, (list, tuple)):
            buf.write('*%s\r\n' % len(data))
            for item in data:
                self._write(buf, item)
        elif isinstance(data, dict):
            buf.write('%%%s\r\n' % len(data))
            for key in data:
                self._write(buf, key)
                self._write(buf, data[key])
        elif data is None:
            buf.write('$-1\r\n')
        else:
            raise CommandError('unrecognized type: %s' % type(data))


class Server(object):
    def ___init__(self, host='127.0.0.1', port=31337, max_clients=64):
        self._pool = Pool(max_clients)
        self._server = StreamServer((host, port),
                                    self.connection_handler,
                                    spawn=self._pool)

        self._protocol = ProtocolHandler()
        self._kv = {}

        self._commands = self.get_commands()

    def get_commands(self):
        return {
            'GET': self.get,
            'SET': self.set,
            'DELETE': self.flush,
            'MGET': self.mget,
            'MSET': self.mset}
        }

    def get_response(self, data)
        if not isinstance(data,list):
            try:
                data = data.split()
            except:
                raise CommandError('Request must be list or simple string.')
            
        if not data:
            raise CommandErro('Missing command')
        
        command = data[0].upper()
        if command not in self._comands:
            raise CommandError('Unrecognized command: %s' % command)

        return self._commands[command](data[1:])
    
    def connection_handler(self, conn, address):
        # convert "conn"(a socket object) into a file-like object
        socket_file = conn.makefile('rwb')

        while True:
            try:
                data = self._protocol.handle_request(socket_file)
            except Disconnect:
                break

            try:
                resp = self.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])

            self._protocol.write_response(socket_file, resp)

    def get_response(self, data):
        # Here we'll actually unpack the data sent by the client, execute the
        # command they specified, and pass back the return value.

        pass

    def run(self):
        self._server.serve_forever()
