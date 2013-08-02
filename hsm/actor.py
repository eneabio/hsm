# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

"""
actor - defines the actor top state 'ActorTopState'.

Actors, within the hsm library, are an implementation of hierarchical state.

Actors support the following features:
- *State Inheritance*
- *Hierarchical transitions*, with automatic _entry()/_exit()
- *Automatic protocol implementation*, to define an event just define an on_xxx
  method.

"""

import types
import traceback
import sys

import default_logger
from runtime import post_msg as runtime_post_msg


__all__ = ["TopState", "initial_state", "error_state", "MissingInitialStateError", "NotActorStateError", "ErrorState"]


def create_msg_sender(fun, signal, handler_name):
    def post_msg(*args, **kwargs):
        self = args[0]
        self._log.trace("(%s : %s) about to send message ('%s' args:%s kwargs:%s) ",
                        id(self), self.__class__.__name__, signal, str(args), str(kwargs), )
        runtime_post_msg((handler_name, args, kwargs))

    return post_msg


def create_except_receiver(fun, name):
    def receive_msg(*args, **kwargs):
        handler = fun
        self = args[0]
        self._log.trace("(%s : %s) about to receive message ('%s' args:%s kwargs:%s) ",
                        id(self), self.__class__.__name__, name, str(args), str(kwargs), )
        try:
            handler(*args, **kwargs)
        except Exception, ex:
            (type, value, tb) = sys.exc_info()
            self._log.error("Exception %s<%s>", type, value)
            for trace in traceback.format_exception(type, value, tb):
                self._log.error("---- traceback: %s", trace)

    return receive_msg


def create_msg_receiver(fun, name):
    def receive_msg(*args, **kwargs):
        handler = fun
        self = args[0]
        self._log.trace("(%s : %s) about to receive message ('%s' args:%s kwargs:%s) ", id(self),
                        self.__class__.__name__, name, str(args), str(kwargs), )
        try:
            handler(*args, **kwargs)
        except Exception, ex:
            curr = self.__class__
            error_state = None
            while True:
                if curr.__error_state__ is not None:
                    error_state = curr.__error_state__
                    break
                if curr.__bases__[0] == TopState:
                    error_state = ErrorState
                    break
                curr = curr.__bases__[0]
            self.transition(error_state)
            exc_type_value_traceback_triple = sys.exc_info()
            self.send_except(exc_type_value_traceback_triple)

    return receive_msg


class MissingInitialStateError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return "%s is missing the initial state. Use @initialState to mark the initial state" % (self._state.__name__)


class NotAStateError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return "@initialState can only by applied to a child class of HsmTopState. '%s' is not child " \
               "of hsm.actor.TopState" % self._state.__name__


class ReservedNameError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return """class '%s': %s the 'send_' prefix is reserved to send messages""" % self._state.__name__


def empty_function(self):
    pass


class StateMetaClass(type):
    def __new__(mcs, name, bases, dct):
        """


        :rtype : object
        :param name: 
        :param bases: 
        :param dct: 
        :return: 
        """
        return type.__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        """

        :param name:
        :param bases:
        :param dct:
        :raise:
        """
        super(StateMetaClass, cls).__init__(name, bases, dct)
        assert len(bases) > 0
        setattr(cls, "__initial_state__", None)
        setattr(cls, "__error_state__", None)
        if "_exit" not in dct:
            setattr(cls, "_exit", types.MethodType(empty_function, None, cls))
        if "_enter" not in dct:
            setattr(cls, "_enter", types.MethodType(empty_function, None, cls))
        for (k, v) in dct.items():
            if k.startswith("send_"):
                raise ReservedNameError(name, cls)
            if k.startswith("on_"):
                sig = k[3:]
                send_method_name = "send_" + sig
                if sig == "except":
                    receiver = create_except_receiver(v, sig)
                else:
                    receiver = create_msg_receiver(v, sig)
                sender = create_msg_sender(receiver, sig, k)
                setattr(cls, k, receiver)
                setattr(cls, send_method_name, sender)

    def __call__(cls, *args, **kwargs):

        instance = super(StateMetaClass, cls).__call__(*args, **kwargs)

        initial_state = getattr(instance.__class__, "__initial_state__", None)
        if instance.__class__ is None:
            raise MissingInitialStateError(cls)

        if not hasattr(instance, "_logger"):
            instance._log = default_logger

        instance._log.trace("(%s : <>): about to enter state (%s)", id(instance), instance.__class__.__name__)
        instance._enter()
        while initial_state is not None:
            instance._log.trace("(%s : %s): about to enter state (%s)", id(instance), instance.__class__.__name__,
                                initial_state.__name__)
            instance.__class__ = initial_state
            instance._enter()
            initial_state = initial_state.__initial_state__

        instance._initial_state = cls
        return instance


