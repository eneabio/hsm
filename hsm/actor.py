# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import default_logger
import types
from runtime import post_msg as runtime_post_msg

__all__ = [ "ActorTopState", "initial", "MissingInitialStateError", "NotActorStateError" ]

def create_msg_sender(fun, signal, handler_name):

	def post_msg(*args, **kwargs):
		self = args[0]
		self._log.trace("(%s : %s) about to send message ('%s' args:%s kwargs:%s) ", id(self), self.__class__.__name__, signal, str(args), str(kwargs), )
		runtime_post_msg( (handler_name, args, kwargs) )

	return post_msg

def create_msg_receiver(fun, name):

	def receive_msg(*args, **kwargs):
		self = args[0]
		self._log.trace("(%s : %s) about to receive message ('%s' args:%s kwargs:%s) ", id(self), self.__class__.__name__, name, str(args), str(kwargs), )
		return fun(*args, **kwargs)

	return receive_msg

class MissingInitialStateError(Exception):

	def __init__(self, state):
		self._state = state

	def __str__(self):
		return "%s is missing the initial state. Use @initialState to mark the initial state" % (self._state.__name__)

class NotHsmStateError(Exception):

	def __init__(self, state):
		self._state = state

	def __str__(self):
		return "@initialState can only by applied to a child class of HsmTopState. '%s' is not child of HsmTopState" % (self._state.__name__)

def empty_function(self): pass

class ActorMetaClass(type):

	def __new__(meta, name, bases, dct):
		return type.__new__(meta, name, bases, dct)

	def __init__(cls, name, bases, dct):
		type.__init__(cls, name, bases, dct)
		cls.__initial_state__ = None
		if not dct.has_key("_exit"):
			setattr(cls, "_exit", types.MethodType(empty_function, None, cls) )
		if not dct.has_key("_enter"):
			setattr(cls, "_enter", types.MethodType(empty_function, None, cls) )
		for (k,v) in dct.items():
			if k.startswith("send_"):
				raise ReservedNameError(name, k, "the 'send_' prefix is reserved to send messages")
			if k.startswith("on_"):
				sig = k[3:]
				send_method_name = "send_" + sig
				receiver = create_msg_receiver(v, sig)
				sender   = create_msg_sender(receiver, sig, k)
				setattr(cls, k , receiver)
				setattr(cls, send_method_name , sender)

	def __call__(cls, *args, **kwds):

		instance = type.__call__(cls, *args, **kwds)

		initial_state = instance.__class__.__initial_state__
		if initial_state == None:
			raise MissingInitialStateError(cls)

		if not hasattr(instance, "_logger"):
			instance._log = default_logger

		instance._log.trace( "(%s : <>): about to enter state (%s)", id(instance), instance.__class__.__name__ )
		instance._enter()
		while initial_state is not None:
			instance._log.trace( "(%s : %s): about to enter state (%s)", id(instance), instance.__class__.__name__, initial_state.__name__ )
			instance.__class__ = initial_state
			instance._enter()
			initial_state = initial_state.__initial_state__

		instance._initialState = cls
		return instance

class ActorTopState(object):

	__metaclass__ = ActorMetaClass

	def __init__(self):
		object.__init__(self)

	def _enter(self):
		pass

	def _exit(self):
		pass

	def get_state_name(self):
		'Returns the current state name'
		return self.__class__.__name__

	def get_state(self):
		'Returns the current state'
		return self.__class__

	def on_fini(self):
		'Close the finite state machine by exiting up to the top use state'
		while True:
			self._log.trace( "(%s : %s): about to exit state", id(self), self.__class__.__name__,)
			self._exit()
			parent_state = self.__class__.__bases__[0]
			if parent_state != ActorTopState:
				self.__class__ = parent_state
				continue
			break

	def transition(self, state):
		'Executes a transition from the current state to state'
		outState = self.__class__
		inState  = state
		left  = outState
		right = inState
		if left == right:
			self._log.warn("transition to current state has no effect")
			return
		assert left != ActorTopState
		assert right != ActorTopState

		while left != ActorTopState and right != left:
			left = left.__bases__[0]
			right = inState
			while right != ActorTopState and right != left:
				right = right.__bases__[0]

		assert left == right

		#Execute Exits
		while self.__class__ != left:
			self._log.trace( "(%s : %s): about to exit state", id(self), self.__class__.__name__,)
			self._exit()
			self.__class__ = self.__class__.__bases__[0]

		### Fix Start ....
		# Left = Right --> Lowest Common Ancestor
		assert self.__class__ == left
		if inState != self.__class__:
			head =  inState.__bases__[0]
			enterTrail = []
			if head != ActorTopState:
				while head != left:
					enterTrail.append(head)
					head = head.__bases__[0]

			while enterTrail:
				head = enterTrail.pop()
				self._log.trace( "(%s : %s): about to enter state (%s)", id(self), self.__class__.__name__,  head.__name__ )
				self.__class__ = head
				self._enter()

			#Enter target state
			self._log.trace( "(%s : %s): about to enter state (%s)", id(self), self.__class__.__name__, inState.__name__)
			self.__class__ = inState
			self._enter()

		#Drill down
		next_state = self.__class__.__initial_state__
		while next_state is not None:
			self._log.trace( "(%s : %s): about to enter state (%s)",
				id(self),
				self.__class__.__name__,
				next_state.__name__ )
			self.__class__ = next_state
			self._enter()
			next_state = next_state.__initial_state__


def initial(state):
	"""
	State anotation. Marks the annotated state as the initial state of the
	the parent state.
	"""
	parent = state.__bases__[0]
	if not issubclass(parent, ActorTopState):
		raise NotActorStateError(state)
	if parent != ActorTopState:
		parent.__initial_state__ = state
	return state
