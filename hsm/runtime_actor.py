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

Note that runtime doesn't support multi-threading and never will, other techniques are
preferred.

*runtime.monitor_xxx(fd, target_actor)*:
  starts monitoring a fd for events and binds a target actor to a file
  descriptor. The *target_actor* will receive the events when data is available,
  data has been sent or an exception has occurred on the fd.

*runtime.unmonitor_xxx(fd)*:
  stops monitoring a fd for events

*runtime.update()*:
   - sends "data_arrived" to a monitoring actors if data si available for reading
   - sends "data_sent"    to a monitoring actors if data has been sent
   - sends "data_except"  to a monitoring actors an error has occurred on the bound fd

The runtime is designed for real-time applications (such as games or
interactive apps) and it's recommended to drive the entire application by using a 'main loop'
such as the following:

----

from hsm import runtime

#Init app here: setup initial actors

def mainloop():
    #... do your real-time stuff here
    return

runtime.run(mainloop)

#Fini app here (if you really need)

"""

import select
import sys

from actor import *
from runtime_queue import actor_message_queue


__all__ = ["runtime"]


class Runtime(TopState):
    READ_EVT = 0
    WRITE_EVT = 1
    EXCEPT_EVT = 2

    def __init__(self):
        TopState.__init__(self)

        self._quit = False
        self._read_list = []
        self._write_list = []
        self._except_list = []

        self._read_list_index = {}
        self._write_list_index = {}
        self._except_list_index = {}

        self._state_index = {}

    def quit(self):
        return self._quit

    def get_msg(self):
        """
        returns and removes the first message stored in the runtime
        or returns None if the runtime as no stored messages.
        """
        try:
            return actor_message_queue.popleft()
        except IndexError:
            return None

    def peek_sig(self):
        """
        returns the signal of the first message stored in the runtime or
        returns None if the runtime as no stored messages. It doesn't deque
        the message.
        """
        try:
            msg = actor_message_queue[0]
        except IndexError:
            return None
        return msg[0][3:]

    def dispatch_msg(self, msg):
        target = msg[1][0]
        try:
            fun = getattr(target, msg[0]).__func__
            fun(*msg[1], **msg[2])
        except Exception, ex:
            curr = target.__class__
            error_state = None
            while True:
                if curr.__error_state__ is not None:
                    error_state = curr.__error_state__
                    break
                if curr.__bases__[0] == TopState:
                    error_state = ErrorState
                    break
                curr = curr.__bases__[0]
            target.transition(error_state)
            exc_type_value_traceback_triple = sys.exc_info()
            target.send_except(exc_type_value_traceback_triple)

    def dispatch_all_msg(self):
        """
        Dispatches all messages stored in the runtime.
        """
        while True:
            msg = self.get_msg()
            if not msg:
                break
            self.dispatch_msg(msg)

    def set_quit_flag(self, quit_flag=True):
        self._quit = quit_flag

    def run(self, *main_loops):
        while not self._quit:
            msg = self.get_msg()
            if msg:
                self.dispatch_msg(msg)
                continue
            for mainloop in main_loops:
                mainloop()

    def is_msg_queue_empty(self):
        return len(actor_message_queue) == 0

    def on_clear_msg_queue(self):
        return actor_message_queue.clear()

    def clear_msg_queue(self):
        actor_message_queue.clear()

    def reset(self):
        self._read_list = []
        self._write_list = []
        self._except_list = []
        self._read_list_index = {}
        self._write_list_index = {}
        self._except_list_index = {}
        self._state_index = {}

    def _monitor_event(self, fd, target_actor, fd_list, list_index, evt):
        assert fd is not None
        #is it registered ?
        if self._state_index.has_key(fd):
            index_vec = self._state_index[fd]
            #is it already monitored ?
            if index_vec[evt] == -1:
                #not monitored
                index = fd_list.__len__()
                index_vec[evt] = index
                fd_list.append(fd)
                list_index[fd] = target_actor

            #already monitored
            #do nothing
            return

        #here ... Not registered

        #Create index vector
        index_vec = [-1, -1, -1]
        self._state_index[fd] = index_vec
        index_vec[evt] = fd_list.__len__()
        fd_list.append(fd)
        list_index[fd] = target_actor
        return

    def _unmonitor_event(self, fd, fd_list, list_index, evt):
        if not fd_list:
            # nothing is being monitored
            return
        if fd in list_index:
            index_vec = self._state_index[fd]
            index = index_vec[evt]
            if index == -1:
                #registered but not monitored
                #do nothing
                return
            list_len = fd_list.__len__()
            assert index < list_len
            if list_len - 1 == index:
                #it the last one! just pop it ...
                fd_list.pop()
                del list_index[fd]
                self._state_index[fd][evt] = -1
            else:
                # pop not the last one
                last = fd_list.pop()
                last_vec_index = self._state_index[last]
                deleted_vec_index = self._state_index[fd]
                deleted_pos = deleted_vec_index[evt]
                last_vec_index[evt] = deleted_pos
                fd_list[index] = last
                del list_index[fd]
                #check if we n eed to clear the state index
            if index_vec[0] == -1 and index_vec[1] == -1 and index_vec[2] == -1:
                del self._state_index[fd]

    def monitor(self, fd, target_actor):
        self._monitor_event(fd, target_actor, self._read_list, self._read_list_index, Runtime.READ_EVT)
        self._monitor_event(fd, target_actor, self._write_list, self._write_list_index, Runtime.WRITE_EVT)
        self._monitor_event(fd, target_actor, self._except_list, self._except_list_index, Runtime.EXCEPT_EVT)
        return

    def monitor_readable(self, fd, target_actor):
        self._monitor_event(fd, target_actor, self._read_list, self._read_list_index, Runtime.READ_EVT)

    def monitor_writable(self, fd, target_actor):
        self._monitor_event(fd, target_actor, self._write_list, self._write_list_index, Runtime.WRITE_EVT)

    def monitor_except(self, fd, target_actor):
        self._monitor_event(fd, target_actor, self._except_list, self._except_list_index, Runtime.EXCEPT_EVT)

    def unmonitor(self, fd):
        self._unmonitor_event(fd, self._read_list, self._read_list_index, Runtime.READ_EVT)
        self._unmonitor_event(fd, self._write_list, self._write_list_index, Runtime.WRITE_EVT)
        self._unmonitor_event(fd, self._except_list, self._except_list_index, Runtime.EXCEPT_EVT)

    def unmonitor_readable(self, fd):
        self._unmonitor_event(fd, self._read_list, self._read_list_index, Runtime.READ_EVT)

    def unmonitor_writable(self, fd):
        self._unmonitor_event(fd, self._write_list, self._write_list_index, Runtime.WRITE_EVT)

    def unmonitor_except(self, fd):
        self._unmonitor_event(fd, self._except_list, self._except_list_index, Runtime.EXCEPT_EVT)

    def update(self, timeout=None):
        if not self._read_list and not self._write_list and not self._except_list:
            return
        rl, wl, xl = select.select(self._read_list, self._write_list, self._except_list, timeout)
        for fd in rl:
            target = self._read_list_index[fd]
            target.send_data_readable(fd)
        for fd in wl:
            target = self._write_list_index[fd]
            target.send_data_writable(fd)
        for fd in xl:
            target = self._except_list_index[fd]
            target.send_data_except(fd)


@initial_state
class RuntimeReadyState(Runtime):

    def on_quit(self):
        self._quit = True


runtime = Runtime()







