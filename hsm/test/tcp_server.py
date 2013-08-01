from hsm import actor
from hsm import runtime
from hsm import iomonitor
import http_parser

import unittest
import socket

# Context #####################################################################

class TestContextTop(actor.TopState):

        def __init__(self, (socket, address), parent):
                self._socket  = socket
                self._address = address
                self._parent = parent
                self._body = ""
                self._to_send = 0
                self._sent = 0
                self._reply = ""

        def _enter(self):
                iomonitor.monitor_except(self._socket, self)

        def _exit(self):
                iomonitor.unmonitor_except(self._socket)
                self._parent.send_remove_context(self)
                self._socket  = None
                self._address = None
                self._http_parser = http_parser.parser()

@actor.initial_state
class TestContextWaitingRequest(TestContextTop):

        def _enter(self):
                iomonitor.monitor_incoming(self._socket, self)

        def _exit(self):
                iomonitor.unmonitor_incoming(self._socket)

        def on_data_incoming(self, socket):
                data = socket.recv(4096)
                print """---\n%s---\n"""% data
                if data == "":
                        iomonitor.unmonitor(self._socket)
                        self.send_fini()
                recved = len(data)
                nparsed = p.execute(data, recved)
                assert nparsed == recved
                if p.is_headers_complete():
                        print p.get_headers()

                if p.is_partial_body():
                        self._body.append(p.recv_body())

                if p.is_message_complete():
                        self.transition()

        def on_data_except(self, socket):
                pass


class TestContextBuildResponse(TestContextTop):
        def _enter(self):
                iomonitor.monitor_outgoing(self._socket)

        def _exit(self):
                iomonitor.unmonitor(self._socket)

        def on_data_outgoing(self, socket):
                msg = ""
                self._to_send = len(msg)
                self._sent = 0

                #build msg here
                self.transition(TestContextSendResponse)

        def on_data_except(self, socket):
                self.send_fini()

class TestContextSendResponse(TestContextTop):

        def _enter(self):
                iomonitor.monitor_outgoing(self._socket)

        def _exit(self):
                iomonitor.unmonitor(self._socket)

        def on_data_outgoing(self, socket):
                pass

        def on_data_except(self, socket):
                pass

# Server ######################################################################

class TcpServer(actor.TopState):

        def __init__(self, host, port, backlog, Context):
                actor.TopState.__init__(self)
                self._acceptor = None
                self._host     = host
                self._port     = port
                self._backlog  = backlog
                self._Context  = Context
                self._context_index = {}

        def on_remove_context(self, ctx):
                print "about to remove context"
                del self._context_index[ctx]

        def _enter(self):
                self._log.trace("Server is idle")
                sock = socket.socket()
                sock.bind( (self._host, self._port) )
                self._acceptor = sock

        def _exit(self):
                io.close(self._acceptor)
                self._acceptor = None

@actor.initial_state
class TcpServerIdle(TcpServer):

        def on_start(self):
                self._acceptor.listen(self._backlog)
                self.transition(TcpServerRunning)

class TcpServerError(TcpServer):
        def _enter():
                pass
        def _exit():
                pass

class TcpServerRunning(TcpServer):

        def _enter(self):
                iomonitor.monitor_incoming(self._acceptor, self)
                iomonitor.monitor_except(self._acceptor, self)
                print "Server is running"

        def _exit(self):
                iomonitor.unmonitor(self._acceptor)

        def on_data_incoming(self, socket):
                sock_addr_tuple = socket.accept()
                self._log.info( "Accepted client from addr:%s", sock_addr_tuple[1] )
                context = self._Context(sock_addr_tuple, self)
                self._context_index[context] = context

        def on_data_except(self, socket):
                self.transition(TcpServerError)

        def on_stop(self):
                self.transition(TcpServerIdle)

        def on_start(self):
                self._log.warn("Server already running")



print "test tcp server"
server = TcpServer("localhost", 8080, 16, TestContextTop)
server.send_start()
while True:
        msg = runtime.get_msg()
        if msg:
                if msg[0] == "quit":
                        break
                runtime.dispatch_msg(msg)
                continue
        iomonitor.update()