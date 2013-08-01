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

__all__ = ["post_msg", "get_msg", "peek_sig", "dispatch_msg"]

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

def dispatch_msg(tuple):
	"""
	returns the signal of the first message stored in the runtime or
	returns None if the runtime as no stored messages.
	"""
	fun = getattr(msg[1][0], msg[0]).__func__
	fun(*msg[1], **msg[2])
	
