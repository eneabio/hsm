# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the "MIT license"
# see LICENCE.txt

"""
runtime -- the hsm runtime which deals with messaging

A message within the hsm framework is defined as a tuple that stores three elements:
(signal, tuple_payload, map_payload).

- signal must be of type str, tuple_payload must be string, map_payload must be a map.
- tuple_payload has at least one value which is called target, which stores a reference
to the object that should receive the message.

Hierarchical state machines communicate by sending messages stored in the runtime.

Note that runtime doesn't support multithreading and never will.

The runtime is designed for real-time applications (such as games or
guis) and it's raccomanded to drive the entire application by using a 'main loop'
such as the following:

from hsm import runtime

#Init app here: setup initial actors

While True:
    msg = get_msg()
    if msg:
        if msg[0] == "quit":
	    break
        dispatch_msg(msg)
    else:
	do_main_loop()

#Fini app here (if you really need)

"""
from collections import deque
import select

__all__ = ["post_msg", "get_msg", "peek_sig", "dispatch_msg", "connect"]

actor_message_queue = deque()

def post_msg(msg):
	"""
	posts a msg to the runtime.
	"""
	assert type(msg) is tuple
	actor_message_queue.append(msg)


def get_msg():
	"""
	returns and removes the first message stored in the runtime
	or returns None if the runtime as no stored messages.
	"""
	try:
		return actor_message_queue.popleft()
	except:
		return None

def peek_sig():
	"""
	returns the signal of the first message stored in the runtime or
	returns None if the runtime as no stored messages.
	"""
	try:
		return actor_message_queue[0][0][2:]
	except:
		return None

def dispatch_msg(msg):
	"""
	returns the signal of the first message stored in the runtime or
	returns None if the runtime as no stored messages.
	"""
	fun = getattr(msg[1][0], msg[0]).__func__
	fun(*msg[1], **msg[2])

def dispatch_all_msg():
	"""dispatches all messages stored in the runtime"""
	while True:
		msg = get_msg()
		if not msg:
			break
		dispatch_msg(msg)


#def monitor_for_input(self, fd):
	#"""
	#monitors a socket for input
	#"""
	#try:
		#index_vec = self._rlist_index[fd]
	#except:
		#index = self._rlist.__len__()
		#self._rlist_index[fd] = [index, index, -1]
		#self._rlist.append(index)

	#if index_vec[0] == -1:
		#index = len(self._rlist)
		#index_vec[0] = index
		#self._rlist.append(index)

#def unmonitor_for_input(self, fd):
	#try:
		#index_vec = self._rlist_index[fd]
	#except KeyError:
		#return

	#index = index_vec[0]
	#if index == -1:
		#return
	#rlist_len = self._rlist.__len__()
	#if rlist_len != index:
		#self.pop()
		#return
	#last = self._rlist.pop()
	#self._rlist[index] = last

#def monitor_for_output(self, fd):
	#"""
	#monitors a socket for input: returns the number of monitored sockets
	#for input.
	#"""
	#try:
		#index_vec = self._wlist_index[fd]
	#except:
		#index = len(self._wlist)
		#self._wlist_index[fd] = [index, index, -1]
		#self._wlist.append(index)
		#return index + 1

	#if index_vec[0] == -1:
		#index = len(self._wlist)
		#index_vec[0] = index
		#self._wlist.append(index)
		#return index + 1

	#count = len(self._wlist)
	#return count

#def unmonitor_for_output(self, fd):
	#pass

#def monitor_for_except(self, fd):
	#pass
#def unmonitor_for_except(self, fd):
	#pass

#def monitor_for_connect(self, fd):
	#pass

def unmonitor_for_conect(self, fd):
	pass

#class IOActor(ActorTopState):

	#SOCK_CONNECTING = 1
	#SOCK_ACCEPTING  = 2
	#SOCK_READING    = 4
	#SOCK_WRITING    = 8

	#def __init__(self):
		## indexes are being monitores
		##(fd -> [rlist_index, xlist_index, wlist_index]
		##   -1 = not monitored
		##   used to avoid o(N) list maintainance

		#self._rlist = []
		#self._rlist_index = {}

		#self._xlist = []
		#self._xlist_index = {}

		#self._wlist = []
		#self._wlist_index = {}

		#self._active_sock = []

		##Datastrucure setup

		#self._fdindex = {} # maps fd -> State

		#self._acceptinglist_index = {} # a { [target1, target2, ...], [target1, target2, ...] }
		#self._acceptinglist       = [] # a [fd]

		#self._readinglist_index = {}
		#self._readinglist       = []

		#self._writeinglist_index = {}
		#self._writeinglist       = []

		#self._connectinglist_index = {}
		#self._connectinglist       = []
		#self._byte

#@initial
#class IOStagingState(IOActor):

	#def _enter():
		#pass
	#def _exit():
		#pass

#@initial
#class IORunningState(IOTopState):

	#def tcp_connect(io, sock, (host, port), target):
		#io.monitor_for_input(sock)
		#io.monitor_for_except(sock)
		#io.monitor_for_connect(sock, target)


	#def tcp_accept(io, sock, (host, port), target):
		#io.monitor_for_input(sock)
		#io.monitor_for_except(sock)
		#io.monitor_for_accept(sock, target)

	#def close(io, sock):
		#pass

	#def update(io):
		#read_list, write_list, xcept_list = select.select(io._rlist, io._wlist, io._xlist, 0)
		#for fd in read_list:
			#state = io._state[fd]
			#if state == IOActor.SOCK_ACCEPTING:

				#pass

#io = IOActor()

