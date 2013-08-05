# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import unittest

from hsm import TopState, initial_state
from hsm.runtime_actor import runtime as runtime_actor

#Test state hierarchy:
# ObjTopState
#  - ObjErrorState
#  - ObjLeftState
#     - ObjLeftChildState *
#     - ObjLeftChildState2 *
#  - ObjRightState *
#     - ObjRightChildState *


class ObjTopState(TopState):
    def on_fatal_error(self):
        print "FatalError"
        self.transition(ObjErrorState)

    def on_print(self, my_data):
        print str(my_data)

    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


class ObjErrorState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )

    def on_except(self, ex):
        self._error = ex
        print str(ex)


@initial_state
class ObjLeftState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )

    def on_update(self):
        self.transition(ObjRightState)


@initial_state
class ObjLeftChildState(ObjLeftState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )

    def on_update(self):
        self.transition(ObjRightState)


class ObjLeftChildState2(ObjLeftState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


class ObjRightState(ObjTopState):
    def on_update(self):
        self._transition(ObjLeftState)

    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


@initial_state
class ObjRightChildState(ObjRightState):
    def on_update(self):
        self.transition(ObjLeftState)


class ActorTest(unittest.TestCase):
    def test_self_transition(self):
        obj = ObjTopState()
        obj.transition(ObjLeftChildState)
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjLeftChildState == st)

    def test_same_parent_transition(self):
        obj = ObjTopState()
        obj.transition(ObjLeftChildState2)
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjLeftChildState2 == st)

    def test_ancestor_transition(self):
        obj = ObjTopState()
        obj.transition(ObjTopState)
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjLeftChildState == st)

    def test_msg_send(self):
        obj = ObjTopState()
        obj.send_fatal_error()
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjErrorState == st)

    def test_fini(self):
        obj = ObjTopState()
        obj.send_fini()
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        print st

    def test_send_data(self):
        obj = ObjTopState()
        obj.send_print("sample")
        obj.send_fini()
        runtime_actor.dispatch_all_msg()

        #obj.send_fini()
        #while True:
        #msg = get_msg()
        #if not msg:
        #break
        #dispatch_msg(msg)
