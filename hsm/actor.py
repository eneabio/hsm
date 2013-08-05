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
from runtime_queue import actor_message_queue
import logging

__all__ = ["TopState", "initial_state", "error_state", "trace_state", "MissingInitialStateError", "NotAStateError", "ErrorState"]


def create_msg_sender(handler_name):
    def post_msg(*args, **kwargs):
        actor_message_queue.append((handler_name, args, kwargs))
    return post_msg


def create_except_receiver(fun, handler_name):
    def receive_msg(*args, **kwargs):
        msg_name = handler_name
        try:
            fun(*args, **kwargs)
        except Exception, ex:
            pass
    return receive_msg


def create_msg_receiver(fun, handler_name):
    def receive_msg(*args, **kwargs):
        msg_name = handler_name
        fun(*args, **kwargs)
    return receive_msg


def create_trace_enter(method, logger):
    assert logger is not None

    def tracing_execute(*args, **kwargs):
        logger.debug("%s: about to enter %s", id(args[0]), args[0].__class__.__name__)
        return method(*args, **kwargs)
    return tracing_execute


def create_trace_exit(method, logger):
    def tracing_execute(*args, **kwargs):
        logger.debug("%s: about to exit %s", id(args[0]), args[0].__class__.__name__)
        return method(*args, **kwargs)
    return tracing_execute


def create_trace_sender(method, logger):
    def tracing_execute(*args, **kwargs):
        name = method.func_closure[0].cell_contents
        logger.debug("%s: about to send msg ('%s' %s %s)", id(args[0]), name,args, kwargs)
        return method(*args, **kwargs)
    return tracing_execute


def create_trace_receiver(method, logger):
    def tracing_execute(*args, **kwargs):
        name = method.func_closure[1].cell_contents
        logger.debug("%s: about to receive msg %s %s %s", id(args[0]), name,args, kwargs)
        return method(*args, **kwargs)
    return tracing_execute


def create_trace_transition(logger):
    def tracing_execute(*args):
        return args[0].transition()(args[1])
    return tracing_execute


def add_tracing(cls, logger):
    if logger is not None:
        for (method_name, method) in cls.__dict__.items():
            if method_name.startswith("send_"):
                setattr(cls, method_name, create_trace_sender(method, logger))
                continue
            if method_name.startswith("on_"):
                setattr(cls, method_name, create_trace_receiver(method, logger))
                continue
            if method_name.startswith("_enter"):
                setattr(cls, method_name, create_trace_enter(method, logger))
                continue
            if method_name.startswith("_exit"):
                setattr(cls, method_name, create_trace_exit(method, logger))
                continue


class MissingInitialStateError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return "%s is missing the initial state. Use @initialState to mark the initial state" % (self._state.__name__)


class NotAStateError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return "@initial_state can only by applied to a child class of TopState. '%s' doesn't inherit from " \
               "hsm.actor.TopState" % self._state.__name__


class ReservedNameError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return """class '%s': %s the 'send_' prefix is reserved to send messages""" % self._state.__name__


class MultipleInheritanceNotSupportedError(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return """class '%s': multiple inheritance not supported""" % self._state.__name__


class MissingParentState(Exception):
    def __init__(self, state):
        self._state = state

    def __str__(self):
        return """class '%s': missing parent state""" % self._state.__name__


def empty_function(self):
    pass


def inheritMethod(cls, cls_dct, method_name):
    if method_name not in cls_dct:
        fun = getattr(TopState, method_name).__func__
        method = types.MethodType(fun, None, cls)
        cls_dct[method_name] = method

class state(type):
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
        super(state, cls).__init__(name, bases, dct)
        if len(bases) == 0:
            raise MissingParentState(cls)
        if len(bases) > 1:
            raise MultipleInheritanceNotSupportedError(cls)

        setattr(cls, "__initial_state__", None)
        setattr(cls, "__error_state__", None)

        #add standard methods to all states
        if cls.__name__ != 'TopState':
            inheritMethod(cls, dct, '_exit',)
            inheritMethod(cls, dct, '_enter',)
            inheritMethod(cls, dct, 'transition',)
            inheritMethod(cls, dct, 'on_fini',)

        for (k, v) in dct.items():
            if k.startswith("send_"):
                raise ReservedNameError(name, cls)
            if k.startswith("on_"):
                sig = k[3:]
                send_method_name = "send_" + sig
                if sig == "except":
                    receiver = create_except_receiver(v, k)
                else:
                    receiver = create_msg_receiver(v, k)
                sender = create_msg_sender(k)
                setattr(cls, k, receiver)
                setattr(cls, send_method_name, sender)

        #Setup tracing
        parent_state = bases[0]
        parent_state_name = parent_state.__name__
        if parent_state_name != "object":
            logger = getattr(parent_state, '__trace_logger__')
            setattr(cls, "__trace_logger__", logger)
            add_tracing(cls, logger)
        else:
            setattr(cls, "__trace_logger__", None)
            pass

    def __call__(cls, *args, **kwargs):
        instance = type.__call__(cls, *args, **kwargs)
        instance._enter()
        initial_state = cls.__initial_state__
        while initial_state is not None:
            instance.__class__ = initial_state
            instance._enter()
            initial_state = initial_state.__initial_state__
        instance._initial_state = cls
        return instance


class TopState(object):
    __metaclass__ = state

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

    def on_msg(self, sig, *args, **kwargs):
        """
        Dynamically send a msg to the runtime.
        """
        assert isinstance(sig, str)
        assert len(args) > 1
        self._actor_message_queue.append(("on_" + sig, (self,) + args, kwargs,))

    def on_fini(self):
        """Close the finite state machine by exiting up to the top use state"""
        while True:
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
                self.__class__ = head
                self._enter()

            #Enter target state
            self.__class__ = inState
            self._enter()

        #Drill down
        cls = self.__class__
        next_state = cls.__initial_state__
        while next_state is not None:
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


class trace_state:
    def __init__(self, logger=None):
        self._logger = logger

    def __call__(self, state):
        if self._logger is not None:
            setattr(state, '__trace_logger__', self._logger)
            add_tracing(state, self._logger)
            assert getattr(state, '__trace_logger__') is not None
        return state
