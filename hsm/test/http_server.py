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

	def _exit(self):
		self._parent.send_remove_context(self)
		self._socket  = None
		self._address = None
		self._http_parser = http_parser.parser()

@actor.initial_state
class TestContextWaitingRequest(TestContextTop):

	def _enter(self):
		iomonitor.monitor_incoming(self._socket, self)
		iomonitor.monitor_except(self._socket, self)

	def _exit(self):
		iomonitor.unmonitor(self._socket)

	def on_data_incoming(self, socket):
		data = socket.recv(4096)
		print """---\n%s---\n"""% data
		if data == "":
			iomonitor.unmonitor(self._socket)
			self.send_fini()

	def on_data_outgoing(self, socket):
		pass

	def on_parse_request(self):
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