class TopState(object):
    __metaclass__ = StateMetaClass

    def __init__(self):
        object.__init__(self)

    def _enter(self):
        pass

    def _exit(self):
        pass

    def get_state_name(self):
        """Returns the current state name"""
        return self.__class__.__name__

    def get_state(self):
        """Returns the current state"""
        return self.__class__

    def on_fini(self):
        """Close the finite state machine by exiting up to the top use state"""
        while True:
            self._log.trace("(%s : %s): about to exit state", id(self), self.__class__.__name__, )
            self._exit()
            parent_state = self.__class__.__bases__[0]
            if parent_state != TopState:
                self.__class__ = parent_state
                continue
            break

    def transition(self, state):
        """Executes a transition from the current state to state"""
        outState = self.__class__
        inState = state
        left = outState
        right = inState
        if left == right:
            self._log.warn("transition to current state has no effect")
            return
        assert left != TopState
        assert right != TopState

        while left != TopState and right != left:
            left = left.__bases__[0]
            right = inState
            while right != TopState and right != left:
                right = right.__bases__[0]

        assert left == right

        #Execute Exits
        while self.__class__ != left:
            self._log.trace("(%s : %s): about to exit state", id(self), self.__class__.__name__, )
            self._exit()
            self.__class__ = self.__class__.__bases__[0]

        ### Fix Start ....
        # Left = Right --> Lowest Common Ancestor
        assert self.__class__ == left
        if inState != self.__class__:
            head = inState.__bases__[0]
            enterTrail = []
            if head != TopState:
                while head != left:
                    enterTrail.append(head)
                    head = head.__bases__[0]

            while enterTrail:
                head = enterTrail.pop()
                self._log.trace("(%s : %s): about to enter state (%s)", id(self), self.__class__.__name__,
                                head.__name__)
                self.__class__ = head
                self._enter()

            #Enter target state
            self._log.trace("(%s : %s): about to enter state (%s)", id(self), self.__class__.__name__, inState.__name__)
            self.__class__ = inState
            self._enter()

        #Drill down
        cls = self.__class__
        next_state = cls.__initial_state__
        while next_state is not None:
            self._log.trace("(%s : %s): about to enter state (%s)",
                            id(self),
                            self.__class__.__name__,
                            next_state.__name__)
            self.__class__ = next_state
            self._enter()
            next_state = next_state.__initial_state__


class ErrorState(TopState):
    def on_except(self, (exc_type, exc_value, exc_traceback )):
        tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for trace in tb:
            self._log.error(trace)


def error_state(state):
    """
    State anotation. Marks the annotated state as the error state of the
    the parent state.
    :param state: the state to be annotated
    """
    parent = state.__bases__[0]
    if not issubclass(parent, TopState):
        raise NotAStateError(state)
    if parent != TopState:
        parent.__error_state__ = state
    return state


def initial_state(state):
    """
    State anotation.
    :param state: the state to be annotated

    Marks the annotated state as the initial state of the
    the parent state.
    """
    parent = state.__bases__[0]
    if not issubclass(parent, TopState):
        raise NotAStateError(state)
    if parent != TopState:
        parent.__initial_state__ = state
    return state
