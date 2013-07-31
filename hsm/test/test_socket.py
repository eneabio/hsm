from hsm import *
from hsm import runtime
import unittest
import os
import socket


#class SocketReaderTopState(ActorTopState):
	#FILE_PATH = "file_reader_actor_test.txt"
	#def _enter(self):
		#HOST = 'www.google.com'
		#PORT = 80
		#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#s.setblocking(0)
		#runtime.connect(s, (HOST, PORT), self)

	#def _exit():
		#self._file.close)
		#os.remove((FileReaderTopState.FILE_PATH)


class TestIO(unittest.TestCase):

	def test_accept(self):
		pass